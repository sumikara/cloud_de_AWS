# Part 3 — Redshift Analytics Delivery (Public, Practical, Portfolio Version)

## 0) One-paragraph objective summary
This section turns a data-lake pipeline into an end-to-end analytics product on Amazon Redshift: connect securely through an EC2 jump host (SSH tunnel), load at least three curated tables from S3 using `COPY`, evaluate compression/distribution/sort design, implement a reporting stored procedure, compare query plans and timing before/after optimization, and optionally expose report data to BI tools. The original notes were theoretical due to temporary service constraints; this runbook converts them into practical CLI/SQL/click-path steps while masking all confidential details.

---

## 1) Bird’s-eye view (why each service exists)

- **S3**: source landing + curated zone for Redshift loads
- **Glue Catalog**: metadata layer used by Athena and Spectrum
- **Athena**: early profiling and data-shape validation
- **EC2**: secure bridge host for private Redshift access
- **Redshift**: MPP warehouse for joins, KPI logic, and reporting
- **Redshift Spectrum**: query S3 data externally when needed
- **Power BI (optional)**: final visualization layer

This part is where “stored files” become “business-ready aggregated output”.

---

## 2) Short architecture diagram

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
```

Task 3 operational path:

```text
Local PC
  └─ SSH tunnel (via EC2 jump host)
      └─ Redshift (private endpoint)
          ├─ COPY from S3 (3+ tables)
          ├─ Encoding + DISTKEY + SORTKEY tuning
          ├─ Stored procedure report load
          ├─ UNLOAD to S3 (optional)
          └─ Spectrum external schema/table (optional)
