import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "superset", "dashboards")
DASHBOARD_TITLE = "ED Performance Dashboard"


def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)

    data = api_get("/api/v1/dashboard/")
    dashboard = None
    for db in data.get("result", []):
        if db.get("dashboard_title") == DASHBOARD_TITLE:
            dashboard = db
            break

    if not dashboard:
        print(f"Dashboard '{DASHBOARD_TITLE}' not found. Run create_dashboard.py first.")
        return

    db_id = dashboard["id"]
    detail = api_get(f"/api/v1/dashboard/{db_id}")
    result = detail.get("result", detail)

    charts = api_get("/api/v1/chart/")
    chart_list = [
        {"id": ch["id"], "slice_name": ch["slice_name"], "viz_type": ch["viz_type"]}
        for ch in charts.get("result", [])
    ]

    export_data = {
        "dashboard_title": result.get("dashboard_title", DASHBOARD_TITLE),
        "slug": result.get("slug", "ed-performance"),
        "published": result.get("published", True),
        "position_json": result.get("position_json", "{}"),
        "metadata": result.get("json_metadata", "{}"),
        "charts": chart_list,
    }

    out_path = os.path.join(EXPORT_DIR, "ed_performance.json")
    with open(out_path, "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"Dashboard exported to: {out_path}")
    print(f"  Charts: {len(chart_list)}")
    return out_path


if __name__ == "__main__":
    main()
