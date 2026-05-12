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
    old_params = json.loads(detail.get("result", {}).get("params", "{}"))
    datasource = old_params.get("datasource", "") or "8__table"

    fresh_params = {
        "viz_type": "heatmap_v2",
        "datasource": datasource,
        "x_axis": "day_of_week",
        "groupby": ["hour_ampm"],
        "metric": {
            "expressionType": "SQL",
            "sqlExpression": "COUNT(*)",
            "label": "COUNT(*)",
        },
        "linear_color_scheme": "reds",
        "legend_type": "continuous",
        "normalize_across": "heatmap",
        "sort_x_axis": "alpha_asc",
        "sort_y_axis": "alpha_asc",
        "show_legend": True,
        "show_values": True,
        "value_bounds": [None, None],
        "adhoc_filters": [],
        "row_limit": 10000,
    }
    api_put(f"/api/v1/chart/{chart_id}", {
        "slice_name": "Booking Heat Map (Peak Times)",
        "viz_type": "heatmap_v2",
        "params": json.dumps(fresh_params),
    })
    print(f"Heatmap rebuilt: id={chart_id}, viz_type=heatmap_v2, x_axis=day_of_week, groupby=['hour_ampm']")


if __name__ == "__main__":
    main()
