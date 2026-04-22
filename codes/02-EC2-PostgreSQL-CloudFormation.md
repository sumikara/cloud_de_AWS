# Part 2 — EC2 üstünde PostgreSQL, SSH Tüneli, S3 Kopyalama, Apache, Alarm ve CloudFormation

## 0) Bu bölümün tek paragraf özeti
Bu bölümün amacı, bulut üzerinde düşük maliyetli bir veri tabanı sunucusunu uçtan uca kurup operasyonel olarak doğrulamaktır: `eu-central-1` bölgesinde küçük bir EC2 (t2.micro) açılır, IMDSv2 zorunlu olacak şekilde güvenli metadata erişimi ayarlanır, 8 GiB root + 10 GiB ek EBS ile depolama ayrıştırılır, PostgreSQL 15 kurularak SQL istemcisi (SSH tunnel ile) bağlantısı doğrulanır, S3’ten dosya EC2’ye kopyalanır, AMI/snapshot ile sunucu kopyalama senaryosu test edilir, Apache ile basit web yayını yapılır, CloudWatch + SNS ile temel izleme/uyarı kurulumu tamamlanır ve aynı sunucu CloudFormation ile koddan tekrar üretilebilir hale getirilir.

---

## 1) Kuşbakışı hedef resmi (neden hangi servis var?)

- **EC2:** Veritabanını kendi yönettiğin VM üzerinde çalıştırma pratiği
- **EBS:** Kalıcı disk yönetimi (OS diski + veri/uygulama için ek disk)
- **IAM Instance Profile:** EC2’nin S3’e anahtarsız erişimi
- **S3:** EC2’ye örnek dosya indirme / veri staging
- **PostgreSQL:** DB servis kurulumu, tablo-fonksiyon-view üretimi
- **DBeaver + SSH Tunnel:** Güvenli uzaktan yönetim
- **AMI + Snapshot:** Yedekleme/kopya ortam oluşturma
- **Apache:** Basit servis yayına alma pratiği
- **CloudWatch + SNS:** Kaynak alarmı ve bildirim
- **CloudFormation:** Aynı altyapıyı tekrar üretilebilir (IaC) hale getirme

---

## 2) Kısa mimari diyagram

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

Bu bölümde aktif kullanılan alt akış:

```text
Local PC
  └─ SSH + DBeaver Tunnel
      └─ EC2 (Amazon Linux 2023, t2.micro)
          ├─ PostgreSQL 15 (systemd service)
          ├─ EBS (8 GiB root + 10 GiB data)
          ├─ S3 (instance profile ile dosya çekme)
          ├─ Apache (/var/www/html)
          └─ CloudWatch Alarm → SNS Email

IaC: CloudFormation ile aynı EC2 topolojisinin yeniden kurulumu
```

---

## 3) Bu bölümde hangi dosya türü ne için kullanılmalı?

| Amaç | Önerilen dosya | Uzantı |
|---|---|---|
| Bölüm anlatımı ve runbook | `codes/02-EC2-PostgreSQL-CloudFormation.md` | `.md` |
| EC2 altyapısının kodu | `templates/ec2-sumi-stack.yaml` | `.yaml` |
| PostgreSQL DDL/DML doğrulama scriptleri | `sql/postgres/02_ec2_postgres_setup.sql` | `.sql` |
| SSH/S3 otomasyon yardımcı scriptleri | `scripts/ec2_bootstrap.py` veya `scripts/pull_from_s3.sh` | `.py` / `.sh` |
| CLI parametre setleri (opsiyonel) | `params/ec2-launch.json` | `.json` |

Toplam hedef: Dokümantasyon (`.md`) + altyapı kodu (`.yaml`) + SQL doğrulama (`.sql`) + küçük otomasyon (`.py/.sh`) birlikte çalışarak **tekrar üretilebilir bir portfolyo senaryosu** oluşturur.

---

## 4) Kürate edilmiş komut akışı (ham log yerine çalıştırılabilir bloklar)

> Tüm hassas alanlar maskele: `<xx>`, `<account-id>`, `<public-ip>`, `<key.pem>`.

### 4.1 EC2’ye bağlan

```bash
ssh -i "<local-path>/<key>.pem" ec2-user@<public-ip>
```

### 4.2 Sunucuyu güncelle

```bash
sudo dnf update -y
```

### 4.3 PostgreSQL 15 kur ve servisle yönet

```bash
sudo dnf install -y postgresql15 postgresql15-server
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl status postgresql
```

### 4.4 PostgreSQL güvenli başlangıç (örnek)

```bash
sudo -iu postgres psql
```

```sql
-- Güçlü parola kullan, düz metin paylaşma
ALTER USER postgres WITH PASSWORD '<strong-password-xx>';
```

