import pytest
import requests

BASE_URL = "http://localhost:8088"
DATASET_ID = 8


@pytest.fixture(scope="module")
def headers():
    resp = requests.post(
        f"{BASE_URL}/api/v1/security/login",
        json={"username": "admin", "password": "admin", "provider": "db"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def get_calculated_columns(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dataset/{DATASET_ID}", headers=headers)
    resp.raise_for_status()
    return {
        c["column_name"]: c
        for c in resp.json()["result"]["columns"]
        if c.get("expression")
    }


def test_day_sorted_column_exists(headers):
    cols = get_calculated_columns(headers)
    assert "day_sorted" in cols, f"day_sorted column missing. Calculated cols: {list(cols.keys())}"


def test_day_sorted_no_double_quotes(headers):
    cols = get_calculated_columns(headers)
    expr = cols.get("day_sorted", {}).get("expression", "")
    assert "''" not in expr, f"day_sorted has double-quote artifact: {expr[:120]}"


def test_day_sorted_expression_correct(headers):
    cols = get_calculated_columns(headers)
    expr = cols.get("day_sorted", {}).get("expression", "")
    for expected in ["'1 Mon'", "'2 Tue'", "'3 Wed'", "'4 Thu'", "'5 Fri'"]:
        assert expected in expr, f"Expected {expected} in day_sorted expression but got: {expr[:200]}"


def test_hour_sorted_column_exists(headers):
    cols = get_calculated_columns(headers)
    assert "hour_sorted" in cols, f"hour_sorted column missing. Calculated cols: {list(cols.keys())}"


def test_hour_sorted_no_double_quotes(headers):
    cols = get_calculated_columns(headers)
    expr = cols.get("hour_sorted", {}).get("expression", "")
    assert "''" not in expr, f"hour_sorted has double-quote artifact: {expr[:120]}"


def test_hour_sorted_expression_correct(headers):
    cols = get_calculated_columns(headers)
    expr = cols.get("hour_sorted", {}).get("expression", "")
    assert "LPAD" in expr, f"LPAD missing from hour_sorted expression: {expr[:200]}"
    assert "hour_ampm" in expr, f"hour_ampm missing from hour_sorted expression: {expr[:200]}"
    assert "hour_of_day" in expr, f"hour_of_day missing from hour_sorted expression: {expr[:200]}"
