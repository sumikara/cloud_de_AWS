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

<img width="1135" height="403" alt="Architecture of the work" src="https://github.com/user-attachments/assets/1baf4605-9216-481a-8273-a8ff59893622" />

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
