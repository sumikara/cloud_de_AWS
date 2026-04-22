# Part 5 — Data Quality Orchestration with AWS Lambda and Step Functions

## 0) Objective summary
This module adds orchestration and automated data quality checks to the pipeline. It demonstrates: (1) Lambda parsing and logging JSON inputs, (2) optional Athena Iceberg DML flow (`SELECT`, `UPDATE`, verification `SELECT`), and (3) Step Functions orchestrating multi-step Redshift checks (`select → update → select → decision`) with pass/fail outcome.

---

## 1) Architecture view

```text
Local PC → SSO/CLI → S3 / EC2 / Glue / Athena / Redshift / RDS / DynamoDB
                                │
                                ├─ Lambda (data quality actions)
                                └─ Step Functions (workflow orchestration)
```

---

## 2) Task mapping

## 2.1 Lambda task (JSON parsing + logs)
- Create Lambda with naming mask: `<your_name>_<purpose>`.
- Parse test event JSON.
- Return structured response (`statusCode`, `body`) and log key fields.

## 2.2 Optional Lambda + Athena task
- Run `SELECT ... LIMIT` on an Iceberg table.
- Run `UPDATE` on the same table.
- Run verification `SELECT` and print row(s) to logs.

> Note: UPDATE is supported for Iceberg tables, not default non-transactional table formats.

## 2.3 Step Functions task
- Invoke Lambda 1: initial test/select.
- Invoke Lambda 2: update row.
- Invoke Lambda 3: final test/select.
- Use `Choice` state:
  - if tests pass → `Succeed`
  - else → `Fail`

---

## 3) IAM and networking requirements

- Attach one execution role with least privilege for Lambda and Step Functions.
- For Redshift connectivity from Lambda:
  - Lambda must be inside the same VPC path (subnet/security rules) that can reach Redshift.
  - Add required dependency layer (for example, `redshift_connector`) if not bundled.
- Store credentials/secrets outside code (Secrets Manager or environment placeholders).

---

## 4) Athena Iceberg Lambda pattern (sanitized)

```python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    table_name = event.get("table_name", "<iceberg_db>.<iceberg_table>")
    target_id = int(event.get("target_id", 1))
    new_age = int(event.get("new_age", 37))

    steps = [
        {"step": "select_limit", "query": f"SELECT * FROM {table_name} LIMIT 10"},
        {"step": "update_row", "query": f"UPDATE {table_name} SET age = {new_age} WHERE id = {target_id}"},
        {"step": "select_updated_row", "query": f"SELECT * FROM {table_name} WHERE id = {target_id}"},
    ]

    for s in steps:
        logger.info("[ATHENA] Running query: %s", s["query"])

    logger.info("[DONE] Steps executed: %s", json.dumps(steps))

    return {
        "statusCode": 200,
        "body": json.dumps({"ok": True, "steps": steps})
    }
```

---

## 5) Redshift Lambda pattern (split by responsibility)

### 5.1 First select Lambda (initial check)
- query target table with `LIMIT`
- return `{"status":"OK","rows":[...]}`

### 5.2 Update Lambda
- update a row by key (`id`, `new_value` from event)
- commit transaction
- return updated row + `status`

### 5.3 Final select Lambda (verification)
- select by key
- compare actual value with expected
- return `SUCCESS` or `FAIL`

Implementation rule:
- no hardcoded credentials in source.
- use placeholders or secret references.

---

## 6) Step Functions state machine (practical)

Reference file:
- `templates/stepfunctions-redshift-dq.asl.json`

Execution path:
1. `InitialSelect`
2. `UpdateRow`
3. `FinalSelect`
4. `CheckResults` (Choice)
5. `Success` or `Fail`

---

## 7) Parsing and observability best practices

- Log query intent and row counts (not secrets).
- Include `execution_id`/`request_id` in logs.
- Emit uniform status payloads (`OK`, `SUCCESS`, `FAIL`).
- Keep response body short and structured JSON.

---

## 8) Common failure points and fixes

- **Timeout on Redshift connect**
  - check VPC/subnet/security rules for Lambda.
- **Dependency import errors**
  - verify Lambda layer package compatibility.
- **Athena UPDATE failure**
  - ensure table is Iceberg and workgroup/output location configured.
- **Step Function fails on Choice**
  - verify JSON paths in `Variable` match Lambda output structure.

---

## 9) What was sanitized from raw notes

- real ARNs, account numbers, usernames, passwords, endpoints.
- organization-specific role names and labels.
- duplicated long logs replaced by curated patterns.

---

## 10) Report evidence checklist

1. Lambda test event and parsed response.
2. CloudWatch logs showing select/update/select pattern.
3. Step Functions graph and one successful execution.
4. One failed execution example (for validation of Choice + Fail path).
5. Short explanation of IAM + VPC + dependency integration.
