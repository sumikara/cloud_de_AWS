# cloud_de_AWS
# AWS Practice Repository

A compact but end-to-end AWS practice repository built from four training tasks covering identity and access, object storage, data lake basics, virtual machines, database-on-EC2, Redshift analytics concepts, and managed database services.

> **Context**
> This repository consolidates earlier hands-on AWS learning materials into one clean portfolio-ready structure.  
> Main region used across the tasks: **eu-central-1 (Frankfurt)**.  
> EPAM VPN was required for restricted resources in several steps.  
> Mandatory resource tag used throughout the tasks: **`owner=student`**. fileciteturn2file0L1-L18

---

## 1. Repository Purpose

This repo demonstrates a practical AWS learning path that starts with secure account access and S3 usage, continues with EC2-based infrastructure and self-managed PostgreSQL, moves into Redshift-oriented analytical design, and finishes with managed database services such as RDS MySQL, Aurora, and DynamoDB. The source materials show both actual hands-on execution and, for some Redshift parts, theory-based completion when service access was unavailable. fileciteturn2file0L19-L37 fileciteturn2file2L1-L20

---

## 2. Covered Practice Areas

### 1 — IAM, SSO, S3, Glue, Athena
- AWS Console login with SSO
- CLI setup with `aws configure sso`
- Role switching from `User` to `students-role`
- Bucket creation and file upload with AWS CLI
- Uploading DWH-style files to S3 folder hierarchy
- Registering S3 data through Glue/Data Catalog
- Querying S3-backed data through Athena fileciteturn2file0L19-L53

### 2 — EC2, EBS, PostgreSQL, Apache, Monitoring, CloudFormation
- Launching an **EC2 t2.micro** with **Amazon Linux 2023**
- Enforcing **IMDSv2**
- Attaching **8 GiB root** and **10 GiB extra EBS**
- Installing and running **PostgreSQL 15**
- Connecting from DBeaver via **SSH tunnel**
- Copying files between S3 and EC2
- Installing Apache and publishing a test web page
- Creating **SNS topic** and **CloudWatch alarm**
- Reproducing the instance through **CloudFormation** fileciteturn2file1L1-L18 fileciteturn2file1L19-L74

### 3 — Redshift Analytics Flow
- Using EC2 as a jump server for Redshift access
- Treating S3 as data lake storage
- Profiling with **Athena**
- Transforming with **Glue Spark**
- Registering metadata in **Glue Data Catalog**
- Loading curated tables into Redshift via `COPY`
- Reasoning about compression, distribution style, sort keys, and report-oriented stored procedures
- Explaining optimization logic and result cache behavior
- Some sections were completed theoretically because Redshift access was unavailable at the time fileciteturn2file2L1-L36 fileciteturn1file0L1-L32

### 4 — Managed DB Services
- **RDS MySQL**: restartable schema/table/view/procedure script
- **Aurora**: secure connectivity through EC2 bastion + SSH tunnel
- **DynamoDB**: table creation, batch write, batch get, scan, and deletion workflow fileciteturn2file3L1-L81 fileciteturn1file4L1-L55

---

## 3. Repository Structure

```text
aws-practice-repo/
│
├── README.md
├── docs/
│   ├── 01_overview.md
│   ├── 02_services_summary.md
│   ├── 03_evidence_guide.md
│   └── 04_security_and_commit_rules.md
│
├── code/
│   ├── 01_iam_s3_glue_athena.md
│   ├── 02_ec2_postgresql_cloudformation.md
│   ├── 03_redshift.md
│   └── 04_rds_aurora_dynamodb.md
│
├── templates/
│   └── ec2-sumeyye-stack.yaml
│
├── assets/
│   ├── Part 1/
│   ├── Part 2/
│   ├── Part 3/
│   └── Part 4/
│
└── samples/
    ├── customers_batch_sumi.json
    └── get_items_sumi.json
```

---

## 4. Key Learning Flow

The materials reflect a natural cloud learning progression:

