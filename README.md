# AWS Data Engineering Practice Repository

This repository is a portfolio-style, end-to-end AWS data engineering practice project.
It follows this progression:

**Access → Storage → Catalog → Query → Compute → Warehouse → Managed DBs → NoSQL → Orchestration**.

Main region used in examples: `eu-central-1`.

---

## 1) Project Overview

Core modules:
1. IAM / SSO / S3 / Glue / Athena
2. EC2 / PostgreSQL / Apache / CloudWatch / CloudFormation
3. Redshift analytics + optimization + Spectrum
4. RDS MySQL / Aurora / DynamoDB
5. Lambda + Step Functions data quality orchestration

Goal: demonstrate practical SQL + NoSQL + orchestration patterns with public-safe artifacts.

---


## 1.1 Workflow image fit check (important)

If you use a workflow image in the project overview, make sure it matches the services actually implemented in this repository.

### Implemented in this repo
- IAM/SSO, STS
- S3
- Glue + Data Catalog + Athena
- EC2 + EBS + CloudWatch + SNS + CloudFormation
- Redshift (plus Spectrum concepts)
- RDS MySQL + Aurora
- DynamoDB
- Lambda + Step Functions

### Not implemented as executable modules in this repo
- AWS DMS
- Amazon EventBridge
- AWS Secrets Manager
- Amazon QuickSight

Recommendation:
- If your workflow image includes non-implemented services, label it as **"Target/Reference Architecture"**.
- For strict implementation proof, use a second image labeled **"Implemented Architecture"** with only the services above.

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
│   ├── 04-RDS-Aurora-DynamoDB.md
│   └── 05-Lambda-StepFunctions-DataQuality.md
├── sql/
│   └── redshift/
│       └── 03_report_pipeline.sql
├── lambda/
│   └── athena_iceberg_quality.py
├── templates/
│   ├── ec2-sumi-stack.yaml
│   └── stepfunctions-redshift-dq.asl.json
├── customers_batch_sumi.json
└── get_items_sumi.json
```

---

## 3) Run Order

1. `codes/01-IAM-S3-Glue-Athena.md`
2. `codes/02-EC2-PostgreSQL-CloudFormation.md`
3. `codes/03-Redshift.md` + `sql/redshift/03_report_pipeline.sql`
4. `codes/04-RDS-Aurora-DynamoDB.md`
5. `codes/05-Lambda-StepFunctions-DataQuality.md`

---

## 4) Architecture Snapshot

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
                                     └→ Lambda + Step Functions (data quality orchestration)
```

---

## 5) Security and Publishing Rules

Never commit:
- private keys (`.pem`, `.ppk`, `.ssh/*`)
- real credentials and tokens
- account-specific private endpoints
- hardcoded ARNs/usernames/passwords

Use placeholders:
- `<account-id>`
- `<cluster-endpoint>`
- `<db-user>`
- `<strong-password-xx>`

---

## 6) Latest Additions

- Data quality orchestration runbook: `codes/05-Lambda-StepFunctions-DataQuality.md`
- Step Functions ASL template: `templates/stepfunctions-redshift-dq.asl.json`
- Lambda sample for Athena Iceberg flow: `lambda/athena_iceberg_quality.py`

---

## 7) Next Improvements

- Add IaC for Lambda + Step Functions deployment.
- Add real CloudWatch metrics/alarms mapping per state.
- Add failure simulation test events for Step Functions Choice branches.
- Add CI lint for markdown/json/python/sql.
