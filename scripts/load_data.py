import os
import sys
import time
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_URI = "postgresql+psycopg2://superset:superset@localhost:5432/healthcare_db"

TABLES = [
    ("dim_hospital", "dim_hospital.csv"),
    ("dim_ward", "dim_ward.csv"),
    ("dim_triage", "dim_triage.csv"),
    ("dim_date", "dim_date.csv"),
    ("fact_ed_visits", "fact_ed_visits.csv"),
]


def wait_for_db(engine, retries=30, delay=5):
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database ready.")
            return
        except Exception:
            print(f"Waiting for database... ({i+1}/{retries})")
            time.sleep(delay)
    raise RuntimeError("Database did not become ready in time.")


def drop_all_tables(engine):
    drop_order = [
        "fact_ed_visits", "dim_ward", "dim_triage", "dim_date", "dim_hospital"
    ]
    with engine.connect() as conn:
        for table in drop_order:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        conn.commit()


def load_table(engine, table_name, csv_file):
    path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(path):
        from data.generate_data import generate_all
        print("CSVs not found. Generating data...")
        generate_all(DATA_DIR)

    df = pd.read_csv(path)

    date_cols = [c for c in df.columns if "time" in c or "date" in c.lower()]
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except Exception:
            pass

    df.to_sql(table_name, engine, if_exists="append", index=False, method="multi", chunksize=5000)
    count = pd.read_sql(f"SELECT COUNT(*) as n FROM {table_name}", engine).iloc[0]["n"]
    print(f"  {table_name}: {count:,} rows loaded")
    return count


def main():
    engine = create_engine(DB_URI)
    wait_for_db(engine)

    print("Dropping existing tables...")
    drop_all_tables(engine)

    print("\nLoading tables...")
    for table_name, csv_file in TABLES:
        load_table(engine, table_name, csv_file)

    print("\nAll tables loaded successfully.")


if __name__ == "__main__":
    main()
