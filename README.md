# AWS Data Engineering Practice Repository

This repository is a portfolio-style, end-to-end AWS data engineering practice project.
It walks through a realistic learning sequence:

**Access → Storage → Catalog → Query → Compute → Warehouse → Managed DBs → NoSQL → Orchestration**.

Main region used in examples: `eu-central-1`.

---

## 1) Project Overview

The project is organized as core modules plus one optional orchestration extension:

1. **IAM / SSO / S3 / Glue / Athena**
2. **EC2 / PostgreSQL / Apache / CloudWatch / CloudFormation**
3. **Redshift analytics + optimization + Spectrum concepts**
4. **RDS MySQL / Aurora / DynamoDB**
5. **(Optional) Lambda + Step Functions orchestration**

The goal is to practice SQL + NoSQL patterns, secure connectivity, and workflow-oriented data platform design with public-safe documentation.

---

## 2) Repository Structure (actual)

```text
cloud_de_AWS/
├── README.md
├── docs/
│   ├── 01-parts-overview.md
│   ├── 02-services-summary.md
│   ├── 03-ss-guide.md
│   ├── 04-pipeline-review.md
│   └── 05-orchestration-lambda-stepfunctions.md
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
- `codes/01-IAM-S3-Glue-Athena.md`

### Step 2 — Compute and Self-managed Database on EC2
- `codes/02-EC2-PostgreSQL-CloudFormation.md`

### Step 3 — Warehouse Layer
- `codes/03-Redshift.md`
- `sql/redshift/03_report_pipeline.sql`

### Step 4 — Managed SQL + NoSQL
- `codes/04-RDS-Aurora-DynamoDB.md`
- `customers_batch_sumi.json`
- `get_items_sumi.json`

### Step 5 — Optional Orchestration Layer
- `docs/05-orchestration-lambda-stepfunctions.md`

Use this step if your implementation includes Lambda-based quality checks and Step Functions workflow orchestration.

---

## 4) Architecture Snapshot

Core path:

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

Extended path (if Lambda + Step Functions are included):

```text
Local PC → SSO/CLI → S3 (Bronze/Silver/Gold) → Lambda → Step Functions → Glue → Redshift → BI
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

- Added a full repository pipeline audit at `docs/04-pipeline-review.md`.
- Added orchestration extension documentation at `docs/05-orchestration-lambda-stepfunctions.md`.
- Updated README to explicitly include optional Lambda + Step Functions + diagram path.
- Kept all examples public-safe and parameterized.

---

## 7) Next Recommended Improvements

- Add real IaC artifacts for Lambda and Step Functions (`templates/stepfunctions-pipeline.yaml`).
- Add sample Lambda handlers under `lambda/` and execution examples.
- Add architecture image asset referenced from README.
- Add CI checks for markdown/json/sql linting.

These steps will make the orchestration layer verifiable as code, not only as documentation.