1. **Authenticate and authorize access** with SSO, CLI profiles, and role assumption.
2. **Store files in S3** and organize them as a simple data lake.
3. **Catalog and query data** using Glue and Athena.
4. **Provision compute with EC2** and attach storage through EBS.
5. **Run PostgreSQL on EC2** to understand IaaS-style database hosting.
6. **Use EC2 as a bastion host** for private AWS services.
7. **Analyze warehouse design choices** in Redshift, including `COPY`, compression, distribution, and sort strategy.
8. **Work with managed databases** through RDS MySQL and Aurora.
9. **Use NoSQL patterns** through DynamoDB.
10. **Automate infrastructure** with CloudFormation and monitor it with CloudWatch + SNS. fileciteturn2file1L1-L18 fileciteturn2file2L21-L53 fileciteturn2file3L1-L81

---

## 5. Highlights by Parts

### Part 1 Highlights
The IAM/S3 task established the foundation for later tasks: SSO setup, CLI profile configuration, and role-based access. It then moved into practical S3 usage and data lake-style organization, followed by Glue crawler/Data Catalog registration and Athena querying. fileciteturn2file0L19-L53

### Part  2 Highlights
The EC2 task focused on the lowest-cost database hosting approach: launching a small Linux server and installing PostgreSQL manually. It also expanded into supporting services such as EBS, Apache, snapshots/AMI logic, monitoring, and infrastructure-as-code with CloudFormation. fileciteturn2file1L1-L18

### Part  3 Highlights
The Redshift task connected the earlier S3 and EC2 work into an analytics workflow. The materials describe S3 as data lake storage, Glue Spark for transformation, Athena for profiling, Redshift `COPY` for loading, and SQL/reporting logic for KPI-oriented analysis. The report procedure used a fact table joined with customer and product dimensions to compute sales by category, city, and month. fileciteturn1file0L1-L22 fileciteturn2file2L21-L58

### Part  4 Highlights
The managed DB task compared different database access patterns:
- **RDS MySQL** allowed direct SQL environment setup.
- **Aurora** required a private-network approach through EC2 SSH tunneling.
- **DynamoDB** introduced JSON request bodies for batch operations and key-based retrieval. fileciteturn2file3L1-L81 fileciteturn1file4L1-L55

---

## 6. Security and Publishing Notes

### What should never be committed
- `.pem` private keys
- `.ssh/` private key material
- local AWS credential files such as `~/.aws/credentials`
- access tokens, passwords, session tokens, or copied console secrets
- screenshots that expose secrets or live credentials

The original training instructions explicitly say **do not commit or share credentials**. fileciteturn2file0L1-L18

### What should be sanitized before publishing
Even if something was acceptable in a classroom environment, public GitHub content should not expose:
- hardcoded passwords
- full private infrastructure details
- temporary account-specific values unless intentionally shared
- mentor-provided credentials from task sheets

---

## 7. Evidence Strategy

A public portfolio repo should include **selected evidence**, not every raw screenshot.

Recommended approach:
- keep **representative screenshots** in `assets/`
- use **small, compressed PNG/JPG files**
- reference them from task docs where they add proof
- avoid uploading repetitive screenshots showing the same action multiple times
- redact passwords, usernames, tokens, private endpoints, and local file paths when possible

every screenshot prove one meaningful milestone such as successful SSO auth, bucket creation, EC2 running, PostgreSQL status, SSH-tunneled connection, Redshift table creation, or DynamoDB batch retrieval.

---

## 8. Summary — AWS Services Used, in Practical Order

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

This sequence is reconstructed from the uploaded task materials and your completion notes. fileciteturn2file0L19-L53 fileciteturn2file1L1-L18 fileciteturn2file2L21-L58 fileciteturn2file3L1-L81

---

## 9. Notes on Completeness

- The uploaded CloudFormation template is reusable and safe to keep in the repo because it is parameterized and does not contain embedded secrets. 
- The uploaded DynamoDB batch JSON appears to contain sample customer records, not secrets. Keep it only if you want to demonstrate request-body structure for CLI usage.

---


