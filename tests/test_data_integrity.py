import pytest
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def test_generate_data_creates_csvs():
    from data.generate_data import generate_all
    generate_all(DATA_DIR)
    assert os.path.exists(os.path.join(DATA_DIR, "dim_hospital.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "dim_ward.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "dim_triage.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "dim_date.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "fact_ed_visits.csv"))

def test_fact_table_row_count():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    assert len(df) >= 100000

def test_fact_table_has_required_columns():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    required = [
        "visit_id", "hospital_id", "ward_id", "triage_id", "date_id",
        "arrival_time", "wait_time_minutes", "total_los_minutes",
        "four_hour_breach", "patient_age", "patient_gender"
    ]
    for col in required:
        assert col in df.columns

def test_dim_hospital_has_lhd():
    df = pd.read_csv(os.path.join(DATA_DIR, "dim_hospital.csv"))
    assert "lhd_name" in df.columns
    assert df["lhd_name"].nunique() >= 5

def test_triage_categories_1_to_5():
    df = pd.read_csv(os.path.join(DATA_DIR, "dim_triage.csv"))
    assert set(df["triage_category"]) == {1, 2, 3, 4, 5}

def test_no_null_visit_ids():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    assert df["visit_id"].notna().all()

def test_wait_times_are_positive():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    assert (df["wait_time_minutes"] >= 0).all()

def test_four_hour_breach_is_boolean():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    assert df["four_hour_breach"].isin([True, False, 0, 1]).all()
