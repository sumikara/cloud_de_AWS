# Part 4 — RDS MySQL, Aurora, DynamoDB

## Scope
This document consolidates SQL and CLI materials from the managed database services part

---

## 1. RDS MySQL — restartable script

> Replace demo credentials before publishing publicly.

```sql
CREATE USER IF NOT EXISTS 'your_user'@'%' IDENTIFIED BY 'REPLACE_ME';
CREATE SCHEMA IF NOT EXISTS mysql_sch;
GRANT ALL PRIVILEGES ON mysql_sch.* TO 'your_user'@'%';
GRANT CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, TRIGGER ON mysql_sch.* TO 'your_user'@'%';
FLUSH PRIVILEGES;

SELECT CURRENT_USER(), USER();
SHOW GRANTS FOR CURRENT_USER;

CREATE TABLE IF NOT EXISTS mysql_sch.sanity_check (
  id INT PRIMARY KEY,
  note VARCHAR(100)
);
DROP TABLE IF EXISTS mysql_sch.sanity_check;

USE mysql_sch;

CREATE TABLE IF NOT EXISTS mysql_sch.people (
  person_id INT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  age INT NOT NULL,
  city VARCHAR(100) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO mysql_sch.people (person_id, full_name, age, city)
VALUES
  (1, 'Ada Lovelace', 36, 'London'),
  (2, 'Alan Turing', 41, 'Manchester'),
  (3, 'Grace Hopper', 85, 'New York')
ON DUPLICATE KEY UPDATE
  full_name = VALUES(full_name),
  age       = VALUES(age),
  city      = VALUES(city);

DROP VIEW IF EXISTS mysql_sch.v_adults;
CREATE SQL SECURITY INVOKER VIEW v_adults AS
SELECT person_id, full_name, age, city
FROM people
WHERE age >= 18;
```

### Procedure note
Some MySQL environments do not support `CREATE PROCEDURE IF NOT EXISTS` directly.  
A portable pattern is:
1. `DROP PROCEDURE IF EXISTS ...`
2. `DELIMITER $$`
3. `CREATE PROCEDURE ...`
4. `DELIMITER ;`

```sql
DROP PROCEDURE IF EXISTS mysql_sch.add_or_update_person;
DELIMITER $$
CREATE PROCEDURE mysql_sch.add_or_update_person(
    IN p_person_id INT,
    IN p_full_name VARCHAR(100),
    IN p_age INT,
    IN p_city VARCHAR(100)
)
BEGIN
  INSERT INTO mysql_sch.people (person_id, full_name, age, city)
  VALUES (p_person_id, p_full_name, p_age, p_city)
  ON DUPLICATE KEY UPDATE
    full_name = VALUES(full_name),
    age       = VALUES(age),
    city      = VALUES(city);
END$$
DELIMITER ;

CALL mysql_sch.add_or_update_person(4, 'Donald Knuth', 86, 'Stanford');
SELECT * FROM mysql_sch.people ORDER BY person_id;
SELECT * FROM mysql_sch.v_adults ORDER BY person_id;
```

---

## 2. Aurora — SSH tunnel through EC2

```bash
ssh -i "Ec2_PG_Server_Keys_sumi.pem" \
  -L 3307:xxlab-aurora-cluster.cluster-cqlpneuyr8on.eu-central-1.rds.amazonaws.com:3306 \
  ec2-user@ec2-3-72-108-205.eu-central-1.compute.amazonaws.com
```

### Why this pattern is needed
Aurora was treated as privately accessible in the task environment, so a local machine could not connect directly. EC2 was used as a bastion/jump server in the same VPC, and DBeaver then connected to `127.0.0.1:3307` through the tunnel.

---

## 3. DynamoDB batch write

```bash
aws dynamodb batch-write-item \
  --request-items file://customers_batch_sumi.json \
  --region eu-central-1 \
  --profile students-role
```

## 4. DynamoDB scan

```bash
aws dynamodb scan \
  --table-name dim_customers_sumi \
  --region eu-central-1 \
  --profile students-role
```

## 5. DynamoDB batch get

```bash
aws dynamodb batch-get-item \
  --request-items file://get_items_sumi.json \
  --region eu-central-1 \
  --profile students-role
```

## 6. Sample request-body pattern for `get_items_sumi.json`

```json
{
  "dim_customers_sumi": {
    "Keys": [
      { "customer_surr_id": { "S": "1" } },
      { "customer_surr_id": { "S": "2" } },
      { "customer_surr_id": { "S": "3" } },
      { "customer_surr_id": { "S": "4" } },
      { "customer_surr_id": { "S": "5" } }
    ]
  }
}
```


