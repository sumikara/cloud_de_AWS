# Part 3 — Redshift ile Analitik Ürün (Public/Sanitized Sürüm)

## 0) Bu bölümün tek paragraf özeti
Bu bölümün amacı, S3 + Glue + Athena ile hazırlanan veri gölü katmanını Redshift’e taşıyıp iş değeri üreten bir raporlama katmanına dönüştürmektir: EC2 üzerinden SSH tüneli ile Redshift bağlantısı kurulur, en az 3 tablo Redshift’e `COPY` ile yüklenir, sık kullanılan join/sorgu senaryolarına göre dist/sort ve encoding analizi yapılır, optimize edilmiş tablo tasarımıyla stored procedure üzerinden rapor tablosu yüklenir ve performans karşılaştırması (`BEFORE`/`AFTER`) teknik olarak açıklanır. Bu public sürümde tüm gizli alanlar maskelenmiş, kurum/özel isimler temizlenmiş, tablo-kolon adları portfolyo için yeniden adlandırılmıştır.

---

## 1) Kuşbakışı hedef resmi (bu bölüm neden var?)

- **S3 (raw/curated):** kaynak verinin iniş alanı
- **Glue Catalog:** veri setlerinin metadata yönetimi
- **Athena:** Redshift öncesi hızlı keşif / kalite kontrol
- **EC2 + SSH tunnel:** private Redshift erişim köprüsü
- **Redshift:** modelleme, performans optimizasyonu, rapor üretimi
- **Stored Procedure:** tekrarlanabilir rapor yükleme
- **Spectrum (external schema/table):** cluster dışı S3 verisini sorgulama

Bu bölüm DWH tarafında “ham veriden KPI tablosuna” geçişi tamamlar.

---

## 2) Kısa mimari diyagram

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

Task 3 aktif akışı:

```text
Local PC
  └─ SSH Tunnel (EC2)
      └─ Redshift (private)
          ├─ COPY from S3
          ├─ Encoding / DIST / SORT analizi
          ├─ Stored Procedure ile report yükleme
          └─ Spectrum external schema ile S3 external query
```

---

## 3) Bu bölümde hangi dosya hangi amaçla kullanılmalı?

| Amaç | Dosya | Uzantı |
|---|---|---|
| Redshift runbook (anlatım + adım adım) | `codes/03-Redshift.md` | `.md` |
| Rapor pipeline SQL’i (schema/table/procedure) | `sql/redshift/03_report_pipeline.sql` | `.sql` |
| COPY ve test parametreleri (opsiyonel) | `params/redshift-copy.json` | `.json` |
| IaC altyapı (varsa Redshift/EC2 destek stack) | `templates/*.yaml` | `.yaml` |
| Otomasyon scripti (opsiyonel) | `scripts/redshift_runner.py` | `.py` |

Toplam hedef: dokümantasyon + SQL + opsiyonel otomasyon birlikte kullanılarak **gizli bilgi içermeyen, tekrar üretilebilir bir analitik portfolyo akışı** sağlanır.

---

## 4) Kürate edilmiş operasyon adımları

### 4.1 EC2 üstünde istemci hazırlığı (Redshift erişimi için)

```bash
sudo dnf update -y
sudo dnf install -y postgresql15.x86_64 postgresql15-server
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl enable --now postgresql
sudo systemctl status postgresql
```

### 4.2 Redshift bağlantı testi (sanitized)

```bash
psql -h <redshift-cluster-endpoint> -p 5439 -U <rs_user_xx> -d dev
```

### 4.3 Sonuç-cache kapatma (performans karşılaştırması öncesi)

```sql
SET enable_result_cache_for_session TO OFF;
```

---

## 5) Public SQL modeli (tablo/kolon adları değiştirilmiş)

> Orijinal kurum/özel isimli tablo-kolonlar yerine portfolyo amaçlı genel isimler kullanıldı.

- `analytics_practice.dim_client`
- `analytics_practice.dim_item`
- `analytics_practice.fct_order`
- `analytics_practice.rpt_monthly_sales`

Detay SQL için: `sql/redshift/03_report_pipeline.sql`

---

## 6) COPY ile yükleme (minimum 3 tablo)

```sql
COPY analytics_practice.dim_client
FROM 's3://<your-bucket>/warehouse/dim_client/'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
REGION 'eu-central-1'
FORMAT AS CSV
IGNOREHEADER 1
DELIMITER ','
TIMEFORMAT 'auto'
DATEFORMAT 'auto';

COPY analytics_practice.dim_item
FROM 's3://<your-bucket>/warehouse/dim_item/'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
REGION 'eu-central-1'
FORMAT AS CSV
IGNOREHEADER 1
DELIMITER ','
TIMEFORMAT 'auto'
DATEFORMAT 'auto';

COPY analytics_practice.fct_order
FROM 's3://<your-bucket>/warehouse/fct_order/'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
REGION 'eu-central-1'
FORMAT AS CSV
IGNOREHEADER 1
DELIMITER ','
TIMEFORMAT 'auto'
DATEFORMAT 'auto';
```

