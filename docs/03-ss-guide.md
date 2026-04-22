# Evidence Guide (Portfolio-Safe)

Use evidence to prove **what you actually built and executed**.

---

## 1) What should be uploaded as evidence

Prefer screenshots from your own AWS account/session for:
- SSO/STS identity check
- S3 bucket + object hierarchy
- Glue crawler result and Athena query output
- EC2 status, SSH session, PostgreSQL service status
- Apache page over public IP
- CloudWatch alarm and SNS subscription
- Redshift query result / table metadata / explain output
- RDS/Aurora connection setup and query output
- DynamoDB create/write/read/delete result
- Lambda test event response + function logs
- Step Functions execution graph (success and failure cases)

---

## 2) Can I use diagrams from the internet?

Short answer: **Not as execution evidence.**

- Internet diagrams are acceptable only as **conceptual architecture references**.
- They do **not** prove your implementation.
- If used, add:
  1. source URL,
  2. "Reference architecture" label,
  3. a separate section from your real execution evidence.

Best practice:
- Keep external diagrams in `docs/references/` (or similar),
- Keep your real execution screenshots in `evidence/`.

---

## 3) Redaction rules before upload

Always hide or crop:
- account IDs
- ARNs
- private endpoints
- usernames/emails
- local machine paths
- tokens/passwords/secrets

If a value is needed for explanation, replace with placeholders like `<account-id>`.

---

## 4) Naming convention for evidence files

Use deterministic names:
- `evidence/01_sso_identity_ok.png`
- `evidence/03_athena_query_result.png`
- `evidence/05_lambda_json_parse_success.png`
- `evidence/06_stepfunctions_redshift_dq_success.png`

This makes report assembly and cross-referencing easier.

---

## 5) Minimum evidence checklist for Part 5 (Lambda + Step Functions)

1. Lambda code screen (sanitized).
2. Lambda test response (`statusCode`, body).
3. CloudWatch function logs with parsed output.
4. Athena/Iceberg query step logs (if optional task implemented).
5. Step Functions execution graph (success).
6. Step Functions execution graph (failure path, if tested).

---

## 6) Conclusion

Use your own screenshots as primary evidence. External architecture images can support explanation, but should never replace implementation proof.
