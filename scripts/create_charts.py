import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_post
from superset.color_theme import CHART_SEQUENCE, PALETTE

COLOR_SCHEME = "custom"


def get_dataset_id(table_name):
    data = api_get("/api/v1/dataset/")
    for ds in data.get("result", []):
        if ds.get("table_name") == table_name:
            return ds["id"]
    raise RuntimeError(f"Dataset not found: {table_name}. Run setup_datasets.py first.")


def chart_exists(name):
    data = api_get("/api/v1/chart/")
    for ch in data.get("result", []):
        if ch.get("slice_name") == name:
            return ch["id"]
    return None


def create_chart(name, viz_type, ds_id, params):
    existing = chart_exists(name)
    if existing:
        print(f"  Chart already exists: {name} id={existing}")
        return existing

    payload = {
        "slice_name": name,
        "viz_type": viz_type,
        "datasource_id": ds_id,
        "datasource_type": "table",
        "params": json.dumps(params),
    }
    result = api_post("/api/v1/chart/", payload)
    cid = result["id"]
    print(f"  Chart created: {name} id={cid}")
    return cid


def main():
    print("Getting dataset IDs...")
    fact_id = get_dataset_id("fact_ed_visits")
    hosp_id = get_dataset_id("dim_hospital")

    print(f"  fact_ed_visits: {fact_id}")

    charts = {}
    print("\nCreating charts...")

    charts["total_presentations"] = create_chart(
        "Total Presentations",
        "big_number_total",
        fact_id,
        {
            "metric": {"expressionType": "SIMPLE", "column": {"column_name": "visit_id"}, "aggregate": "COUNT", "label": "COUNT(visit_id)"},
            "subheader": "ED Presentations",
            "y_axis_format": ",d",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        },
    )

    charts["avg_wait_time"] = create_chart(
        "Average Wait Time (min)",
        "big_number_total",
        fact_id,
        {
            "metric": {"expressionType": "SIMPLE", "column": {"column_name": "wait_time_minutes"}, "aggregate": "AVG", "label": "AVG(wait_time_minutes)"},
            "subheader": "Minutes",
            "y_axis_format": ".1f",
        },
    )

    charts["four_hour_compliance"] = create_chart(
        "4-Hour Rule Compliance %",
        "big_number_total",
        fact_id,
        {
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": "100.0 * SUM(CASE WHEN four_hour_breach = false THEN 1 ELSE 0 END) / COUNT(*)",
                "label": "4HR Compliance %",
            },
            "subheader": "% within 4 hours",
            "y_axis_format": ".1f",
        },
    )

    charts["avg_los"] = create_chart(
        "Average LOS (min)",
        "big_number_total",
        fact_id,
        {
            "metric": {"expressionType": "SIMPLE", "column": {"column_name": "total_los_minutes"}, "aggregate": "AVG", "label": "AVG(total_los_minutes)"},
            "subheader": "Length of Stay",
            "y_axis_format": ".0f",
        },
    )

    charts["presentations_by_hospital"] = create_chart(
        "Presentations by Hospital",
        "echarts_timeseries_bar",
        fact_id,
        {
            "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "visit_id"}, "aggregate": "COUNT", "label": "Presentations"}],
            "groupby": ["hospital_id"],
            "x_axis": "hospital_id",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": True,
        },
    )

    charts["monthly_trend"] = create_chart(
        "Monthly Presentation Trend",
        "echarts_timeseries_line",
        fact_id,
        {
            "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "visit_id"}, "aggregate": "COUNT", "label": "Presentations"}],
            "x_axis": "arrival_time",
            "time_grain_sqla": "P1M",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": False,
        },
    )

    charts["triage_distribution"] = create_chart(
        "Triage Category Distribution",
        "echarts_timeseries_bar",
        fact_id,
        {
            "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "visit_id"}, "aggregate": "COUNT", "label": "Count"}],
            "groupby": ["triage_id"],
            "x_axis": "triage_id",
            "stack": True,
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
        },
    )

    charts["hourly_heatmap"] = create_chart(
        "Hourly Presentation Heatmap",
        "heatmap_v2",
        fact_id,
        {
            "metric": {"expressionType": "SIMPLE", "column": {"column_name": "visit_id"}, "aggregate": "COUNT", "label": "COUNT"},
            "all_columns_x": "arrival_time",
            "all_columns_y": "arrival_time",
            "linear_color_scheme": "blue_white_yellow",
            "xscale_interval": 1,
            "yscale_interval": 1,
        },
    )

    charts["wait_time_by_triage"] = create_chart(
        "Wait Time by Triage Category",
        "echarts_timeseries_bar",
        fact_id,
        {
            "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "wait_time_minutes"}, "aggregate": "AVG", "label": "Avg Wait (min)"}],
            "groupby": ["triage_id"],
            "x_axis": "triage_id",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": False,
        },
    )

    charts["breach_rate_gauge"] = create_chart(
        "4-Hour Breach Rate",
        "gauge_chart",
        fact_id,
        {
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": "100.0 * SUM(CASE WHEN four_hour_breach = true THEN 1 ELSE 0 END) / COUNT(*)",
                "label": "Breach Rate %",
            },
            "min_val": 0,
            "max_val": 100,
            "start_angle": 225,
            "end_angle": -45,
        },
    )

    charts["departure_status"] = create_chart(
        "Departure Status Distribution",
        "pie",
        fact_id,
        {
            "metric": {"expressionType": "SIMPLE", "column": {"column_name": "visit_id"}, "aggregate": "COUNT", "label": "Count"},
            "groupby": ["departure_status"],
            "color_scheme": "supersetColors",
            "show_legend": True,
            "donut": True,
        },
    )

    charts["lhd_comparison"] = create_chart(
        "LHD Comparison",
        "echarts_timeseries_bar",
        fact_id,
        {
            "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "visit_id"}, "aggregate": "COUNT", "label": "Presentations"}],
            "groupby": ["hospital_id"],
            "x_axis": "hospital_id",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": False,
            "orientation": "horizontal",
        },
    )

    print(f"\nDone. {len(charts)} charts created/verified.")
    return charts


if __name__ == "__main__":
    main()
