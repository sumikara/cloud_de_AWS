
# Part 2 — EC2, PostgreSQL, Apache, Monitoring, CloudFormation

## Scope
This document gathers the command-oriented parts of the EC2 task: server creation, PostgreSQL installation, SSH-based access, S3 interaction, Apache installation, and CloudFormation templating.

## 1. Connect to EC2

```bash
ssh -i "C:\Users\Sümeyye Karabacak\Desktop__\AWS\aws2\Ec2_PG_Server_Keys_sumi.pem" ec2-user@63.178.71.121
```

## 2. Update packages

```bash
sudo dnf update -y
```

## 3. Install PostgreSQL 15

```bash
sudo dnf install -y postgresql15 postgresql15-server
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl status postgresql
```

## 4. Basic PostgreSQL objects

```sql
SELECT version();

CREATE TABLE test_table(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

CREATE OR REPLACE FUNCTION insert_data(p_name VARCHAR, p_age INT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO test_table(name, age) VALUES (p_name, p_age);
END;
$$ LANGUAGE plpgsql;

SELECT insert_data('Sumi', 25);

CREATE OR REPLACE VIEW v_adults AS
SELECT id, name, age
FROM test_table
WHERE age >= 18;

SELECT * FROM test_table;
SELECT * FROM v_adults;

SELECT schemaname, viewname
FROM pg_views
WHERE viewname = 'v_adults';
```

## 5. Copy from S3 on EC2

```bash
aws s3 ls s3://sumeyye-karabacak-bucket/
aws s3 cp s3://sumeyye-karabacak-bucket/test.txt /home/ec2-user/
ls -l /home/ec2-user/
```

## 6. Install Apache and publish a page

```bash
sudo dnf install -y httpd
httpd -v
sudo systemctl start httpd
sudo systemctl enable httpd
sudo systemctl status httpd
echo "<h1>sumis first web page on EC2- happii</h1>" | sudo tee /var/www/html/index.html
```

## 7. Monitoring
- Create an SNS topic with email subscription
- Create a CloudWatch alarm for EC2 resource threshold, such as CPU utilization

## 8. CloudFormation template
Store the parameterized EC2 template under `templates/ec2-sumeyye-stack.yaml`.

## Notes
- Instance profile used for S3 access
- IMDSv2 required
- Recommended disk layout: 8 GiB root + 10 GiB additional EBS
- Security group: `dilab-training`
