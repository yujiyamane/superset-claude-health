"""Add logo markdown component and native filters to the ED Performance Dashboard."""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_put, get_session

DASHBOARD_ID = 1
DASHBOARD_TITLE = "ED Performance Dashboard"

LOGO_HTML = """<div style="display:flex;align-items:center;gap:20px;padding:6px 12px;border-bottom:3px solid #002664;margin-bottom:4px;">
  <svg width="52" height="68" viewBox="0 0 200 260" xmlns="http://www.w3.org/2000/svg">
    <path d="M100 8 C155 35 178 88 168 130 C155 175 132 198 100 215 C68 198 45 175 32 130 C22 88 45 35 100 8Z" fill="#8B0000"/>
    <path d="M100 8 C98 70 85 150 100 215 C115 150 102 70 100 8Z" fill="white" opacity="0.25"/>
    <path d="M80 50 C60 80 55 110 65 140" fill="none" stroke="white" stroke-width="6" stroke-linecap="round" opacity="0.4"/>
  </svg>
  <div>
    <div style="font-size:38px;font-weight:900;color:#002664;line-height:1;letter-spacing:-1px;font-family:Arial,sans-serif;">AIxBI</div>
    <div style="font-size:15px;font-weight:700;color:#002664;letter-spacing:3px;font-family:Arial,sans-serif;">GOVERNMENT</div>
  </div>
  <div style="margin-left:auto;text-align:right;">
    <div style="font-size:11px;color:#666;font-family:Arial,sans-serif;">NSW Emergency Department Analytics</div>
    <div style="font-size:11px;color:#666;font-family:Arial,sans-serif;">FY2024-25 · FY2025-26 · 208,955 Presentations</div>
  </div>
</div>"""


def build_native_filters(chart_ids: dict) -> list:
    # Chart IDs by dataset
    # Dataset 5 (fact_ed_visits): all except LHD Comparison (12) and Heatmap (8)
    fact_charts = [
        chart_ids["Total Presentations"],
        chart_ids["Average Wait Time (min)"],
        chart_ids["Average LOS (min)"],
        chart_ids["4-Hour Rule Compliance %"],
        chart_ids["4-Hour Breach Rate"],
        chart_ids["Departure Status Distribution"],
        chart_ids["Monthly Presentation Trend"],
        chart_ids["Presentations by Hospital"],
        chart_ids["Triage Category Distribution"],
        chart_ids["Wait Time by Triage Category"],
    ]
    lhd_charts = [chart_ids["LHD Comparison"]]
    heatmap_charts = [chart_ids["Hourly Presentation Heatmap"]]
    all_charts = list(chart_ids.values())

    def scope(excluded=None):
        return {"rootPath": ["ROOT_ID"], "excluded": excluded or []}

    filters = [
        {
            "id": "NATIVE_FILTER-time",
            "type": "NATIVE_FILTER",
            "name": "Date Range",
            "filterType": "filter_time",
            "targets": [{"datasetId": 5, "column": {"name": "arrival_time"}}],
            "defaultDataMask": {"filterState": {"value": None}},
            "controlValues": {"defaultView": "Last year"},
            "cascadeParentIds": [],
            "scope": scope(),
            "chartsInScope": fact_charts + heatmap_charts,
            "description": "Filter by patient arrival date",
        },
        {
            "id": "NATIVE_FILTER-lhd",
            "type": "NATIVE_FILTER",
            "name": "LHD",
            "filterType": "filter_select",
            "targets": [{"datasetId": 6, "column": {"name": "lhd_name"}}],
            "defaultDataMask": {"filterState": {"value": None}},
            "controlValues": {
                "enableEmptyFilter": False,
                "defaultToFirstItem": False,
                "multiSelect": True,
                "searchAllOptions": True,
                "inverseSelection": False,
            },
            "cascadeParentIds": [],
            "scope": scope(),
            "chartsInScope": lhd_charts,
            "description": "Filter by Local Health District",
        },
        {
            "id": "NATIVE_FILTER-triage",
            "type": "NATIVE_FILTER",
            "name": "Triage Category",
            "filterType": "filter_select",
            "targets": [{"datasetId": 5, "column": {"name": "triage_id"}}],
            "defaultDataMask": {"filterState": {"value": None}},
            "controlValues": {
                "enableEmptyFilter": False,
                "defaultToFirstItem": False,
                "multiSelect": True,
                "searchAllOptions": False,
                "inverseSelection": False,
                "sortAscending": True,
            },
            "cascadeParentIds": [],
            "scope": scope(),
            "chartsInScope": fact_charts,
            "description": "ATS triage category (1=Immediate … 5=Non-urgent)",
        },
        {
            "id": "NATIVE_FILTER-breach",
            "type": "NATIVE_FILTER",
            "name": "4-Hour Breach",
            "filterType": "filter_select",
            "targets": [{"datasetId": 5, "column": {"name": "four_hour_breach"}}],
            "defaultDataMask": {"filterState": {"value": None}},
            "controlValues": {
                "enableEmptyFilter": False,
                "defaultToFirstItem": False,
                "multiSelect": False,
                "searchAllOptions": False,
            },
            "cascadeParentIds": [],
            "scope": scope(),
            "chartsInScope": fact_charts,
            "description": "Show breached / compliant presentations only",
        },
        {
            "id": "NATIVE_FILTER-departure",
            "type": "NATIVE_FILTER",
            "name": "Departure Status",
            "filterType": "filter_select",
            "targets": [{"datasetId": 5, "column": {"name": "departure_status"}}],
            "defaultDataMask": {"filterState": {"value": None}},
            "controlValues": {
                "enableEmptyFilter": False,
                "defaultToFirstItem": False,
                "multiSelect": True,
                "searchAllOptions": False,
            },
            "cascadeParentIds": [],
            "scope": scope(),
            "chartsInScope": fact_charts,
            "description": "Discharged / Admitted / Transferred / Did Not Wait / Deceased",
        },
        {
            "id": "NATIVE_FILTER-gender",
            "type": "NATIVE_FILTER",
            "name": "Patient Gender",
            "filterType": "filter_select",
            "targets": [{"datasetId": 5, "column": {"name": "patient_gender"}}],
            "defaultDataMask": {"filterState": {"value": None}},
            "controlValues": {
                "enableEmptyFilter": False,
                "defaultToFirstItem": False,
                "multiSelect": True,
                "searchAllOptions": False,
            },
            "cascadeParentIds": [],
            "scope": scope(),
            "chartsInScope": fact_charts,
            "description": "Filter by patient gender",
        },
        {
            "id": "NATIVE_FILTER-wait",
            "type": "NATIVE_FILTER",
            "name": "Wait Time (min)",
            "filterType": "filter_range",
            "targets": [{"datasetId": 5, "column": {"name": "wait_time_minutes"}}],
            "defaultDataMask": {"filterState": {"value": None}},
            "controlValues": {"enableEmptyFilter": False},
            "cascadeParentIds": [],
            "scope": scope(),
            "chartsInScope": fact_charts,
            "description": "Slide to filter by triage-to-treatment wait time",
        },
        {
            "id": "NATIVE_FILTER-age",
            "type": "NATIVE_FILTER",
            "name": "Patient Age",
            "filterType": "filter_range",
            "targets": [{"datasetId": 5, "column": {"name": "patient_age"}}],
            "defaultDataMask": {"filterState": {"value": None}},
            "controlValues": {"enableEmptyFilter": False},
            "cascadeParentIds": [],
            "scope": scope(),
            "chartsInScope": fact_charts,
            "description": "Slide to filter by patient age range",
        },
    ]
    return filters


