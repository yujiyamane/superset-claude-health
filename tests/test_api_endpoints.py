import pytest
import requests

BASE_URL = "http://localhost:8088"

@pytest.fixture(scope="module")
def auth_token():
    resp = requests.post(
        f"{BASE_URL}/api/v1/security/login",
        json={"username": "admin", "password": "admin", "provider": "db"}
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]

@pytest.fixture(scope="module")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

def test_superset_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200

def test_list_dashboards(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dashboard/", headers=headers)
    assert resp.status_code == 200

def test_list_datasets(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dataset/", headers=headers)
    assert resp.status_code == 200

def test_list_charts(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/chart/", headers=headers)
    assert resp.status_code == 200

def test_rls_endpoint_exists(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/rowlevelsecurity/", headers=headers)
    assert resp.status_code in [200, 401, 403]

def test_security_roles_endpoint(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/security/roles/", headers=headers)
    assert resp.status_code == 200
