import pytest
import requests
import psycopg2

BASE_URL = "http://localhost:8088"
META_DB = "postgresql://superset:superset@localhost:5432/superset_meta"


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


@pytest.fixture(scope="module")
def meta_conn():
    conn = psycopg2.connect(META_DB)
    yield conn
    conn.close()


def test_rls_rules_exist(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/rowlevelsecurity/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 2


def test_lhd_manager_role_exists(meta_conn):
    with meta_conn.cursor() as cur:
        cur.execute("SELECT name FROM ab_role WHERE name = 'LHD_Manager'")
        row = cur.fetchone()
    assert row is not None, "LHD_Manager role not found in database"


def test_ward_nurse_role_exists(meta_conn):
    with meta_conn.cursor() as cur:
        cur.execute("SELECT name FROM ab_role WHERE name = 'Ward_Nurse'")
        row = cur.fetchone()
    assert row is not None, "Ward_Nurse role not found in database"
