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


def test_meeting_dashboard_exists(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dashboard/", headers=headers)
    dashboards = resp.json()["result"]
    names = [d["dashboard_title"] for d in dashboards]
    assert any("Meeting" in n for n in names)


def test_meeting_dashboard_has_charts(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dashboard/", headers=headers)
    dashboards = resp.json()["result"]
    meeting = [d for d in dashboards if "Meeting" in d["dashboard_title"]][0]
    dash_id = meeting["id"]
    charts_resp = requests.get(f"{BASE_URL}/api/v1/dashboard/{dash_id}/charts", headers=headers)
    slices = charts_resp.json().get("result", [])
    assert len(slices) >= 12


def test_meeting_dashboard_has_filters(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dashboard/", headers=headers)
    dashboards = resp.json()["result"]
    meeting = [d for d in dashboards if "Meeting" in d["dashboard_title"]][0]
    dash_id = meeting["id"]
    detail = requests.get(f"{BASE_URL}/api/v1/dashboard/{dash_id}", headers=headers)
    json_meta = detail.json()["result"].get("json_metadata", "{}")
    assert "native_filter_configuration" in json_meta or "filter" in str(json_meta).lower()
