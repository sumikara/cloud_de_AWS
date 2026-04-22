# Part 4 — RDS + Aurora + DynamoDB (Technical Implementation and Interpretation)

## 0) One-paragraph objective summary
This final section validates both relational and NoSQL managed database practice in AWS: create and test a MySQL workload on RDS, connect to private Aurora through an EC2 SSH tunnel, design and operate a DynamoDB table with batch write/read patterns, and interpret service-level tradeoffs (consistency, scaling, cost, and query patterns). The goal is to show practical cloud database engineering decisions, not only command execution.

---

## 1) Bird’s-eye architecture and purpose

- **RDS MySQL**: managed relational engine for transactional SQL patterns
- **Aurora MySQL-compatible**: managed high-availability relational cluster pattern
- **EC2 jump host**: secure access bridge to private database endpoints
- **DynamoDB**: serverless key-value/NoSQL access for low-latency reads/writes
- **S3 + Glue + Athena + Redshift (previous parts)**: analytical pipeline integration context

Required full-chain view:

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

Part 4 active path:

```text
Local PC
  ├─ DBeaver / mysql client
  │   └─ SSH tunnel via EC2
  │       └─ Aurora (private)
  ├─ Direct SQL client
  │   └─ RDS MySQL endpoint
  └─ AWS CLI
      └─ DynamoDB table (batch write/get/scan/query)
```

---

## 2) Artifact mapping by file type

| Purpose | Suggested file | Extension |
|---|---|---|
| Runbook and interpretation | `codes/04-RDS-Aurora-DynamoDB.md` | `.md` |
| RDS/Aurora SQL setup scripts | `sql/mysql/04_relational_setup.sql` (optional) | `.sql` |
| DynamoDB batch write payload | `customers_batch_sumi.json` | `.json` |
| DynamoDB batch get payload | `get_items_sumi.json` | `.json` |
| Optional CLI automation | `scripts/dynamo_seed.py` | `.py` |
| Optional infra templates | `templates/*.yaml` | `.yaml` |

Combined purpose: demonstrate both SQL and NoSQL implementation with reusable, public-safe assets.

---

## 3) RDS MySQL: practical SQL build (transactional baseline)

> Use placeholders for all secrets. Do not commit real passwords.

```sql
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY '<strong-password-xx>';
CREATE SCHEMA IF NOT EXISTS app_relational;
GRANT ALL PRIVILEGES ON app_relational.* TO 'app_user'@'%';
GRANT CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, TRIGGER ON app_relational.* TO 'app_user'@'%';
FLUSH PRIVILEGES;

USE app_relational;

CREATE TABLE IF NOT EXISTS customer_profile (
  customer_id INT PRIMARY KEY,
  customer_name VARCHAR(100) NOT NULL,
  age INT NOT NULL,
  city VARCHAR(100),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customer_profile (customer_id, customer_name, age, city)
VALUES
  (1, 'Ada Lovelace', 36, 'London'),
  (2, 'Alan Turing', 41, 'Manchester'),
  (3, 'Grace Hopper', 85, 'New York')
ON DUPLICATE KEY UPDATE
  customer_name = VALUES(customer_name),
  age = VALUES(age),
  city = VALUES(city);

DROP VIEW IF EXISTS v_customer_adults;
CREATE SQL SECURITY INVOKER VIEW v_customer_adults AS
SELECT customer_id, customer_name, age, city
FROM customer_profile
WHERE age >= 18;
```

Procedure pattern (portable):

```sql
DROP PROCEDURE IF EXISTS app_relational.upsert_customer;
DELIMITER $$
CREATE PROCEDURE app_relational.upsert_customer(
    IN p_customer_id INT,
    IN p_customer_name VARCHAR(100),
    IN p_age INT,
    IN p_city VARCHAR(100)
)
BEGIN
  INSERT INTO app_relational.customer_profile (customer_id, customer_name, age, city)
  VALUES (p_customer_id, p_customer_name, p_age, p_city)
  ON DUPLICATE KEY UPDATE
    customer_name = VALUES(customer_name),
    age = VALUES(age),
    city = VALUES(city);
END$$
DELIMITER ;

CALL app_relational.upsert_customer(4, 'Donald Knuth', 86, 'Stanford');
SELECT * FROM app_relational.customer_profile ORDER BY customer_id;
SELECT * FROM app_relational.v_customer_adults ORDER BY customer_id;
```

