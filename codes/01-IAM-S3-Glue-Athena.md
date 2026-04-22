# Part 1 — IAM, S3, Glue, Athena

## Scope
This document consolidates the hands-on flow for AWS authentication, role assumption, S3 usage, and basic data-lake-style querying.

## 1. AWS CLI SSO setup

```bash
aws configure sso
aws sts get-caller-identity --profile user-role-260586643565
aws sts get-caller-identity --profile students-role
```

### Expected configuration logic
- Authenticate with SSO
- Use `user-role-260586643565` as the initial profile
- Assume `students-role` for task execution
- Operate in `eu-central-1`

## 2. S3 bucket creation

```bash
aws s3 mb s3://sumeyye-karabacak-bucket --region eu-central-1 --profile students-role
```

## 3. Upload a test file

```bash
aws s3 cp "C:\Users\Sümeyye Karabacak\Desktop__\test.txt" s3://sumeyye-karabacak-bucket/ --profile students-role
aws s3 ls s3://sumeyye-karabacak-bucket/ --profile students-role
```

## 4. Upload structured DWH-style files to S3

```bash
aws s3 cp "C:\Users\Sümeyye Karabacak\Desktop__\di_dwh_database\bl_dm\dim_customers\dim_customers.csv" s3://sumeyye-karabacak-bucket/di_dwh_database/bl_dm/dim_customers/ --profile students-role
```

## 5. Glue and Athena workflow
1. Place the dataset under a clean folder hierarchy in S3.
2. Register the S3 path through Glue Crawler / Data Catalog.
3. Query the discovered tables in Athena.
4. Inspect table properties and validate sample results.

## Notes
- Use **Frankfurt (`eu-central-1`)**
- Enable **EPAM VPN EU**
- Tag resources with **`owner=student`**
- Do **not** commit credentials