---

## 7) Encoding / dist / sort analizi (ödev maddeleriyle hizalı)

### 7.1 Default vs withoutcomp vs analyzedcomp

1. `fct_order_defaultcomp` (default encoding)
2. `fct_order_withoutcomp` (ENCODE RAW)
3. `fct_order_analyzedcomp` (ANALYZE COMPRESSION önerisiyle)

### 7.2 İnceleme sorguları

```sql
ANALYZE COMPRESSION analytics_practice.fct_order_withoutcomp;

SELECT "column", type, encoding
FROM pg_table_def
WHERE schemaname = 'analytics_practice'
  AND tablename = 'fct_order_analyzedcomp';

SELECT "schema", "table", diststyle, sortkey1, size
FROM svv_table_info
WHERE "schema" = 'analytics_practice'
  AND "table" IN ('fct_order_defaultcomp','fct_order_withoutcomp','fct_order_analyzedcomp')
ORDER BY "table";
```

> Beklenen çıktı: `withoutcomp` en büyük, `analyzedcomp` çoğu durumda daha küçük ve I/O açısından daha verimli olur.

---

## 8) BEFORE / AFTER performans metodolojisi

### BEFORE
- Default dist/sort ile join rapor sorgusunu çalıştır.
- İlk çalıştırmayı ısınma olarak sayma.
- Sonraki koşuların sürelerini kaydet.

### AFTER
- Join kolonlarına uygun `DISTKEY`, filtrelenen tarih kolonuna uygun `SORTKEY` uygula.
- Aynı sorguyu tekrar koştur ve plan/süre farkını kaydet.

### Neden ilk çalıştırma kıyas için doğru değil?
- Disk cache, block warming, metadata warming etkisi nedeniyle ilk koşu tipik steady-state davranışı temsil etmez.

---

## 9) Stored procedure ile rapor yükleme

Stored procedure mantığı:
- 3 tablo join (`fct_order` + `dim_client` + `dim_item`)
- aylık KPI üretimi
- hedef rapor tablosuna insert/refresh

Uygulama SQL’i: `sql/redshift/03_report_pipeline.sql`

---

## 10) COPY performans sorusu (özet yorum şablonu)

Aynı veriyi içeren iki farklı S3 prefix’i farklı hızda yüklenebilir; tipik nedenler:
- Dosya sayısı / parça boyutu dengesi
- S3 object dağılımı ve paralellik
- Dosya sıkıştırma / format farklılığı
- COPY anındaki cluster yükü

---

## 11) Spectrum (external table) kısa pratik

```sql
CREATE EXTERNAL SCHEMA IF NOT EXISTS analytics_practice_ext
FROM DATA CATALOG
DATABASE 'glue_db_xx'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-spectrum-role>';
```

Partition tasarım önerisi:
- S3 klasör yapısını `event_month=YYYY-MM-01` şeklinde kur.
- External table’ı `PARTITION BY (event_month date)` ile yönet.
- Aylık satır sayısı karşılaştırma sorgusu ile farkın `0` olduğuna dair test script’i ekle.

---

## 12) Elenen / dönüştürülen kısımlar (ve neden)

- **Kurum adı, özel endpoint, kullanıcı adı, ARN, bucket isimleri**
  - **Neden:** Public repo’da gizlilik ve güvenlik.
- **Confidential ibareli ham metnin olduğu gibi paylaşımı**
  - **Neden:** Yalnızca pratik teknik bilgi yayınlanmalı.
- **Öğrenciye özel şema ve tablo adları**
  - **Neden:** Yeniden kullanılabilir ve kişisiz bir portfolyo standardı.
- **Aşırı uzun teorik tekrarlar**
  - **Neden:** Çalıştırılabilir adım ve net kontrol listesi odaklı kalmak.

---

## 13) Bu bölüm sonunda kazanım

Bu adımı tamamlayan kişi şunları gösterebilir:
- Redshift’e güvenli bağlantı ve veri yükleme
- MPP temelli performans optimizasyonu (encoding/dist/sort)
- Stored procedure ile rapor üretim otomasyonu
- Spectrum ile S3 external data sorgulama yaklaşımı

Böylece portfolyo, data lake katmanından analitik sunum katmanına ilerleyen gerçekçi bir “end-to-end” çizgiye ulaşır.
