import sys
import os
import json
import uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_post, api_put

DASHBOARD_TITLE = "Meeting Room Utilisation"
SLUG = "meeting-room-utilisation"


def get_meeting_chart_ids():
    data = api_get("/api/v1/chart/")
    return {ch["slice_name"]: ch["id"] for ch in data.get("result", []) if "Meeting:" in ch.get("slice_name", "")}


def dashboard_exists():
    data = api_get("/api/v1/dashboard/")
    for d in data.get("result", []):
        if "Meeting" in d.get("dashboard_title", ""):
            return d["id"]
    return None


def build_position_json(chart_ids):
    def cid(name):
        return chart_ids.get(name)

    def chart_block(key, name, col, row, width, height):
        chart_id = cid(name)
        if not chart_id:
            return None, None
        elem_id = f"CHART-{key}"
        return elem_id, {
            "type": "CHART",
            "id": elem_id,
            "children": [],
            "meta": {"chartId": chart_id, "height": height, "sliceName": name, "width": width},
        }

    def row_block(row_id, children_ids):
        return {
            "type": "ROW",
            "id": row_id,
            "children": children_ids,
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }

    positions = {
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
        "HEADER_ID": {"type": "HEADER", "id": "HEADER_ID", "meta": {"text": DASHBOARD_TITLE}},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": []},
    }

    grid_rows = []

    kpi_charts = [
        ("kpi1", "Meeting: Total Bookings", 3, 12),
        ("kpi2", "Meeting: Total Hours Booked", 3, 12),
        ("kpi3", "Meeting: Average Booking Duration", 3, 12),
        ("kpi4", "Meeting: Utilisation Rate", 3, 12),
    ]
    row1_children = []
    for key, name, width, height in kpi_charts:
        eid, block = chart_block(key, name, 0, 0, width, height)
        if eid:
            positions[eid] = block
            row1_children.append(eid)
    if row1_children:
        positions["ROW-1"] = row_block("ROW-1", row1_children)
        grid_rows.append("ROW-1")

    donut_charts = [
        ("donut1", "Meeting: Bookings by Floor Level (Donut)", 4, 30),
        ("donut2", "Meeting: Bookings by Time (Donut)", 4, 30),
        ("donut3", "Meeting: Bookings by Day of Week (Donut)", 4, 30),
    ]
    row2_children = []
    for key, name, width, height in donut_charts:
        eid, block = chart_block(key, name, 0, 0, width, height)
        if eid:
            positions[eid] = block
            row2_children.append(eid)
    if row2_children:
        positions["ROW-2"] = row_block("ROW-2", row2_children)
        grid_rows.append("ROW-2")

    row3_pairs = [
        ("hmap", "Meeting: Booking Heat Map (Peak Times)", 6, 30),
        ("bfloor", "Meeting: Bookings by Floor Level (Bar)", 6, 30),
    ]
    row3_children = []
    for key, name, width, height in row3_pairs:
        eid, block = chart_block(key, name, 0, 0, width, height)
        if eid:
            positions[eid] = block
            row3_children.append(eid)
    if row3_children:
        positions["ROW-3"] = row_block("ROW-3", row3_children)
        grid_rows.append("ROW-3")

    tseid, tsblock = chart_block("tsdate", "Meeting: Bookings by Date", 0, 0, 12, 25)
    if tseid:
        positions[tseid] = tsblock
        positions["ROW-4"] = row_block("ROW-4", [tseid])
        grid_rows.append("ROW-4")

    row5_pairs = [
        ("broom", "Meeting: Bookings by Room", 6, 35),
        ("uroom", "Meeting: Utilisation Rate by Room Name", 6, 35),
    ]
    row5_children = []
    for key, name, width, height in row5_pairs:
        eid, block = chart_block(key, name, 0, 0, width, height)
        if eid:
            positions[eid] = block
            row5_children.append(eid)
    if row5_children:
        positions["ROW-5"] = row_block("ROW-5", row5_children)
        grid_rows.append("ROW-5")

    comboeid, comboblock = chart_block("combo", "Meeting: Bookings & Duration by Day of Week", 0, 0, 12, 30)
    if comboeid:
        positions[comboeid] = comboblock
        positions["ROW-6"] = row_block("ROW-6", [comboeid])
        grid_rows.append("ROW-6")

    positions["GRID_ID"]["children"] = grid_rows
    return positions


def build_native_filters(ds_id):
    def make_filter(name, col, filter_type, target_ds_id):
        fid = f"NATIVE_FILTER-{uuid.uuid4().hex[:8]}"
        return {
            "id": fid,
            "name": name,
            "filterType": filter_type,
            "targets": [{"datasetId": target_ds_id, "column": {"name": col}}],
            "defaultDataMask": {"extraFormData": {}, "filterState": {"value": None}, "ownState": {}},
            "scope": {"rootPath": ["ROOT_ID"], "excluded": []},
            "type": "NATIVE_FILTER",
            "description": "",
            "chartsInScope": [],
            "cascadeParentIds": [],
        }

    return [
        make_filter("Day", "start_date", "filter_time", ds_id),
        make_filter("Hour", "hour_ampm", "filter_select", ds_id),
        make_filter("Organizer Name", "organizer_name", "filter_select", ds_id),
        make_filter("Subject", "subject", "filter_select", ds_id),
        make_filter("Room", "room_name", "filter_select", ds_id),
        make_filter("Floor Level", "floor_level_name", "filter_select", ds_id),
    ]


def get_dataset_id():
    data = api_get("/api/v1/dataset/")
    for ds in data.get("result", []):
        if ds.get("table_name") == "meeting_bookings":
            return ds["id"]
    raise RuntimeError("meeting_bookings dataset not found. Run create_meeting_charts.py first.")


def main():
    existing_id = dashboard_exists()
    if existing_id:
        print(f"Dashboard already exists: id={existing_id}")
        return existing_id

    print("Getting chart IDs...")
    chart_ids = get_meeting_chart_ids()
    print(f"  Found {len(chart_ids)} Meeting charts")

    ds_id = get_dataset_id()

    position_json = build_position_json(chart_ids)
    native_filters = build_native_filters(ds_id)

    json_metadata = {
        "color_scheme": "supersetColors",
        "expanded_slices": {},
        "refresh_frequency": 0,
        "timed_refresh_immune_slices": [],
        "cross_filters_enabled": True,
        "native_filter_configuration": native_filters,
    }

    payload = {
        "dashboard_title": DASHBOARD_TITLE,
        "published": True,
        "slug": SLUG,
        "position_json": json.dumps(position_json),
        "json_metadata": json.dumps(json_metadata),
    }

    result = api_post("/api/v1/dashboard/", payload)
    dash_id = result["id"]

    for chart_id in chart_ids.values():
        api_put(f"/api/v1/chart/{chart_id}", {"dashboards": [dash_id]})

    print(f"Dashboard created: id={dash_id}, {len(chart_ids)} charts linked")
    return dash_id


if __name__ == "__main__":
    main()
