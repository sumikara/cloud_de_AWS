# Part 1 — AWS Access, S3 Data Lake Ingestion, Glue Catalog, Athena Query

## 0) Quick intent summary (what this section aims to build)
This first section establishes a **minimum but production-minded cloud data foundation**: you authenticate to AWS with SSO, switch into a task role with the correct permissions, create and validate an S3 bucket, upload local DWH-style source files into a clean folder hierarchy, register metadata with Glue (Crawler + Data Catalog), and run analytical SQL in Athena on top of those files. In short: **secure access + governed storage + queryable metadata + serverless SQL**.

At the end of this section you should have a working local-to-cloud ingestion path and an analytics-ready lake layout.

---

## 1) Big picture (section goals by component)

### 1.1 Authentication & authorization
**Goal:** Connect from local machine to AWS in a secure, repeatable, role-based way.

- Login via SSO (browser)
- Create a base CLI profile (`user-role-xxxxxxxxxxxx`)
- Assume an execution profile (`students-role`) for data tasks

### 1.2 Object storage (S3)
**Goal:** Create personal bucket and store files with a predictable prefix structure.

- Bucket naming with personal prefix
- Upload a smoke-test file (`test.txt`)
- Upload analytical table files under hierarchical prefixes

### 1.3 Metadata & discovery (Glue)
**Goal:** Make S3 files discoverable as tables.

- Crawler points to `s3://<bucket>/<database>/<schema>/...`
- Tables materialize in Glue Data Catalog

### 1.4 Query layer (Athena)
**Goal:** Validate data availability and run SQL checks.

- `SELECT` queries for sanity and profiling
- Inspect table properties and row volumes

---

## 2) Architecture (short diagram)

```text
[Local PC]
   |
   v
[AWS SSO + AWS CLI Profiles]
   |
   +------------------------------+
   |                              |
   v                              v
[S3 Data Lake]                [EC2 (future sections)]
   |
   v
[Glue Crawler + Data Catalog]
   |
   v
[Athena SQL]

(Portfolio roadmap targets include: Redshift / RDS / DynamoDB integrations.)
```

Requested full-chain view:

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

---

## 3) Recommended folder & file strategy (portfolio-ready, simple)

### 3.1 Repository artifacts by purpose

- **`.md`** → narrative, runbooks, decision logs, and curated command steps
- **`.yaml`** → infrastructure templates (CloudFormation)
- **`.sql`** → Athena/Redshift/RDS query scripts
- **`.py`** → utility scripts (ETL helpers, validations, file movers)

### 3.2 For this section specifically

| Purpose | Suggested file | Extension |
|---|---|---|
| Access setup runbook | `codes/01-IAM-S3-Glue-Athena.md` | `.md` |
| CLI profile example (sanitized) | `snippets/aws-config-example.txt` (optional) | `.txt` |
| Athena sanity queries | `sql/athena/01_sanity_checks.sql` (optional) | `.sql` |
| Data upload helper | `scripts/upload_to_s3.py` (optional) | `.py` |

---

## 4) Curated executable commands (cleaned from raw logs)

> Notes:
> - Replace placeholders before running.
> - Never store real usernames/emails/tokens in repository files.

### 4.1 Configure SSO profile

```bash
aws configure sso
# SSO session name: user-role
# SSO start URL: https://xx.awsapps.com/start#
# SSO region: us-east-1
# Default region: eu-central-1
# Profile name: user-role-xxxxxxxxxxxx
```

### 4.2 Verify base identity

```bash
aws sts get-caller-identity --profile user-role-xxxxxxxxxxxx
```

### 4.3 Add task role profile (students-role) in `~/.aws/config`

```ini
[profile user-role-xxxxxxxxxxxx]
sso_session = user-role
sso_account_id = xxxxxxxxxxxx
sso_role_name = User
region = eu-central-1

[sso-session user-role]
sso_start_url = https://xx.awsapps.com/start#
sso_region = us-east-1
sso_registration_scopes = sso:account:access

[profile students-role]
role_arn = arn:aws:iam::xxxxxxxxxxxx:role/students-role
source_profile = user-role-xxxxxxxxxxxx
region = eu-central-1
```

### 4.4 Verify assumed role

```bash
aws sts get-caller-identity --profile students-role
```

### 4.5 Create bucket

```bash
aws s3 mb s3://<your-unique-bucket-name> --region eu-central-1 --profile students-role
```

### 4.6 Upload and validate a smoke-test file

```bash
aws s3 cp "<local-path>/test.txt" s3://<your-unique-bucket-name>/ --profile students-role
aws s3 ls s3://<your-unique-bucket-name>/ --profile students-role
```

### 4.7 Upload DWH-style table file to structured prefix

```bash
aws s3 cp "<local-path>/di_dwh_database/bl_dm/dim_customers/dim_customers.csv" \
  s3://<your-unique-bucket-name>/di_dwh_database/bl_dm/dim_customers/ \
  --profile students-role
```

---

## 5) Glue + Athena execution checklist

1. Create (or edit) Glue Crawler with source path:
   - `s3://<your-unique-bucket-name>/di_dwh_database/bl_dm/`
2. Ensure crawler naming is consistent (hyphen/underscore convention).
3. Run crawler and verify Data Catalog tables are created.
4. In Athena, point query result location to a dedicated S3 prefix.
5. Run validation SQL:

```sql
SELECT *
FROM bl_dm.dim_customers
LIMIT 100;
```

```sql
SELECT country, COUNT(*) AS customer_count
FROM bl_dm.dim_customers
GROUP BY country
ORDER BY customer_count DESC
LIMIT 50;
```

---

## 6) Noise removed from raw notes (and why)

The following items were intentionally excluded from executable guidance:

- **Repeated command blocks** (`aws configure sso`, `aws sts get-caller-identity`, upload examples repeated):
  - **Reason:** duplicates create confusion and version drift.
- **Personal identifiers (name/email/account-linked ARN fragments):**
  - **Reason:** privacy and security hygiene for portfolio publication.
- **Region-mismatched console link (`eu-north-1`) while runtime region is `eu-central-1`:**
  - **Reason:** can lead to “resource not found” misunderstandings.
- **Typo in profile (`students-rol`):**
  - **Reason:** command fails; standardized to `students-role`.
- **Long raw authorization URLs and full terminal transcripts:**
  - **Reason:** too verbose, sensitive, and not reusable as a runbook.

---

## 7) Practical best practices (simple, not overengineered)

- Keep one **active region per learning module** (here: `eu-central-1`).
- Use deterministic S3 layout: `s3://<bucket>/<domain_db>/<schema>/<table>/...`
- Add lightweight tagging: `project=cloud-data-practice`, `owner=<alias>`, `env=dev`
- Keep SQL checks in versioned `.sql` files, not only Athena history.
- Store only sanitized examples in docs and screenshots.

---

## 8) What this section delivers to the full project roadmap

This part provides the foundation for later modules:
- EC2-based tooling and scripts can read/write the same S3 data.
- Redshift Spectrum / COPY workflows can consume cataloged datasets.
- RDS/DynamoDB extracts can be landed into S3 and queried by Athena.

So this section is the **access + storage + metadata + SQL validation baseline** for the full end-to-end portfolio.
