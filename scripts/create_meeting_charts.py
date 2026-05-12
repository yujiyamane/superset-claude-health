import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_post

HEALTHCARE_DB_URI = "postgresql+psycopg2://superset:superset@postgres:5432/healthcare_db"
TABLE_NAME = "meeting_bookings"

PINK_RED = ["#ffb8c1", "#e89aab", "#d17c95", "#ba5e7f", "#a34069", "#8c2253", "#75043d", "#630019"]
NAVY = "#002664"
ALERT = "#630019"
SOFT_PINK = "#ffb8c1"
NEUTRAL = "#d1eeea"


def get_or_create_database():
    existing = api_get("/api/v1/database/")
    for db in existing.get("result", []):
        if "healthcare" in db.get("database_name", "").lower():
            return db["id"]
    result = api_post("/api/v1/database/", {
        "database_name": "healthcare_db",
        "sqlalchemy_uri": HEALTHCARE_DB_URI,
        "expose_in_sqllab": True,
        "allow_run_async": True,
        "allow_dml": False,
        "allow_file_upload": False,
    })
    return result["id"]


def get_or_create_dataset(db_id):
    existing = api_get("/api/v1/dataset/")
    for ds in existing.get("result", []):
        if ds.get("table_name") == TABLE_NAME:
            print(f"  Dataset already exists: {TABLE_NAME} id={ds['id']}")
            return ds["id"]
    result = api_post("/api/v1/dataset/", {
        "database": db_id,
        "table_name": TABLE_NAME,
        "schema": "public",
    })
    ds_id = result["id"]
    print(f"  Dataset created: {TABLE_NAME} id={ds_id}")
    return ds_id


def chart_exists(name):
    data = api_get("/api/v1/chart/")
    for ch in data.get("result", []):
        if ch.get("slice_name") == name:
            return ch["id"]
    return None


def make_chart(name, viz_type, ds_id, params):
    existing = chart_exists(name)
    if existing:
        print(f"  Exists: {name} id={existing}")
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
    print(f"  Created: {name} id={cid}")
    return cid


def count_metric(label="COUNT(*)"):
    return {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": label}


def simple_metric(col, agg, label=None):
    return {"expressionType": "SIMPLE", "column": {"column_name": col}, "aggregate": agg, "label": label or f"{agg}({col})"}


def main():
    print("Setting up database + dataset...")
    db_id = get_or_create_database()
    ds_id = get_or_create_dataset(db_id)
    print(f"  db_id={db_id}, ds_id={ds_id}")

    print("\nCreating 13 Meeting charts...")

    ids = {}

    ids["kpi_bookings"] = make_chart(
        "Meeting: Total Bookings",
        "big_number_total",
        ds_id,
        {
            "metric": count_metric("COUNT(*)"),
            "subheader": "",
            "y_axis_format": ",d",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        },
    )

    ids["kpi_hours"] = make_chart(
        "Meeting: Total Hours Booked",
        "big_number_total",
        ds_id,
        {
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": "ROUND(SUM(duration_minutes)::numeric / 60, 0)",
                "label": "Total Hours",
            },
            "subheader": "",
            "y_axis_format": ",d",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        },
    )

    ids["kpi_avg_duration"] = make_chart(
        "Meeting: Average Booking Duration",
        "big_number_total",
        ds_id,
        {
            "metric": simple_metric("duration_minutes", "AVG", "Avg Duration (min)"),
            "subheader": "minutes",
            "y_axis_format": ".0f",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        },
    )

    ids["kpi_utilisation"] = make_chart(
        "Meeting: Utilisation Rate",
        "big_number_total",
        ds_id,
        {
            "metric": simple_metric("utilisation_rate", "AVG", "Avg Utilisation %"),
            "subheader": "%",
            "y_axis_format": ".2f",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        },
    )

    ids["donut_floor"] = make_chart(
        "Meeting: Bookings by Floor Level (Donut)",
        "pie",
        ds_id,
        {
            "metric": count_metric(),
            "groupby": ["floor_level_name"],
            "color_scheme": "supersetColors",
            "label_colors": {f"Level {i}": PINK_RED[i - 2] for i in range(2, 10)},
            "show_labels": True,
            "show_legend": True,
            "donut": True,
            "innerRadius": 40,
        },
    )

    ids["donut_time"] = make_chart(
        "Meeting: Bookings by Time (Donut)",
        "pie",
        ds_id,
        {
            "metric": count_metric(),
            "groupby": ["hour_ampm"],
            "color_scheme": "supersetColors",
            "show_labels": True,
            "show_legend": True,
            "donut": True,
            "innerRadius": 40,
        },
    )

    ids["donut_dow"] = make_chart(
        "Meeting: Bookings by Day of Week (Donut)",
        "pie",
        ds_id,
        {
            "metric": count_metric(),
            "groupby": ["day_of_week"],
            "color_scheme": "supersetColors",
            "show_labels": True,
            "show_legend": True,
            "donut": True,
            "innerRadius": 40,
        },
    )

    ids["heatmap"] = make_chart(
        "Meeting: Booking Heat Map (Peak Times)",
        "heatmap_v2",
        ds_id,
        {
            "metric": count_metric(),
            "all_columns_x": "day_of_week",
            "all_columns_y": "hour_ampm",
            "linear_color_scheme": "blue_white_yellow",
            "xscale_interval": 1,
            "yscale_interval": 1,
            "left_margin": "auto",
            "bottom_margin": "auto",
            "normalize_across": "heatmap",
        },
    )

    ids["bar_floor"] = make_chart(
        "Meeting: Bookings by Floor Level (Bar)",
        "echarts_timeseries_bar",
        ds_id,
        {
            "metrics": [count_metric("Bookings")],
            "x_axis": "floor_level_name",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": False,
            "orientation": "horizontal",
        },
    )

    ids["combo_dow"] = make_chart(
        "Meeting: Bookings & Duration by Day of Week",
        "mixed_timeseries",
        ds_id,
        {
            "metrics": [count_metric("Bookings")],
            "metrics_b": [simple_metric("duration_minutes", "AVG", "Avg Duration")],
            "x_axis": "day_of_week",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": True,
            "viz_type_b": "line",
        },
    )

    ids["bar_room"] = make_chart(
        "Meeting: Bookings by Room",
        "echarts_timeseries_bar",
        ds_id,
        {
            "metrics": [count_metric("Bookings")],
            "x_axis": "room_name",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": False,
            "orientation": "horizontal",
            "row_limit": 20,
            "order_desc": True,
        },
    )

    ids["bar_util_room"] = make_chart(
        "Meeting: Utilisation Rate by Room Name",
        "echarts_timeseries_bar",
        ds_id,
        {
            "metrics": [simple_metric("utilisation_rate", "AVG", "Avg Utilisation %")],
            "x_axis": "room_name",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": False,
            "orientation": "horizontal",
            "row_limit": 20,
            "order_desc": True,
        },
    )

    ids["timeseries_date"] = make_chart(
        "Meeting: Bookings by Date",
        "echarts_area",
        ds_id,
        {
            "metrics": [count_metric("Bookings")],
            "x_axis": "start_date",
            "time_grain_sqla": "P1D",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": False,
            "opacity": 0.7,
        },
    )

    print(f"\nDone. {len(ids)} charts created/verified.")
    return ids


if __name__ == "__main__":
    main()
