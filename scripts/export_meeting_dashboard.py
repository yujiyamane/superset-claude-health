import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, get_session

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "superset", "dashboards")
EXPORT_FILE = os.path.join(EXPORT_DIR, "meeting_room_utilisation.json")
BASE_URL = "http://localhost:8088"


def get_meeting_dashboard_id():
    data = api_get("/api/v1/dashboard/")
    for d in data.get("result", []):
        if "Meeting" in d.get("dashboard_title", ""):
            return d["id"]
    raise RuntimeError("Meeting dashboard not found.")


def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)

    dash_id = get_meeting_dashboard_id()
    print(f"Exporting dashboard id={dash_id}...")

    s = get_session()
    r = s.get(f"{BASE_URL}/api/v1/dashboard/export/", params={"q": f"[{dash_id}]"})

    if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/zip"):
        zip_path = EXPORT_FILE.replace(".json", ".zip")
        with open(zip_path, "wb") as f:
            f.write(r.content)
        print(f"Exported (zip): {zip_path}")
    else:
        detail = api_get(f"/api/v1/dashboard/{dash_id}")
        with open(EXPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(detail, f, indent=2, default=str)
        print(f"Exported (json): {EXPORT_FILE}")


if __name__ == "__main__":
    main()