Interpretation:
- View gives reusable semantic filtering.
- Procedure centralizes write logic and keeps app-side SQL cleaner.

---

## 4) Aurora private access via EC2 SSH tunnel

```bash
ssh -i "<jump-host-key>.pem" \
  -L 3307:<aurora-cluster-endpoint>:3306 \
  ec2-user@<jump-host-public-dns>
```

In SQL client (DBeaver/MySQL Workbench):
- host: `127.0.0.1`
- port: `3307`
- database: `<db_name_xx>`
- user/password: `<xx>`

Interpretation:
- Aurora stays private inside VPC.
- SSH tunnel provides controlled access without opening broad public DB access.

---

## 5) DynamoDB NoSQL: technical coding + interpretation

### 5.1 Table modeling recommendation

Table name: `customer_profile_nosql`

- Partition key: `customer_id` (String)
- Optional attributes: `customer_name`, `age`, `city`, `segment`, `last_update_ts`
- Recommended billing for labs: **On-Demand** (simpler cost behavior)

### 5.2 Batch write from JSON

```bash
aws dynamodb batch-write-item \
  --request-items file://customers_batch_sumi.json \
  --region eu-central-1 \
  --profile students-role
```

### 5.3 Read patterns

Batch get:

```bash
aws dynamodb batch-get-item \
  --request-items file://get_items_sumi.json \
  --region eu-central-1 \
  --profile students-role
```

Scan (for small lab datasets only):

```bash
aws dynamodb scan \
  --table-name customer_profile_nosql \
  --region eu-central-1 \
  --profile students-role
```

Query example (preferred over scan when key known):

```bash
aws dynamodb query \
  --table-name customer_profile_nosql \
  --key-condition-expression "customer_id = :cid" \
  --expression-attribute-values '{":cid":{"S":"1"}}' \
  --region eu-central-1 \
  --profile students-role
```

### 5.4 Interpretation (important)

- `Scan` reads many items and is expensive at scale.
- `Query` is key-based and much more efficient.
- `BatchWriteItem` can return `UnprocessedItems`; production code must retry with backoff.
- DynamoDB gives very low latency for key access, but joins are not native like SQL.

---

## 6) Public-safe JSON payload patterns

`customers_batch_sumi.json` should contain:
- table key: `customer_profile_nosql`
- multiple `PutRequest` entries with typed DynamoDB attributes.

`get_items_sumi.json` should contain:
- table key: `customer_profile_nosql`
- list of key objects for `BatchGetItem`.

---

## 7) Validation checklist (what to prove in report)

1. RDS SQL objects exist: table + view + procedure.
2. Procedure call updates/inserts as expected.
3. Aurora reachable only through tunnel path.
4. DynamoDB batch write succeeded with no remaining unprocessed items.
5. Query returns expected item(s) by partition key.
6. Explain why query pattern beats scan pattern.

---

## 8) What was removed/refactored and why

- Personal endpoints, keys, emails, and credentials
  - removed for security and public publishing safety.
- Repetitive terminal transcripts
  - replaced with concise executable blocks.
- weak/default password examples
  - replaced with placeholder + security guidance.
- student-specific naming that reduces reuse
  - normalized to portfolio-safe generic names.

---

## 9) Final technical takeaway

By completing Part 4, you demonstrate:
- relational modeling and routines on managed SQL,
- secure private DB connectivity patterns (bastion/tunnel),
- NoSQL access design and CLI operation patterns,
- engineering-level interpretation of performance and cost behavior.

This closes the portfolio with both OLTP-style SQL and key-value NoSQL practice on AWS.
