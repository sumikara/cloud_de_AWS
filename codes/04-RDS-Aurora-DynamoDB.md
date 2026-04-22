# Part 4 — DB Services (RDS MySQL, Aurora, DynamoDB)

## objective summary
This final module demonstrates production-style managed database practice across SQL and NoSQL: build a restartable MySQL initialization script on RDS, run meaningful Aurora queries through secure private connectivity (console + SSH bastion), and execute DynamoDB lifecycle operations by CLI (create table, load 20+ rows, retrieve by key, filter/select patterns, and delete records). All sensitive values are replaced with placeholders so the guide is safe for public portfolio use.

---

## 1) Big-picture architecture

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

Part 4 active flow:

```text
Local PC
  ├─ SQL client → RDS MySQL (publicly reachable only if intentionally exposed)
  ├─ SQL client → SSH tunnel via EC2 → Aurora (private endpoint)
  └─ AWS CLI → DynamoDB API (create/write/read/delete)
```

---

## 2) Artifact map by extension

| Purpose | File | Type |
|---|---|---|
| Step by step runbook + interpretation | `codes/04-RDS-Aurora-DynamoDB.md` | `.md` |
| DynamoDB batch write payload (20+ rows) | `customers_batch_sumi.json` | `.json` |
| DynamoDB batch get payload (5+ keys) | `get_items_sumi.json` | `.json` |
| Optional relational init script extraction | `sql/mysql/04_init.sql` | `.sql` |
| Optional Dynamo automation wrapper | `scripts/dynamo_seed.py` | `.py` |
| Optional infra templates | `templates/*.yaml` | `.yaml` |

---

## 3) RDS MySQL (restartable initial script)

### 3.1 Why this script structure
A restartable initialization script must be idempotent:
- `CREATE ... IF NOT EXISTS`
- `DROP ... IF EXISTS` before object recreation when needed
- `INSERT ... ON DUPLICATE KEY UPDATE` for repeat-safe DML

### 3.2 Admin bootstrap vs personal user
- Admin credentials are used only once to create/grant a personal user.
- All later operations should run with the personal user.
- Never store real passwords in repository files.

### 3.3 Practical SQL script (public-safe)

```sql
-- 1) user + schema
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY '<strong-password-xx>';
CREATE SCHEMA IF NOT EXISTS app_relational;

-- 2) privileges
GRANT ALL PRIVILEGES ON app_relational.* TO 'app_user'@'%';
GRANT CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, TRIGGER ON app_relational.* TO 'app_user'@'%';
FLUSH PRIVILEGES;

-- 3) validation
SELECT CURRENT_USER(), USER();
SHOW GRANTS FOR CURRENT_USER;

-- 4) table
CREATE TABLE IF NOT EXISTS app_relational.people (
  person_id INT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  age INT NOT NULL,
  city VARCHAR(100),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5) idempotent seed
INSERT INTO app_relational.people (person_id, full_name, age, city)
VALUES
  (1, 'Ada Lovelace', 36, 'London'),
  (2, 'Alan Turing', 41, 'Manchester'),
  (3, 'Grace Hopper', 85, 'New York')
ON DUPLICATE KEY UPDATE
  full_name = VALUES(full_name),
  age = VALUES(age),
  city = VALUES(city);

-- 6) view
DROP VIEW IF EXISTS app_relational.v_adults;
CREATE SQL SECURITY INVOKER VIEW app_relational.v_adults AS
SELECT person_id, full_name, age, city
FROM app_relational.people
WHERE age >= 18;

-- 7) procedure (portable pattern)
DROP PROCEDURE IF EXISTS app_relational.add_or_update_person;
DELIMITER $$
CREATE PROCEDURE app_relational.add_or_update_person(
    IN p_person_id INT,
    IN p_full_name VARCHAR(100),
    IN p_age INT,
    IN p_city VARCHAR(100)
)
BEGIN
  INSERT INTO app_relational.people (person_id, full_name, age, city)
  VALUES (p_person_id, p_full_name, p_age, p_city)
  ON DUPLICATE KEY UPDATE
    full_name = VALUES(full_name),
    age = VALUES(age),
    city = VALUES(city);
END$$
DELIMITER ;

-- 8) quick tests
CALL app_relational.add_or_update_person(4, 'Donald Knuth', 86, 'Stanford');
SELECT * FROM app_relational.people ORDER BY person_id;
SELECT * FROM app_relational.v_adults ORDER BY person_id;
```

Interpretation:
- View gives reusable semantic filtering.
- Procedure centralizes write logic and keeps app-side SQL cleaner.

---

## 4) Aurora access and meaningful querying

