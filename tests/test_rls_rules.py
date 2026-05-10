import pytest
import requests

BASE_URL = "http://localhost:8088"

@pytest.fixture(scope="module")
def auth_token():
    resp = requests.post(
        f"{BASE_URL}/api/v1/security/login",
        json={"username": "admin", "password": "admin", "provider": "db"}
    )
    return resp.json()["access_token"]

@pytest.fixture(scope="module")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

def test_rls_rules_exist(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/rowlevelsecurity/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 2

def test_lhd_manager_role_exists(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/security/roles/", headers=headers)
    roles = [r["name"] for r in resp.json()["result"]]
    assert "LHD_Manager" in roles

def test_ward_nurse_role_exists(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/security/roles/", headers=headers)
    roles = [r["name"] for r in resp.json()["result"]]
    assert "Ward_Nurse" in roles
