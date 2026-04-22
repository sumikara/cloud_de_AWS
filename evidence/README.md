# Evidence Upload Retry Guide

If screenshot upload failed previously, use this folder and upload again with the exact filenames below.

## Recommended filenames
1. `evidence/05_lambda_editor_test_event_saved.png`
2. `evidence/05_lambda_test_response_and_logs.png`
3. `evidence/05_athena_query_result_location_and_upload.png`
4. `evidence/05_lambda_athena_select_update_logs.png`
5. `evidence/05_stepfunctions_execution_graph_custom.png`
6. `evidence/05_reference_architecture_external.png` *(reference only, not execution evidence)*

## Important
- Files 1–5 should be your own account execution evidence.
- File 6 must be labeled as "Reference Architecture" and include source attribution in the report/README.
- Redact any account IDs, ARNs, emails, hostnames, and local paths before commit.

## Optional markdown snippet

```markdown
![Lambda editor + test event](evidence/05_lambda_editor_test_event_saved.png)
![Lambda response + logs](evidence/05_lambda_test_response_and_logs.png)
![Athena result location](evidence/05_athena_query_result_location_and_upload.png)
![Lambda Athena logs](evidence/05_lambda_athena_select_update_logs.png)
![Step Functions execution graph](evidence/05_stepfunctions_execution_graph_custom.png)
![Reference architecture (external source)](evidence/05_reference_architecture_external.png)
```