```

---

## 3) Artifact mapping (which file type for what purpose)

| Purpose | Suggested file | Extension |
|---|---|---|
| Step-by-step runbook | `codes/03-Redshift.md` | `.md` |
| Executable Redshift SQL pipeline | `sql/redshift/03_report_pipeline.sql` | `.sql` |
| COPY/load parameter packs (optional) | `params/redshift-copy.json` | `.json` |
| Infra templates (if provisioning infra by code) | `templates/*.yaml` | `.yaml` |
| Automation wrappers (optional) | `scripts/redshift_runner.py` | `.py` |

Together these files provide a reproducible portfolio flow: narrative + executable SQL + optional automation.

---

## 4) Practical setup: convert theory into executable steps

## 4.1 Console click path (secure connectivity)

1. Open **EC2 Console** (region: `eu-central-1`).
2. Confirm jump host is running (Amazon Linux 2023, small instance size).
3. Open **Redshift Console** and verify cluster status is `Available`.
4. Confirm Redshift is private (no public inbound SQL endpoint).
5. In **Security Groups**, ensure only required inbound/outbound rules exist.
6. In **IAM**, confirm Redshift has an attached S3-read role for `COPY`.

## 4.2 EC2 commands (client readiness)

```bash
sudo dnf update -y
sudo dnf install -y postgresql15.x86_64 postgresql15-server
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl enable --now postgresql
sudo systemctl status postgresql
```

## 4.3 SSH tunnel from local machine

```bash
ssh -i "<path>/<jump-host-key>.pem" -N -L 5439:<redshift-private-endpoint>:5439 ec2-user@<jump-host-public-ip>
```

## 4.4 Redshift connection test from local machine

```bash
psql -h 127.0.0.1 -p 5439 -U <rs_user_xx> -d dev
```

---

## 5) Load design (minimum 3-table analytical model)

Use a clean, neutral schema and table set:
- `analytics_practice.dim_client`
- `analytics_practice.dim_item`
- `analytics_practice.fct_order`

Practical SQL implementation is in:
- `sql/redshift/03_report_pipeline.sql`

### 5.1 COPY pattern (public-safe template)

```sql
COPY analytics_practice.fct_order
FROM 's3://<your-bucket>/warehouse/fct_order/'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
REGION 'eu-central-1'
FORMAT AS CSV
IGNOREHEADER 1
DELIMITER ','
DATEFORMAT 'auto'
TIMEFORMAT 'auto';
```

Repeat the same pattern for dimensions.

---

## 6) Compression, distribution, and sort-key analysis

## 6.1 Identify current compression (default table)

```sql
SELECT "column", type, encoding
FROM pg_table_def
WHERE schemaname = 'analytics_practice'
  AND tablename = 'fct_order';
```

## 6.2 Build comparison tables

- `fct_order_defaultcomp`: default encodings
- `fct_order_withoutcomp`: force `ENCODE RAW`
- `fct_order_analyzedcomp`: apply recommendation from `ANALYZE COMPRESSION`

```sql
ANALYZE COMPRESSION analytics_practice.fct_order_withoutcomp;
```

## 6.3 Compare table size

```sql
SELECT "schema", "table", size, diststyle, sortkey1
FROM svv_table_info
WHERE "schema"='analytics_practice'
  AND "table" IN ('fct_order_defaultcomp','fct_order_withoutcomp','fct_order_analyzedcomp')
ORDER BY "table";
```

Expected interpretation:
- `withoutcomp` is typically the largest.
- `analyzedcomp` is typically smaller and more I/O-efficient.

---

## 7) Stored procedure + report load

The stored procedure in `sql/redshift/03_report_pipeline.sql`:
- joins 3 tables,
- aggregates monthly KPI metrics,
- writes to `analytics_practice.rpt_monthly_sales`.

Execution:

```sql
SET enable_result_cache_for_session TO OFF;
CALL analytics_practice.sp_load_monthly_sales_report(2025);
SELECT *
FROM analytics_practice.rpt_monthly_sales
ORDER BY report_month, total_net_amount DESC
LIMIT 100;
```

---

## 8) BEFORE vs AFTER optimization (how to document evidence)

## 8.1 BEFORE
- Run report query on default distribution/sort design.
- Ignore first run (warm-up effects).
- Record execution times and `EXPLAIN` plan text.

## 8.2 AFTER
- Apply join-aware `DISTKEY` and filter-aware `SORTKEY`.
- Re-run same query and collect same metrics.

## 8.3 What to compare
- Plan operators (`DS_DIST_NONE` vs redistribution-heavy operations)
- Scan behavior (more pruning with sort/zone-map benefit)
- End-to-end latency reduction

Why first execution is not a fair baseline:
- cache warming + metadata warming can mask true engine cost.

---

## 9) Spectrum and S3 tiering (optional but recommended)

## 9.1 Create external schema

```sql
CREATE EXTERNAL SCHEMA IF NOT EXISTS analytics_practice_ext
FROM DATA CATALOG
DATABASE 'glue_db_xx'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-spectrum-role>';
```

## 9.2 Partition strategy
- Export to S3 with monthly folders, e.g. `sale_month=2025-01`.
- Create external table partitioned by `sale_month`.
- Add partitions and validate with row-count reconciliation query.

## 9.3 Internal vs external count check

```sql
WITH internal_count AS (
    SELECT COUNT(*) AS cnt FROM analytics_practice.fct_order
),
external_count AS (
    SELECT COUNT(*) AS cnt FROM analytics_practice_ext.ext_fct_order_partitioned
)
SELECT
    i.cnt AS internal_rows,
    e.cnt AS external_rows,
    (i.cnt - e.cnt) AS diff,
    CASE WHEN i.cnt = e.cnt THEN 'SUCCESS' ELSE 'CHECK_REQUIRED' END AS status
FROM internal_count i
CROSS JOIN external_count e;
```

---

## 10) Power BI integration (optional)

Practical route:
1. Install Redshift ODBC/JDBC driver locally.
2. Keep SSH tunnel active (`localhost:5439`).
3. In Power BI Desktop → **Get Data** → **Amazon Redshift**.
4. Connect to `127.0.0.1:5439`, database `dev`.
5. Load report table (`analytics_practice.rpt_monthly_sales`).

Lower-cost alternative:
- Query Parquet files from S3 via Athena when interactive speed is less critical.

---

## 11) Removed / transformed content and why

- **Org-specific names, real endpoints, account IDs, ARNs, bucket names, personal identities**
  - Removed for public security hygiene.
- **Confidential statement blocks copied verbatim**
  - Replaced by practical, reusable technical steps.
- **Student-specific schema and table names**
  - Renamed to neutral portfolio-safe names.
- **Long repetitive prose**
  - Replaced with command-oriented checklists and executable SQL.

---

## 12) Outcome of this section

After completing this part, the portfolio demonstrates:
- secure private Redshift access,
- controlled S3-to-Redshift ingestion,
- measurable performance tuning methodology,
- procedure-driven reporting,
- optional external table and BI integration paths.

That makes the project a complete “lake-to-warehouse-to-report” data engineering practice track.
