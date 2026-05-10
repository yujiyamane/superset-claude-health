import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_post

HEALTHCARE_DB_URI = "postgresql+psycopg2://superset:superset@postgres:5432/healthcare_db"

TABLES = ["dim_hospital", "dim_ward", "dim_triage", "dim_date", "fact_ed_visits"]


def get_or_create_database():
    existing = api_get("/api/v1/database/")
    for db in existing.get("result", []):
        if "healthcare" in db.get("database_name", "").lower():
            print(f"  Database already exists: id={db['id']}")
            return db["id"]

    payload = {
        "database_name": "healthcare_db",
        "sqlalchemy_uri": HEALTHCARE_DB_URI,
        "expose_in_sqllab": True,
        "allow_run_async": True,
        "allow_dml": False,
        "allow_file_upload": False,
    }
    result = api_post("/api/v1/database/", payload)
    db_id = result["id"]
    print(f"  Database created: id={db_id}")
    return db_id


def get_or_create_dataset(db_id, table_name):
    existing = api_get("/api/v1/dataset/")
    for ds in existing.get("result", []):
        if ds.get("table_name") == table_name:
            print(f"  Dataset already exists: {table_name} id={ds['id']}")
            return ds["id"]

    payload = {
        "database": db_id,
        "table_name": table_name,
        "schema": "public",
    }
    result = api_post("/api/v1/dataset/", payload)
    ds_id = result["id"]
    print(f"  Dataset created: {table_name} id={ds_id}")
    return ds_id


def main():
    print("Setting up Superset database connection...")
    db_id = get_or_create_database()

    print("\nCreating datasets...")
    dataset_ids = {}
    for table in TABLES:
        dataset_ids[table] = get_or_create_dataset(db_id, table)

    print(f"\nDone. Dataset IDs: {dataset_ids}")
    return dataset_ids


if __name__ == "__main__":
    main()
