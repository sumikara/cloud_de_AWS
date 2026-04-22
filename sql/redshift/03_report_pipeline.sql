-- Part 3 Redshift SQL (public/sanitized)

CREATE SCHEMA IF NOT EXISTS analytics_practice;

DROP TABLE IF EXISTS analytics_practice.dim_client;
CREATE TABLE analytics_practice.dim_client (
    client_id        INTEGER ENCODE az64,
    client_name      VARCHAR(120) ENCODE zstd,
    client_city      VARCHAR(80) ENCODE zstd,
    client_segment   VARCHAR(40) ENCODE zstd,
    signup_date      DATE ENCODE az64
)
DISTSTYLE ALL
SORTKEY (client_id);

DROP TABLE IF EXISTS analytics_practice.dim_item;
CREATE TABLE analytics_practice.dim_item (
    item_id          INTEGER ENCODE az64,
    item_name        VARCHAR(140) ENCODE zstd,
    item_category    VARCHAR(60) ENCODE zstd,
    unit_price       DECIMAL(12,2) ENCODE az64
)
DISTSTYLE ALL
SORTKEY (item_id);

DROP TABLE IF EXISTS analytics_practice.fct_order;
CREATE TABLE analytics_practice.fct_order (
    order_id         BIGINT ENCODE az64,
    client_id        INTEGER ENCODE az64,
    item_id          INTEGER ENCODE az64,
    order_ts         TIMESTAMP ENCODE az64,
    quantity         INTEGER ENCODE az64,
    gross_amount     DECIMAL(14,2) ENCODE az64,
    discount_amount  DECIMAL(14,2) ENCODE az64,
    net_amount       DECIMAL(14,2) ENCODE az64
)
DISTKEY (client_id)
SORTKEY (order_ts, client_id);

-- COPY examples (fill placeholders before running)
-- COPY analytics_practice.dim_client
-- FROM 's3://<your-bucket>/warehouse/dim_client/'
-- IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
-- REGION 'eu-central-1'
-- FORMAT AS CSV IGNOREHEADER 1 DELIMITER ',' DATEFORMAT 'auto' TIMEFORMAT 'auto';

-- COPY analytics_practice.dim_item
-- FROM 's3://<your-bucket>/warehouse/dim_item/'
-- IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
-- REGION 'eu-central-1'
-- FORMAT AS CSV IGNOREHEADER 1 DELIMITER ',' DATEFORMAT 'auto' TIMEFORMAT 'auto';

-- COPY analytics_practice.fct_order
-- FROM 's3://<your-bucket>/warehouse/fct_order/'
-- IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
-- REGION 'eu-central-1'
-- FORMAT AS CSV IGNOREHEADER 1 DELIMITER ',' DATEFORMAT 'auto' TIMEFORMAT 'auto';

DROP TABLE IF EXISTS analytics_practice.rpt_monthly_sales;
CREATE TABLE analytics_practice.rpt_monthly_sales (
    report_month       DATE ENCODE az64,
    client_city        VARCHAR(80) ENCODE zstd,
    item_category      VARCHAR(60) ENCODE zstd,
    order_count        INTEGER ENCODE az64,
    total_net_amount   DECIMAL(18,2) ENCODE az64,
    avg_order_amount   DECIMAL(18,2) ENCODE az64
)
DISTSTYLE AUTO
SORTKEY (report_month, item_category);

CREATE OR REPLACE PROCEDURE analytics_practice.sp_load_monthly_sales_report(p_year INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM analytics_practice.rpt_monthly_sales
    WHERE EXTRACT(YEAR FROM report_month) = p_year;

    INSERT INTO analytics_practice.rpt_monthly_sales
    SELECT
        DATE_TRUNC('month', fo.order_ts)::DATE AS report_month,
        dc.client_city,
        di.item_category,
        COUNT(DISTINCT fo.order_id) AS order_count,
        SUM(fo.net_amount) AS total_net_amount,
        AVG(fo.net_amount) AS avg_order_amount
    FROM analytics_practice.fct_order fo
    JOIN analytics_practice.dim_client dc
      ON fo.client_id = dc.client_id
    JOIN analytics_practice.dim_item di
      ON fo.item_id = di.item_id
    WHERE EXTRACT(YEAR FROM fo.order_ts) = p_year
    GROUP BY 1,2,3;
END;
$$;

-- Run example
-- SET enable_result_cache_for_session TO OFF;
-- CALL analytics_practice.sp_load_monthly_sales_report(2025);
-- SELECT * FROM analytics_practice.rpt_monthly_sales ORDER BY report_month, total_net_amount DESC LIMIT 100;

-- Compression / table info checks
-- ANALYZE COMPRESSION analytics_practice.fct_order;
-- SELECT "schema", "table", diststyle, sortkey1, size
-- FROM svv_table_info
-- WHERE "schema"='analytics_practice';