### 4.5 S3’ten EC2’ye dosya kopyala (instance profile ile)

```bash
aws s3 ls s3://<your-bucket>/
aws s3 cp s3://<your-bucket>/test.txt /home/ec2-user/
ls -lah /home/ec2-user/
```

### 4.6 Apache kur ve test sayfası yayınla

```bash
sudo dnf install -y httpd
sudo systemctl enable --now httpd
echo '<h1>cloud data practice - ec2 web test</h1>' | sudo tee /var/www/html/index.html
curl -I http://localhost
```

---

## 5) SQL doğrulama paketi (minimum ama yeterli)

```sql
SELECT version();

CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

CREATE OR REPLACE FUNCTION insert_data(p_name VARCHAR, p_age INT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO test_table(name, age) VALUES (p_name, p_age);
END;
$$ LANGUAGE plpgsql;

SELECT insert_data('demo_user', 25);

CREATE OR REPLACE VIEW v_adults AS
SELECT id, name, age
FROM test_table
WHERE age >= 18;

SELECT * FROM test_table;
SELECT * FROM v_adults;
```

---

## 6) DBeaver SSH Tunnel bağlantı modeli (güvenli ve sade)

- **DB Host:** `127.0.0.1`
- **DB Port:** `5432`
- **Database:** `postgres`
- **DB User:** `postgres`
- **DB Password:** `<xx>`
- **SSH Host:** `<ec2-public-dns>`
- **SSH Port:** `22`
- **SSH User:** `ec2-user`
- **Auth:** Private key (`<key>.pem`)

> Not: Security Group tarafında sadece gerekli IP/CIDR’lere izin ver.

---

## 7) Snapshot + AMI + kopya instance kontrol listesi

1. Ek EBS volume için snapshot al.
2. EC2’den AMI üret (tanınabilir isim).
3. AMI’dan yeni instance aç.
4. **IMDSv2 (`HttpTokens=required`)** ayarını yeni instance’da da zorunlu tut.
5. Eski instance’taki dosyanın yeni instance’ta varlığını doğrula.

---

## 8) CloudWatch Alarm + SNS önerilen minimal kurulum

- SNS Topic: `cloud-practice-ec2-alerts`
- Subscription: `Email` (doğrulanmış kişisel adres)
- Alarm Metric: `EC2 > CPUUtilization`
- Threshold örneği: `>= 70` (5 dk)
- Action: alarm durumunda SNS topic’e publish

---

## 9) CloudFormation notları (rollback hatasını azalt)

`templates/ec2-sumi-stack.yaml` dosyasını kullanırken:

- `KeyName`, `SubnetId`, `SecurityGroupId`, `InstanceProfileName` parametrelerini doğru VPC/region’dan ver.
- SG’nin `22` ve gerekiyorsa `80` port izinlerini kontrol et.
- Instance profile adı ile role adını karıştırma (profile adı verilmelidir).
- Kaynak adlarında çakışma varsa stack rollback olur; isimleri benzersizleştir.

---

## 10) Ham notlardan elenen / düzeltilen parçalar (ve neden)

- **Tekrarlanan SSO + S3 komutları**
  - **Neden elendi:** Bu bölümün ana odağı EC2/DB operasyonları; tekrarlar okunabilirliği düşürüyor.
- **Kişisel email, hesap ARN, public IP, key path gibi açık bilgiler**
  - **Neden elendi:** Güvenlik ve gizlilik.
- **Zayıf veya açık parola örnekleri (`1234`, `12345`)**
  - **Neden elendi:** Güvenlik anti-pattern.
- **Hatalı/eksik komutlar (`students-rol`, kapanmayan tırnak, eksik `dnf install -y`)**
  - **Neden elendi:** Çalıştırılabilir değil, yeni başlayan için yanıltıcı.
- **Uzun ham terminal çıktıları**
  - **Neden elendi:** Gürültü üretir; yerine kısa doğrulama komutları bırakıldı.

---

## 11) Bu bölüm tamamlandığında kazanım

Bu bölüm sonunda, bir cloud data engineer adayı olarak şunları göstermiş olursun:
- VM tabanlı DB kurulumu ve işletimi
- S3↔EC2 veri akışı
- SSH tünel ile güvenli istemci erişimi
- Basit servis yayını (Apache)
- Alarm/notification temel gözlemlenebilirlik
- IaC ile aynı altyapıyı tekrar ayağa kaldırma

Bir sonraki adımda bu EC2 üstü veritabanı çıktısını Redshift/RDS/DynamoDB ve S3 tabanlı analitik akışına bağlayarak portfolyoyu uçtan uca tamamlayabilirsin.
