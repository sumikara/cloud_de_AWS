# Part 3 — Redshift, Data Lake, Glue, Athena

## Scope
This document consolidates the Redshift-related SQL and workflow logic. Some parts were written as theory-based completion because the Redshift service was unavailable during the assignment period.

## 1. Redshift access preparation on EC2

```bash
sudo dnf update
sudo dnf install postgresql15.x86_64 postgresql15-server
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```

## 2. Check Redshift connectivity

```bash
psql -h data-xx-lab-redshift-cluster-3.cettexdsxw3xx.eu-central-1.redshift.amazonaws.com -v schema=public -p 5439 -U <user_name> -d dev
```

## 3. Practical workflow
1. Upload source data to S3.
2. Profile data in Athena.
3. Transform and catalog data through Glue / Glue Spark.
4. Connect to Redshift through EC2 SSH tunnel.
5. Create schema and tables.
6. Load selected tables via `COPY`.
7. Analyze encoding, distribution, and sort strategies.
8. Build a report stored procedure.

## 4. Example schema and load pattern

```sql
CREATE SCHEMA IF NOT EXISTS dilab_training;

CREATE TABLE IF NOT EXISTS dilab_training.fct_sales (
    customer_id INT,
    product_id INT,
    transaction_date DATE,
    payment_amount DECIMAL(18,2),
    unit INT
);
```

### Example COPY pattern
```sql
COPY xxlab_train.fct_sales
FROM 's3://<my-bucket>/<path>/fct_sales.csv'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-role>'
REGION 'eu-central-1'
DELIMITER ','
CSV
DATEFORMAT AS 'MM-DD-YYYY'
IGNOREHEADER 1;
```

## 5. Compression and metadata inspection

```sql
ANALYZE COMPRESSION fct_sales;

SELECT "column", type, encoding
FROM pg_table_def
WHERE tablename = 'fct_sales';

SELECT "table", diststyle, sortkey1
FROM svv_table_info
WHERE "table" = 'dim_customers';
```

## 6. Stored procedure for reporting

```sql
CREATE OR REPLACE PROCEDURE total_sales_by_customer_and_category_report()
LANGUAGE plpgsql
AS $$
BEGIN
    DROP TABLE IF EXISTS tmp_sales_report_final;

    CREATE TEMP TABLE tmp_sales_report_final AS
    SELECT
        dp.product_category,
        dc.customer_city,
        EXTRACT(MONTH FROM fs.transaction_date) AS sales_month,
        SUM(fs.payment_amount) AS total_sales_amount,
        COUNT(fs.customer_id) AS number_of_transactions
    FROM dilab_training.fct_sales fs
    LEFT JOIN dilab_training.dim_products dp
        ON fs.product_id = dp.product_id
    LEFT JOIN dilab_training.dim_customers dc
        ON fs.customer_id = dc.customer_id
    WHERE EXTRACT(YEAR FROM fs.transaction_date) = 2024
    GROUP BY 1, 2, 3
    ORDER BY sales_month, total_sales_amount DESC;

    RAISE NOTICE 'Three-table sales report loaded successfully into tmp_sales_report_final.';
END;
$$;

CALL total_sales_by_customer_and_category_report();
SELECT * FROM tmp_sales_report_final;
```

## 7. Result-cache warning before performance comparison

```sql
SET enable_result_cache_for_session = OFF;
```

## 8. Optimization logic
- Choose `DISTKEY` based on most frequent join column
- Choose `SORTKEY` based on most frequent filter column, especially dates
- Small dimensions may use `ALL`
- Large fact tables often benefit from `KEY` instead of default even-style spreading

## Note
Be transparent in the repo that some Redshift sections are theoretical due to service shutdown.

