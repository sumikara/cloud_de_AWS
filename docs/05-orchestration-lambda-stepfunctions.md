# Orchestration Notes — Lambda + Step Functions

This document is the index for the data quality orchestration module.

## Main implementation runbook
- `codes/05-Lambda-StepFunctions-DataQuality.md`

## State machine template
- `templates/stepfunctions-redshift-dq.asl.json`

## Lambda sample
- `lambda/athena_iceberg_quality.py`

## Coverage
- Lambda JSON parsing and structured responses
- Optional Athena Iceberg `SELECT/UPDATE/SELECT` pattern
- Step Functions orchestration with pass/fail `Choice`
- Sanitized examples (no real ARNs/users/passwords/endpoints)
