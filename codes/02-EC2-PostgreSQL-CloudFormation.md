# Part 2 — PostgreSQL on EC2, SSH Tunnel, S3 Copy, Apache, Alarms, and CloudFormation

## 0) One-paragraph summary of this section
The goal of this section is to build and operationally validate a low-cost cloud database server end to end: launch a small EC2 instance (t2.micro) in `eu-central-1`, enforce secure metadata access with IMDSv2, separate storage using 8 GiB root + 10 GiB additional EBS, install PostgreSQL 15 and verify SQL-client connectivity (via SSH tunnel), copy files from S3 to EC2, test AMI/snapshot-based server cloning, publish a simple web page with Apache, configure basic monitoring/alerts using CloudWatch + SNS, and make the same server reproducible with CloudFormation.

---

## 1) Bird’s-eye goal map (why each service exists)

- **EC2:** Practice running a database on a self-managed VM
- **EBS:** Persistent disk management (OS disk + additional disk for data/app)
- **IAM Instance Profile:** Keyless S3 access from EC2
- **S3:** Sample file download / staging into EC2
- **PostgreSQL:** DB service setup and table-function-view creation
- **DBeaver + SSH Tunnel:** Secure remote management
- **AMI + Snapshot:** Backup and clone environment creation
- **Apache:** Practice publishing a basic service
- **CloudWatch + SNS:** Resource alarms and notifications
- **CloudFormation:** Reproducible infrastructure (IaC)

---

## 2) Short architecture diagram

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

Active sub-flow used in this section:

```text
Local PC
  └─ SSH + DBeaver Tunnel
      └─ EC2 (Amazon Linux 2023, t2.micro)
          ├─ PostgreSQL 15 (systemd service)
          ├─ EBS (8 GiB root + 10 GiB data)
          ├─ S3 (file pull via instance profile)
          ├─ Apache (/var/www/html)
          └─ CloudWatch Alarm → SNS Email

IaC: Re-create the same EC2 topology using CloudFormation
```

---

## 3) Which file type should be used for what in this section?

| Purpose | Suggested file | Extension |
|---|---|---|
| Section narrative and runbook | `codes/02-EC2-PostgreSQL-CloudFormation.md` | `.md` |
| EC2 infrastructure code | `templates/ec2-sumi-stack.yaml` | `.yaml` |
| PostgreSQL DDL/DML validation scripts | `sql/postgres/02_ec2_postgres_setup.sql` | `.sql` |
| SSH/S3 automation helper scripts | `scripts/ec2_bootstrap.py` or `scripts/pull_from_s3.sh` | `.py` / `.sh` |
| CLI parameter sets (optional) | `params/ec2-launch.json` | `.json` |

Overall target: documentation (`.md`) + infra code (`.yaml`) + SQL validation (`.sql`) + small automation (`.py/.sh`) working together to form a **reproducible portfolio scenario**.

---

## 4) Curated command flow (executable blocks instead of raw logs)

> Mask all sensitive values: `<xx>`, `<account-id>`, `<public-ip>`, `<key.pem>`.

### 4.1 Connect to EC2

```bash
ssh -i "<local-path>/<key>.pem" ec2-user@<public-ip>
```

### 4.2 Update server packages

```bash
sudo dnf update -y
```

### 4.3 Install PostgreSQL 15 and manage service

```bash
sudo dnf install -y postgresql15 postgresql15-server
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl status postgresql
```

### 4.4 Secure PostgreSQL start (example)

```bash
sudo -iu postgres psql
```

```sql
-- Use a strong password, never share plaintext credentials
ALTER USER postgres WITH PASSWORD '<strong-password-xx>';
```

### 4.5 Copy file from S3 to EC2 (using instance profile)

```bash
aws s3 ls s3://<your-bucket>/
aws s3 cp s3://<your-bucket>/test.txt /home/ec2-user/
ls -lah /home/ec2-user/
```

### 4.6 Install Apache and publish a test page

```bash
sudo dnf install -y httpd
sudo systemctl enable --now httpd
echo '<h1>cloud data practice - ec2 web test</h1>' | sudo tee /var/www/html/index.html
curl -I http://localhost
```

---

## 5) SQL validation package (minimal but sufficient)

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

## 6) DBeaver SSH Tunnel connection model (secure and simple)

- **DB Host:** `127.0.0.1`
- **DB Port:** `5432`
- **Database:** `postgres`
- **DB User:** `postgres`
- **DB Password:** `<xx>`
- **SSH Host:** `<ec2-public-dns>`
- **SSH Port:** `22`
- **SSH User:** `ec2-user`
- **Auth:** Private key (`<key>.pem`)

> Note: Allow only required IP/CIDR ranges in Security Group rules.

---

## 7) Snapshot + AMI + cloned instance checklist

1. Create snapshot for the additional EBS volume.
2. Create AMI from the EC2 instance (use a recognizable name).
3. Launch a new instance from that AMI.
4. Enforce **IMDSv2 (`HttpTokens=required`)** on the cloned instance as well.
5. Verify that files from the original instance are available in the clone.

---

## 8) Recommended minimal CloudWatch Alarm + SNS setup

- SNS Topic: `cloud-practice-ec2-alerts`
- Subscription: `Email` (verified personal address)
- Alarm Metric: `EC2 > CPUUtilization`
- Example threshold: `>= 70` (5 minutes)
- Action: publish to SNS topic when alarm state is reached

---

## 9) CloudFormation notes (reduce rollback risk)

When using `templates/ec2-sumi-stack.yaml`:

- Provide `KeyName`, `SubnetId`, `SecurityGroupId`, and `InstanceProfileName` from the correct VPC/region.
- Verify SG allows port `22` (and `80` if required).
- Do not confuse instance profile name with role name (profile name must be provided).
- Resource name collisions can cause stack rollback; use unique names.

---

## 10) Removed/fixed parts from raw notes (and why)

- **Repeated SSO + S3 commands**
  - **Why removed:** This section focuses on EC2/DB operations; repeats reduce readability.
- **Exposed personal values (email, account ARN, public IP, key path)**
  - **Why removed:** Security and privacy.
- **Weak/plaintext password examples (`1234`, `12345`)**
  - **Why removed:** Security anti-pattern.
- **Broken/incomplete commands (`students-rol`, unclosed quote, missing `dnf install -y`)**
  - **Why removed:** Not executable and misleading.
- **Very long raw terminal outputs**
  - **Why removed:** Noise; replaced with concise verification commands.

---

## 11) What you demonstrate after completing this section

At the end of this section, a cloud data engineer candidate demonstrates:
- VM-based DB setup and operations
- S3↔EC2 data movement
- Secure client access via SSH tunnel
- Basic service publishing (Apache)
- Basic observability (alarms/notifications)
- Reproducible infra with IaC

In the next step, this EC2-hosted database output can be connected to Redshift/RDS/DynamoDB and S3-based analytical flows to complete the end-to-end portfolio.
