import pytest
import requests

BASE_URL = "http://localhost:8088"


@pytest.fixture(scope="module")
def headers():
    resp = requests.post(
        f"{BASE_URL}/api/v1/security/login",
        json={"username": "admin", "password": "admin", "provider": "db"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def get_meeting_dashboard_id(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dashboard/", headers=headers)
    for d in resp.json().get("result", []):
        if "Meeting" in d.get("dashboard_title", ""):
            return d["id"]
    return None


def get_charts(headers):
    dash_id = get_meeting_dashboard_id(headers)
    if not dash_id:
        return []
    resp = requests.get(f"{BASE_URL}/api/v1/dashboard/{dash_id}/charts", headers=headers)
    return resp.json().get("result", [])


def test_meeting_charts_count(headers):
    charts = get_charts(headers)
    assert len(charts) >= 13


def test_no_meeting_prefix_in_names(headers):
    charts = get_charts(headers)
    names = [c["slice_name"] for c in charts]
    assert not any(n.startswith("Meeting:") for n in names), \
        f"Charts still have 'Meeting:' prefix: {[n for n in names if n.startswith('Meeting:')]}"


def test_kpi_total_bookings_exists(headers):
    charts = get_charts(headers)
    names = [c["slice_name"] for c in charts]
    assert any("Total Bookings" in n for n in names)


def test_kpi_total_hours_exists(headers):
    charts = get_charts(headers)
    names = [c["slice_name"] for c in charts]
    assert any("Total Hours" in n for n in names)


def test_kpi_avg_duration_exists(headers):
    charts = get_charts(headers)
    names = [c["slice_name"] for c in charts]
    assert any("Average Booking Duration" in n or "Avg" in n for n in names)


def test_kpi_utilisation_exists(headers):
    charts = get_charts(headers)
    names = [c["slice_name"] for c in charts]
    assert any("Utilisation" in n for n in names)


def test_donut_charts_exist(headers):
    charts = get_charts(headers)
    names = [c["slice_name"] for c in charts]
    assert any("Floor Level" in n for n in names)
    assert any("Time" in n for n in names)
    assert any("Day of Week" in n for n in names)


def test_heatmap_exists(headers):
    charts = get_charts(headers)
    names = [c["slice_name"] for c in charts]
    assert any("Heat Map" in n or "Heatmap" in n for n in names)


def test_bar_charts_exist(headers):
    charts = get_charts(headers)
    viz_types = [c.get("form_data", {}).get("viz_type", "") for c in charts]
    bar_count = sum(1 for v in viz_types if "bar" in v.lower())
    assert bar_count >= 3


def test_timeseries_exists(headers):
    charts = get_charts(headers)
    names = [c["slice_name"] for c in charts]
    assert any("Date" in n for n in names)
