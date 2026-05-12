import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_put

HEADER_HTML = (
    '<div style="background:#002664;padding:8px 20px;margin:-16px -16px 0 -16px;'
    'border-bottom:4px solid #630019;">'
    '<span style="color:white;font-size:14px;font-weight:600;">Meeting Room Utilisation</span>'
    '</div>'
)

FOOTER_HTML = (
    '<div style="background:#002664;padding:6px 20px;margin:0 -16px -16px -16px;'
    'display:flex;justify-content:space-between;color:white;font-size:11px;">'
    '<span>Developed by Data Analytics Division</span>'
    '<span>Data Last Refreshed: 2026/05/12</span>'
    '</div>'
)

KPI_ORDER = ["total bookings", "total hours", "average booking duration", "utilisation rate"]
DONUT_ORDER = ["# of bookings by floor level", "# of bookings by time", "# of bookings by day of week"]


def get_dashboard_id():
    data = api_get("/api/v1/dashboard/")
    for d in data.get("result", []):
        if "Meeting" in d.get("dashboard_title", ""):
            return d["id"]
    raise RuntimeError("Meeting dashboard not found")


def vt(ch):
    return ch.get("form_data", {}).get("viz_type", "").lower()


def classify(charts):
    kpis, donuts = [], []
    heatmap = floor_bar = combo = room_bar = util_room = timeseries = None

    for ch in charts:
        name = ch.get("slice_name", "").lower()
        v = vt(ch)
        if "big_number" in v:
            kpis.append(ch)
        elif "pie" in v:
            donuts.append(ch)
        elif "heatmap" in v:
            heatmap = ch
        elif "heat" in name:
            heatmap = ch
        elif "floor" in name and ("bar" in v or "dist_bar" in v or "echarts_timeseries_bar" in v):
            floor_bar = ch
        elif "duration" in name and ("day" in name or "week" in name):
            combo = ch
        elif "mixed" in v and combo is None:
            combo = ch
        elif "date" in name:
            timeseries = ch
        elif "utilisation" in name and "room" in name:
            util_room = ch
        elif "room" in name:
            room_bar = ch

    if floor_bar is None:
        for ch in charts:
            name = ch.get("slice_name", "").lower()
            v = vt(ch)
            if "floor" in name and "pie" not in v and ch not in kpis and ch not in donuts:
                if heatmap and ch["id"] == heatmap["id"]:
                    continue
                floor_bar = ch
                break

    if timeseries is None:
        for ch in charts:
            name = ch.get("slice_name", "").lower()
            v = vt(ch)
            if "date" in name or ("line" in v or "area" in v or "timeseries" in v):
                if ch not in kpis and ch not in donuts and ch is not heatmap and ch is not floor_bar and ch is not combo:
                    timeseries = ch
                    break

    return kpis, donuts, heatmap, floor_bar, combo, room_bar, util_room, timeseries


def sort_kpis(kpis):
    ordered = []
    for target in KPI_ORDER:
        for ch in kpis:
            if target in ch.get("slice_name", "").lower() and ch not in ordered:
                ordered.append(ch)
                break
    for ch in kpis:
        if ch not in ordered:
            ordered.append(ch)
    return ordered


def sort_donuts(donuts):
    ordered = []
    for target in DONUT_ORDER:
        for ch in donuts:
            if target == ch.get("slice_name", "").lower() and ch not in ordered:
                ordered.append(ch)
                break
    for ch in donuts:
        if ch not in ordered:
            ordered.append(ch)
    return ordered


def chart_block(key, ch, width, height):
    eid = f"CHART-{key}"
    return eid, {
        "type": "CHART",
        "id": eid,
        "children": [],
        "meta": {"chartId": ch["id"], "height": height, "sliceName": ch.get("slice_name", ""), "width": width},
    }


def row_block(row_id, children_ids):
    return {
        "type": "ROW",
        "id": row_id,
        "children": children_ids,
        "meta": {"background": "BACKGROUND_TRANSPARENT"},
    }


def markdown_block(md_id, content, width, height):
    return {
        "type": "MARKDOWN",
        "id": md_id,
        "children": [],
        "meta": {"code": content, "height": height, "width": width},
    }


def build_position_json(charts):
    kpis, donuts, heatmap, floor_bar, combo, room_bar, util_room, timeseries = classify(charts)
    kpis = sort_kpis(kpis)
    donuts = sort_donuts(donuts)

    positions = {
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
        "HEADER_ID": {"type": "HEADER", "id": "HEADER_ID", "meta": {"text": "Meeting Room Utilisation"}},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": []},
    }
    grid_rows = []

    positions["MARKDOWN-header"] = markdown_block("MARKDOWN-header", HEADER_HTML, 12, 6)
    positions["ROW-header"] = row_block("ROW-header", ["MARKDOWN-header"])
    grid_rows.append("ROW-header")

    row1 = []
    for i, ch in enumerate(kpis[:4]):
        eid, blk = chart_block(f"kpi{i+1}", ch, 3, 16)
        positions[eid] = blk
        row1.append(eid)
    if row1:
        positions["ROW-1"] = row_block("ROW-1", row1)
        grid_rows.append("ROW-1")

    row2 = []
    for i, ch in enumerate(donuts[:3]):
        eid, blk = chart_block(f"donut{i+1}", ch, 3, 32)
        positions[eid] = blk
        row2.append(eid)
    if heatmap:
        eid, blk = chart_block("hmap", heatmap, 3, 32)
        positions[eid] = blk
        row2.append(eid)
    if row2:
        positions["ROW-2"] = row_block("ROW-2", row2)
        grid_rows.append("ROW-2")

    row3 = []
    for key, ch, w in [("floorbar", floor_bar, 4), ("combo", combo, 4), ("roombar", room_bar, 4)]:
        if ch:
            eid, blk = chart_block(key, ch, w, 32)
            positions[eid] = blk
            row3.append(eid)
    if row3:
        positions["ROW-3"] = row_block("ROW-3", row3)
        grid_rows.append("ROW-3")

    if timeseries:
        eid, blk = chart_block("ts", timeseries, 12, 28)
        positions[eid] = blk
        positions["ROW-4"] = row_block("ROW-4", [eid])
        grid_rows.append("ROW-4")

    positions["MARKDOWN-footer"] = markdown_block("MARKDOWN-footer", FOOTER_HTML, 12, 6)
    positions["ROW-footer"] = row_block("ROW-footer", ["MARKDOWN-footer"])
    grid_rows.append("ROW-footer")

    positions["GRID_ID"]["children"] = grid_rows
    return positions


def main():
    dash_id = get_dashboard_id()
    detail = api_get(f"/api/v1/dashboard/{dash_id}")
    json_meta = json.loads(detail.get("result", {}).get("json_metadata", "{}"))
    json_meta["color_scheme"] = "nsw_navy"
    json_meta["label_colors"] = {}

    charts = api_get(f"/api/v1/dashboard/{dash_id}/charts").get("result", [])
    print(f"Laying out {len(charts)} charts for dashboard id={dash_id}.")

    position_json = build_position_json(charts)
    rows = position_json["GRID_ID"]["children"]
    print(f"Built {len(rows)} rows: {rows}")

    api_put(f"/api/v1/dashboard/{dash_id}", {
        "position_json": json.dumps(position_json),
        "json_metadata": json.dumps(json_meta),
    })
    print("Layout updated.")


if __name__ == "__main__":
    main()
