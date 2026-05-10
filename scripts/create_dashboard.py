import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_post, api_put

DASHBOARD_TITLE = "ED Performance Dashboard"


def get_all_chart_ids():
    data = api_get("/api/v1/chart/")
    return {ch["slice_name"]: ch["id"] for ch in data.get("result", [])}


def dashboard_exists():
    data = api_get("/api/v1/dashboard/")
    for db in data.get("result", []):
        if db.get("dashboard_title") == DASHBOARD_TITLE:
            return db["id"]
    return None


def build_position_json(chart_ids):
    GRID_COLUMN_COUNT = 12

    def chart_meta(chart_id, idx):
        return {
            "type": "CHART",
            "id": f"CHART-{chart_id}",
            "children": [],
            "meta": {
                "chartId": chart_id,
                "height": 50,
                "sliceName": f"Chart {idx}",
                "width": 4,
            },
        }

    charts = list(chart_ids.values())
    rows = []
    for i in range(0, len(charts), 3):
        row_charts = charts[i:i+3]
        row_id = f"ROW-{i}"
        row = {
            "type": "ROW",
            "id": row_id,
            "children": [f"CHART-{cid}" for cid in row_charts],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        rows.append((row_id, row, row_charts))

    positions = {
        "GRID_ID": {
            "type": "GRID",
            "id": "GRID_ID",
            "children": [r[0] for r in rows],
        },
        "HEADER_ID": {
            "type": "HEADER",
            "id": "HEADER_ID",
            "meta": {"text": DASHBOARD_TITLE},
        },
        "ROOT_ID": {
            "type": "ROOT",
            "id": "ROOT_ID",
            "children": ["GRID_ID"],
        },
    }

    for row_id, row, row_charts in rows:
        positions[row_id] = row
        for cid in row_charts:
            positions[f"CHART-{cid}"] = chart_meta(cid, cid)

    return positions


def main():
    print("Getting chart IDs...")
    chart_ids = get_all_chart_ids()
    if not chart_ids:
        print("No charts found. Run create_charts.py first.")
        return None

    print(f"  Found {len(chart_ids)} charts")

    existing_id = dashboard_exists()
    if existing_id:
        print(f"  Dashboard already exists: id={existing_id}")
        return existing_id

    position_json = build_position_json(chart_ids)

    payload = {
        "dashboard_title": DASHBOARD_TITLE,
        "published": True,
        "slug": "ed-performance",
        "position_json": json.dumps(position_json),
        "json_metadata": json.dumps({
            "color_scheme": "supersetColors",
            "expanded_slices": {},
            "refresh_frequency": 0,
            "timed_refresh_immune_slices": [],
            "filter_scopes": {},
            "cross_filters_enabled": True,
        }),
    }

    result = api_post("/api/v1/dashboard/", payload)
    db_id = result["id"]
    print(f"  Dashboard created: id={db_id} with {len(chart_ids)} charts in layout")
    return db_id


if __name__ == "__main__":
    main()
