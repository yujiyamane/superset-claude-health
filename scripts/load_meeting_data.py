import os
import sys
import time
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_URI = "postgresql+psycopg2://superset:superset@localhost:5432/healthcare_db"
SCHEMA_PATH = os.path.join(DATA_DIR, "meeting_schema.sql")
CSV_PATH = os.path.join(DATA_DIR, "meeting_bookings.csv")


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


def apply_schema(engine):
    with open(SCHEMA_PATH) as f:
        sql = f.read()
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS meeting_bookings CASCADE"))
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("Schema applied.")


def load_csv(engine):
    if not os.path.exists(CSV_PATH):
        from data.generate_meeting_data import generate_all
        print("CSV not found, generating...")
        generate_all(DATA_DIR)

    df = pd.read_csv(CSV_PATH)
    df["start_datetime"] = pd.to_datetime(df["start_datetime"])
    df["end_datetime"] = pd.to_datetime(df["end_datetime"])
    df["start_date"] = pd.to_datetime(df["start_date"]).dt.date

    df.to_sql("meeting_bookings", engine, if_exists="append", index=False, method="multi", chunksize=5000)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM meeting_bookings", engine).iloc[0]["n"]
    print(f"meeting_bookings: {count:,} rows loaded")
    return count


def main():
    engine = create_engine(DB_URI)
    wait_for_db(engine)
    apply_schema(engine)
    load_csv(engine)
    print("Done.")


if __name__ == "__main__":
    main()
