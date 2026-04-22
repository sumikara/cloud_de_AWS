# AWS Data Engineering Practice Repository

This repository is a portfolio-style, end-to-end AWS data engineering practice project.
It follows this progression:

**Access → Storage → Catalog → Query → Compute → Warehouse → Managed DBs → NoSQL → Orchestration**.

## 1. Repository Purpose

This repo demonstrates a practical AWS learning path that starts with secure account access and S3 usage, continues with EC2-based infrastructure and self-managed PostgreSQL, moves into Redshift-oriented analytical design, and finishes with managed database services such as RDS MySQL, Aurora, and DynamoDB. The source materials show both actual hands-on execution and, for some Redshift parts, theory-based completion when service access was unavailable. 

Main region used in examples: `eu-central-1`.

Core modules:
1. IAM / SSO / S3 / Glue / Athena
2. EC2 / PostgreSQL / Apache / CloudWatch / CloudFormation
3. Redshift analytics + optimization + Spectrum
4. RDS MySQL / Aurora / DynamoDB
5. Lambda + Step Functions data quality orchestration

## 2. Project Overview

Core modules:
1. IAM / SSO / S3 / Glue / Athena
2. EC2 / PostgreSQL / Apache / CloudWatch / CloudFormation
3. Redshift analytics + optimization + Spectrum
4. RDS MySQL / Aurora / DynamoDB
5. Lambda + Step Functions data quality orchestration

Goal: demonstrate practical SQL + NoSQL + orchestration patterns with public-safe artifacts.

### 2.1 — IAM, SSO, S3, Glue, Athena
- AWS Console login with SSO
- CLI setup with `aws configure sso`
- Role switching from `User` to `students-role`
- Bucket creation and file upload with AWS CLI
- Uploading DWH-style files to S3 folder hierarchy
- Registering S3 data through Glue/Data Catalog
- Querying S3-backed data through Athena fileciteturn2file0L19-L53

### 2.2 — EC2, EBS, PostgreSQL, Apache, Monitoring, CloudFormation
- Launching an **EC2 t2.micro** with **Amazon Linux 2023**
- Enforcing **IMDSv2**
- Attaching **8 GiB root** and **10 GiB extra EBS**
- Installing and running **PostgreSQL 15**
- Connecting from DBeaver via **SSH tunnel**
- Copying files between S3 and EC2
- Installing Apache and publishing a test web page
- Creating **SNS topic** and **CloudWatch alarm**
- Reproducing the instance through **CloudFormation**

### 2.3 — Redshift Analytics Flow
- Using EC2 as a jump server for Redshift access
- Treating S3 as data lake storage
- Profiling with **Athena**
- Transforming with **Glue Spark**
- Registering metadata in **Glue Data Catalog**
- Loading curated tables into Redshift via `COPY`
- Reasoning about compression, distribution style, sort keys, and report-oriented stored procedures
- Explaining optimization logic and result cache behavior
- Some sections were completed theoretically because Redshift access was unavailable at the time 

### 2.4 — Managed DB Services
- **RDS MySQL**: restartable schema/table/view/procedure script
- **Aurora**: secure connectivity through EC2 bastion + SSH tunnel
- **DynamoDB**: table creation, batch write, batch get, scan, and deletion workflow 

### Implemented in this repo
- IAM/SSO, STS
- S3
- Glue + Data Catalog + Athena
- EC2 + EBS + CloudWatch + SNS + CloudFormation
- Redshift (plus Spectrum concepts)
- RDS MySQL + Aurora
- DynamoDB
- Lambda + Step Functions

---

## 3. Architecture Snapshot

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
                                     └→ Lambda + Step Functions (data quality orchestration)
```

---
## 4. Key Learning Flow

1. **Authenticate and authorize access** with SSO, CLI profiles, and role assumption.
2. **Store files in S3** and organize them as a simple data lake.
3. **Catalog and query data** using Glue and Athena.
4. **Provision compute with EC2** and attach storage through EBS.
5. **Run PostgreSQL on EC2** to understand IaaS-style database hosting.
6. **Use EC2 as a bastion host** for private AWS services.
7. **Analyze warehouse design choices** in Redshift, including `COPY`, compression, distribution, and sort strategy.
8. **Work with managed databases** through RDS MySQL and Aurora.
9. **Use NoSQL patterns** through DynamoDB.
10. **Automate infrastructure** with CloudFormation and monitor it with CloudWatch + SNS. 

## 5) Security and Publishing Rules

PRIVATE docs:
- private keys (`.pem`, `.ppk`, `.ssh/*`)
- real credentials and tokens
- account-specific private endpoints
- hardcoded ARNs/usernames/passwords

I used placeholders for:
- `<account-id>`
- `<cluster-endpoint>`
- `<db-user>`
- `<strong-password-xx>`

---
## 6. Summary — AWS Services Used, in Practical Order

| Order | Service | Purpose in This Repo |
|---|---|---|
| 1 | IAM Identity Center / SSO | Secure sign-in and CLI profile bootstrap |
| 2 | STS | Identity verification and assumed-role usage |
| 3 | S3 | Bucket storage, file uploads, simple data lake layout |
| 4 | Glue / Data Catalog / Crawler | Registering S3 datasets and metadata discovery |
| 5 | Athena | Querying and profiling S3-backed data |
| 6 | EC2 | Virtual machine for PostgreSQL, bastion access, and general compute |
| 7 | EBS | Persistent block storage for EC2 |
| 8 | PostgreSQL on EC2 | Self-managed relational database practice |
| 9 | Apache HTTP Server | Basic web service deployment on EC2 |
| 10 | SNS | Email notification target |
| 11 | CloudWatch | Monitoring EC2 metrics and alarm creation |
| 12 | CloudFormation | Infrastructure automation for EC2 deployment |
| 13 | Redshift | Data warehouse loading, modeling, and performance reasoning |
| 14 | RDS MySQL | Managed relational DB practice |
| 15 | Aurora | Private managed DB access through bastion/SSH tunneling |
| 16 | DynamoDB | NoSQL table operations with batch JSON requests |

---





