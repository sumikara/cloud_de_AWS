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

    for step in steps:
        logger.info("[ATHENA] Running query: %s", step["query"])

    return {
        "statusCode": 200,
        "body": json.dumps({"ok": True, "steps": steps})
    }
