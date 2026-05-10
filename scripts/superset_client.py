import requests

BASE_URL = "http://localhost:8088"
_session = None


def get_session():
    global _session
    if _session:
        return _session
    s = requests.Session()
    resp = s.post(
        f"{BASE_URL}/api/v1/security/login",
        json={"username": "admin", "password": "admin", "provider": "db"},
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]
    csrf_resp = s.get(f"{BASE_URL}/api/v1/security/csrf_token/", headers={"Authorization": f"Bearer {token}"})
    csrf_token = csrf_resp.json()["result"]
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "X-CSRFToken": csrf_token,
        "Referer": BASE_URL,
        "Content-Type": "application/json",
    })
    _session = s
    return s


def api_get(path):
    s = get_session()
    r = s.get(f"{BASE_URL}{path}")
    r.raise_for_status()
    return r.json()


def api_post(path, payload):
    s = get_session()
    r = s.post(f"{BASE_URL}{path}", json=payload)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"POST {path} failed {r.status_code}: {r.text[:300]}")
    return r.json()


def api_put(path, payload):
    s = get_session()
    r = s.put(f"{BASE_URL}{path}", json=payload)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"PUT {path} failed {r.status_code}: {r.text[:300]}")
    return r.json()
