
# Services Summary

## AWS services used, in practical sequence

| Sequence | Service | Why it was used |
|---|---|---|
| 1 | IAM Identity Center / SSO | Authentication to AWS console and CLI bootstrap |
| 2 | STS | Identity verification and role assumption checks |
| 3 | S3 | Bucket storage and data lake-style file organization |
| 4 | Glue Crawler / Data Catalog | Register S3 files as queryable datasets |
| 5 | Athena | Query and profile S3-backed data |
| 6 | EC2 | General compute, bastion/jump host, PostgreSQL host |
| 7 | EBS | Persistent storage for EC2 |
| 8 | PostgreSQL | Self-managed relational DB on EC2 |
| 9 | Apache HTTP Server | Basic web service deployment on EC2 |
| 10 | SNS | Email notifications |
| 11 | CloudWatch | Metric alarms on EC2 |
| 12 | CloudFormation | Re-create EC2 infrastructure from template |
| 13 | Redshift | Warehouse loading and analytical optimization concepts |
| 14 | RDS MySQL | Managed relational database practice |
| 15 | Aurora | Private managed DB accessed through bastion host |
| 16 | DynamoDB | NoSQL key-based batch operations |

## Cross-service learning pattern
- Authentication and authorization come first.
- Storage and metadata come next.
- Compute and self-managed databases follow.
- Analytics and warehouse concepts build on the earlier storage layer.
- Managed DB and NoSQL services round out the practice set.
