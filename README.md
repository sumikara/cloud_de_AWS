# AWS Data Engineering Practice Repository

This repository is a portfolio-style, end-to-end AWS data engineering practice project.
It walks through a realistic learning sequence:

**Access → Storage → Catalog → Query → Compute → Warehouse → Managed DBs → NoSQL**.

Main region used in examples: `eu-central-1`.

---

## 1) Project Overview

The project is organized as four hands-on modules:

1. **IAM / SSO / S3 / Glue / Athena**
2. **EC2 / PostgreSQL / Apache / CloudWatch / CloudFormation**
3. **Redshift analytics + optimization + Spectrum concepts**
4. **RDS MySQL / Aurora / DynamoDB**

The goal is to practice both SQL and NoSQL patterns with secure connectivity, reproducible scripts, and public-safe documentation.

---

## 2) Repository Structure (actual)

```text
cloud_de_AWS/
├── README.md
├── docs/
│   ├── 01-parts-overview.md
│   ├── 02-services-summary.md
│   ├── 03-ss-guide.md
│   └── 04-pipeline-review.md
├── codes/
│   ├── 01-IAM-S3-Glue-Athena.md
│   ├── 02-EC2-PostgreSQL-CloudFormation.md
│   ├── 03-Redshift.md
│   └── 04-RDS-Aurora-DynamoDB.md
├── sql/
│   └── redshift/
│       └── 03_report_pipeline.sql
├── templates/
│   └── ec2-sumi-stack.yaml
├── customers_batch_sumi.json
└── get_items_sumi.json
```

---

## 3) How to Navigate the Learning Path

### Step 1 — Access and Data Lake Basics
Start with:
- `codes/01-IAM-S3-Glue-Athena.md`

You will practice:
- AWS CLI SSO profiles
- S3 bucket layout
- Glue crawler + Data Catalog
- Athena validation queries

### Step 2 — Compute and Self-managed Database on EC2
Continue with:
- `codes/02-EC2-PostgreSQL-CloudFormation.md`

You will practice:
- EC2 provisioning with IMDSv2
- PostgreSQL installation and SQL objects
- SSH-based access
- EBS snapshot + AMI flow
- CloudWatch/SNS + CloudFormation fundamentals

### Step 3 — Warehouse Layer
Continue with:
- `codes/03-Redshift.md`
- `sql/redshift/03_report_pipeline.sql`

You will practice:
- Secure Redshift access via jump host
- S3-to-Redshift COPY ingestion
- Encoding / DISTKEY / SORTKEY reasoning
- Stored procedure report loading
- Spectrum external schema concepts

### Step 4 — Managed SQL + NoSQL
Finish with:
- `codes/04-RDS-Aurora-DynamoDB.md`
- `customers_batch_sumi.json`
- `get_items_sumi.json`

You will practice:
- Restartable RDS MySQL init script
- Aurora private connectivity via SSH tunnel
- DynamoDB CLI-driven create/write/read/delete operations

---

## 4) Architecture Snapshot

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

---

## 5) Security and Publishing Rules

Never commit:
- private keys (`.pem`, `.ppk`, `.ssh/*`)
- AWS credential files
- real passwords, tokens, session secrets
- full private endpoints tied to live environments

Use placeholders instead:
- `<account-id>`
- `<db-user>`
- `<strong-password-xx>`
- `<cluster-endpoint>`

---

## 6) What Was Improved in This Revision

- Added `docs/04-pipeline-review.md` with a full repository audit against a typical data engineering pipeline.
- Cleaned README structure to reflect **actual repository paths**.
- Removed outdated references and made the overview consistent with current files.
- Made onboarding clearer with a strict “what to run first” sequence.

---

## 7) Next Recommended Improvements

- Add data-quality test SQL templates (null checks, duplicate-key checks, row-count reconciliation).
- Add Redshift troubleshooting snippets (`stl_load_errors`, query diagnostics).
- Add DynamoDB retry/backoff example for `UnprocessedItems`.
- Add lightweight CI checks for markdown/json/sql formatting.

These will improve operational maturity and make the portfolio even stronger.
