import os
import pytest
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.fixture(scope="module")
def df():
    path = os.path.join(DATA_DIR, "meeting_bookings.csv")
    assert os.path.exists(path), "meeting_bookings.csv not generated yet"
    return pd.read_csv(path)


def test_row_count_above_50k(df):
    assert len(df) >= 50000


def test_date_range(df):
    dates = pd.to_datetime(df["start_date"])
    assert dates.min().year == 2024
    assert dates.max().year == 2026


def test_floor_levels_2_to_9(df):
    assert set(df["floor_level"].unique()) == {2, 3, 4, 5, 6, 7, 8, 9}


def test_floor_level_names_match(df):
    for _, row in df[["floor_level", "floor_level_name"]].drop_duplicates().iterrows():
        assert row["floor_level_name"] == f"Level {row['floor_level']}"


def test_weekdays_only(df):
    valid_days = {"Mon", "Tue", "Wed", "Thu", "Fri"}
    assert set(df["day_of_week"].unique()).issubset(valid_days)


def test_hours_8am_to_5pm(df):
    assert df["hour_of_day"].min() >= 8
    assert df["hour_of_day"].max() <= 17


def test_avg_duration_around_45_mins(df):
    avg = df["duration_minutes"].mean()
    assert 35 <= avg <= 55


def test_no_null_booking_ids(df):
    assert df["booking_id"].notna().all()


def test_no_null_room_names(df):
    assert df["room_name"].notna().all()


def test_room_name_format(df):
    import re
    pattern = r"^\d\.\w\.\d+-S\d+-VC$"
    for name in df["room_name"].unique():
        assert re.match(pattern, name), f"Invalid room name format: {name}"


def test_organizer_names_no_real_orgs(df):
    banned = ["NSW Health", "Ministry of Health", "Corporate Analytics", "eHealth",
              "Hunter New England", "South Western Sydney", "Western Sydney",
              "South Eastern Sydney", "Northern Sydney"]
    for org in banned:
        matches = df["organizer_name"].str.contains(org, case=False, na=False)
        assert not matches.any(), f"Found real org name: {org}"


def test_organizer_count(df):
    assert df["organizer_name"].nunique() >= 100


def test_room_count(df):
    assert df["room_name"].nunique() >= 40


def test_utilisation_rate_range(df):
    rates = df["utilisation_rate"].dropna()
    assert (rates >= 0).all()
    assert (rates <= 100).all()


def test_duration_positive(df):
    assert (df["duration_minutes"] > 0).all()


def test_day_of_week_number_correct(df):
    day_map = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5}
    for _, row in df[["day_of_week", "day_of_week_number"]].drop_duplicates().iterrows():
        assert day_map[row["day_of_week"]] == row["day_of_week_number"]
