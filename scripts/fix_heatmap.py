import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_put


def get_dashboard_id():
    for d in api_get("/api/v1/dashboard/").get("result", []):
        if "Meeting" in d.get("dashboard_title", ""):
            return d["id"]
    raise RuntimeError("Meeting dashboard not found")


def get_heatmap_chart(dash_id):
    charts = api_get(f"/api/v1/dashboard/{dash_id}/charts").get("result", [])
    for ch in charts:
        if "heat" in ch.get("slice_name", "").lower():
            return ch
    raise RuntimeError("Heatmap chart not found")


def main():
    dash_id = get_dashboard_id()
    ch = get_heatmap_chart(dash_id)
    chart_id = ch["id"]

    detail = api_get(f"/api/v1/chart/{chart_id}")
    result = detail.get("result", {})
    old_params = json.loads(result.get("params", "{}"))

    datasource = old_params.get("datasource", "")
    datasource_id = result.get("datasource_id") or old_params.get("datasource_id")

    fresh_params = {
        "viz_type": "heatmap",
        "datasource": datasource or "8__table",
        "all_columns_x": "day_of_week",
        "all_columns_y": "hour_ampm",
        "metric": {
            "expressionType": "SQL",
            "sqlExpression": "COUNT(*)",
            "label": "COUNT(*)",
            "hasCustomLabel": False,
        },
        "linear_color_scheme": "schemeReds",
        "normalize_across": "heatmap",
        "xscale_interval": 1,
        "yscale_interval": 1,
        "left_margin": "auto",
        "bottom_margin": "auto",
        "show_legend": True,
        "show_values": False,
        "sort_x_axis": "alpha_asc",
        "sort_y_axis": "alpha_asc",
        "adhoc_filters": [],
        "row_limit": 10000,
    }

    payload = {
        "slice_name": "Booking Heat Map (Peak Times)",
        "viz_type": "heatmap",
        "params": json.dumps(fresh_params),
    }
    if datasource_id:
        payload["datasource_id"] = datasource_id
        payload["datasource_type"] = "table"

    api_put(f"/api/v1/chart/{chart_id}", payload)
    print(f"Heatmap rebuilt: id={chart_id}, datasource={datasource}")


if __name__ == "__main__":
    main()
