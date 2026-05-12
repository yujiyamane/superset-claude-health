import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_put


def main():
    data = api_get("/api/v1/dashboard/")
    for d in data.get("result", []):
        if "Meeting" in d.get("dashboard_title", ""):
            dash_id = d["id"]
            detail = api_get(f"/api/v1/dashboard/{dash_id}")
            meta = json.loads(detail.get("result", {}).get("json_metadata", "{}"))
            meta["color_scheme"] = "nsw_navy"
            meta["label_colors"] = {}
            api_put(f"/api/v1/dashboard/{dash_id}", {"json_metadata": json.dumps(meta)})
            print(f"Dashboard {dash_id} colour scheme set to nsw_navy")
            return
    print("Meeting dashboard not found")


if __name__ == "__main__":
    main()