### 4.1 Why Aurora from local PC usually needs bastion/SSH tunnel
Unlike a publicly exposed RDS MySQL instance, Aurora is commonly deployed in private subnets without a public endpoint. That improves security, but local machines cannot connect directly. EC2 in the same VPC acts as a controlled bridge.

### 4.2 SSH tunnel command (local → EC2 → Aurora)

```bash
ssh -i "<jump-host-key>.pem" \
  -L 3307:<aurora-cluster-endpoint>:3306 \
  ec2-user@<jump-host-public-dns>
```

Then connect in DBeaver/MySQL client to:
- host: `127.0.0.1`
- port: `3307`
- db: `<db_name_xx>`
- user/password: `<xx>`

### 4.3 Meaningful Aurora query examples (not trivial)

```sql
-- Top 10 cities by total customer payments
SELECT c.city, SUM(p.amount) AS total_amount, COUNT(*) AS payment_count
FROM sakila.payment p
JOIN sakila.customer c ON p.customer_id = c.customer_id
GROUP BY c.city
ORDER BY total_amount DESC
LIMIT 10;

-- Monthly revenue trend
SELECT DATE_FORMAT(payment_date, '%Y-%m') AS ym,
       SUM(amount) AS revenue
FROM sakila.payment
GROUP BY DATE_FORMAT(payment_date, '%Y-%m')
ORDER BY ym;

-- Customers with high frequency rentals
SELECT c.customer_id, CONCAT(c.first_name,' ',c.last_name) AS full_name,
       COUNT(r.rental_id) AS rentals
FROM sakila.customer c
JOIN sakila.rental r ON c.customer_id = r.customer_id
GROUP BY c.customer_id, full_name
HAVING COUNT(r.rental_id) >= 20
ORDER BY rentals DESC;
```

---

## 5) DynamoDB (API-first operations)

## 5.1 Create table (CLI)

```bash
aws dynamodb create-table \
  --table-name customer_profile_nosql \
  --attribute-definitions AttributeName=customer_id,AttributeType=S \
  --key-schema AttributeName=customer_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region eu-central-1 \
  --profile students-role
```

### Why `customer_id` as partition key
- high cardinality (good partition distribution),
- direct item lookup pattern (`GetItem/Query`) is frequent,
- avoids hot partitions better than low-cardinality keys like city.

## 5.2 Insert 20+ rows (batch)

```bash
aws dynamodb batch-write-item \
  --request-items file://customers_batch_sumi.json \
  --region eu-central-1 \
  --profile students-role
```

## 5.3 Retrieve 5+ rows by keys

```bash
aws dynamodb batch-get-item \
  --request-items file://get_items_sumi.json \
  --region eu-central-1 \
  --profile students-role
```

## 5.4 “Select-like” reads (scan/query examples)

```bash
# full scan (lab/demo only)
aws dynamodb scan \
  --table-name customer_profile_nosql \
  --region eu-central-1 \
  --profile students-role

# filter: city = Istanbul
aws dynamodb scan \
  --table-name customer_profile_nosql \
  --filter-expression "city = :c" \
  --expression-attribute-values '{":c":{"S":"Istanbul"}}' \
  --region eu-central-1 \
  --profile students-role

# filter: age >= 25
aws dynamodb scan \
  --table-name customer_profile_nosql \
  --filter-expression "age >= :a" \
  --expression-attribute-values '{":a":{"N":"25"}}' \
  --region eu-central-1 \
  --profile students-role

# key-based query (preferred when key is known)
aws dynamodb query \
  --table-name customer_profile_nosql \
  --key-condition-expression "customer_id = :cid" \
  --expression-attribute-values '{":cid":{"S":"1"}}' \
  --region eu-central-1 \
  --profile students-role
```

## 5.5 Delete 2 items

```bash
aws dynamodb delete-item \
  --table-name customer_profile_nosql \
  --key '{"customer_id":{"S":"19"}}' \
  --region eu-central-1 \
  --profile students-role

aws dynamodb delete-item \
  --table-name customer_profile_nosql \
  --key '{"customer_id":{"S":"20"}}' \
  --region eu-central-1 \
  --profile students-role
```

## 5.6 Verify post-delete row count

```bash
aws dynamodb scan \
  --table-name customer_profile_nosql \
  --select "COUNT" \
  --region eu-central-1 \
  --profile students-role
```

Interpretation:
- `Scan` is expensive at scale; use key-centric access patterns for performance.
- Retry `UnprocessedItems` from batch operations with exponential backoff in production.

--

This completes the end-to-end portfolio with managed SQL + managed NoSQL service practice.