def add_logo_to_layout(position_json: dict) -> dict:
    pos = position_json.copy()

    logo_component = {
        "type": "MARKDOWN",
        "id": "MARKDOWN-logo",
        "children": [],
        "meta": {
            "code": LOGO_HTML,
            "height": 12,
            "width": 12,
        },
    }
    logo_row = {
        "type": "ROW",
        "id": "ROW-logo",
        "children": ["MARKDOWN-logo"],
        "meta": {"background": "BACKGROUND_TRANSPARENT"},
    }

    pos["MARKDOWN-logo"] = logo_component
    pos["ROW-logo"] = logo_row

    grid = pos.get("GRID_ID", {})
    children = grid.get("children", [])
    if "ROW-logo" not in children:
        grid["children"] = ["ROW-logo"] + children
    pos["GRID_ID"] = grid
    return pos


def main():
    print("Fetching dashboard state...")
    db = api_get(f"/api/v1/dashboard/{DASHBOARD_ID}")["result"]
    position_json = json.loads(db.get("position_json", "{}"))
    existing_meta = json.loads(db.get("json_metadata", "{}"))

    print("Fetching charts...")
    charts_data = api_get("/api/v1/chart/?q=(page_size:50)")["result"]
    chart_ids = {c["slice_name"]: c["id"] for c in charts_data}
    print(f"  Found {len(chart_ids)} charts")

    print("Adding logo component to layout...")
    new_position = add_logo_to_layout(position_json)

    print("Building native filter configuration...")
    filters = build_native_filters(chart_ids)

    new_meta = {
        **existing_meta,
        "color_scheme": "nswHealth",
        "native_filter_configuration": filters,
        "cross_filters_enabled": True,
    }

    print("Updating dashboard...")
    api_put(f"/api/v1/dashboard/{DASHBOARD_ID}", {
        "position_json": json.dumps(new_position),
        "json_metadata": json.dumps(new_meta),
    })
    print(f"  Done — {len(filters)} filters added, logo injected.")


if __name__ == "__main__":
    main()
