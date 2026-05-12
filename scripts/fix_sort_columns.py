import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_put

DATASET_ID = 8

ALLOWED_COL_FIELDS = {
    "column_name", "verbose_name", "type", "expression", "description",
    "groupby", "filterable", "is_dttm", "python_date_format", "extra", "uuid", "id",
}

CORRECT_EXPRESSIONS = {
    "day_sorted": (
        "CASE WHEN day_of_week='Mon' THEN '1 Mon' "
        "WHEN day_of_week='Tue' THEN '2 Tue' "
        "WHEN day_of_week='Wed' THEN '3 Wed' "
        "WHEN day_of_week='Thu' THEN '4 Thu' "
        "WHEN day_of_week='Fri' THEN '5 Fri' "
        "ELSE day_of_week END"
    ),
    "hour_sorted": "LPAD(CAST(hour_of_day AS VARCHAR), 2, '0') || ' ' || hour_ampm",
}


def filter_col(col):
    return {k: v for k, v in col.items() if k in ALLOWED_COL_FIELDS}


def main():
    detail = api_get(f"/api/v1/dataset/{DATASET_ID}")
    result = detail["result"]
    columns = result["columns"]

    updated = []
    for col in columns:
        name = col.get("column_name", "")
        if name in CORRECT_EXPRESSIONS:
            col = dict(col)
            col["expression"] = CORRECT_EXPRESSIONS[name]
            print(f"  Fixed {name}: {col['expression'][:80]}")
        updated.append(filter_col(col))

    api_put(f"/api/v1/dataset/{DATASET_ID}", {"columns": updated})
    print(f"\nDataset {DATASET_ID} updated with corrected expressions.")


if __name__ == "__main__":
    main()
