import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_put

PINK_RED_8 = ["#ffb8c1", "#e89aab", "#d17c95", "#ba5e7f", "#a34069", "#8c2253", "#75043d", "#630019"]
FLOOR_COLORS = {f"Level {i}": PINK_RED_8[i - 2] for i in range(2, 10)}
DOW_COLORS = {"Mon": "#002664", "Tue": "#146cfd", "Wed": "#2e808e", "Thu": "#8ce0ff", "Fri": "#ffb8c1"}


def get_meeting_charts():
    data = api_get("/api/v1/chart/")
    return {ch["slice_name"]: ch for ch in data.get("result", []) if "Meeting:" in ch.get("slice_name", "")}


def update_chart(chart_id, new_name, params_override):
    detail = api_get(f"/api/v1/chart/{chart_id}")
    existing_params = json.loads(detail.get("result", {}).get("params", "{}"))
    existing_params.update(params_override)
    api_put(f"/api/v1/chart/{chart_id}", {
        "slice_name": new_name,
        "params": json.dumps(existing_params),
    })
    print(f"  {new_name} (id={chart_id})")


def main():
    charts = get_meeting_charts()
    print(f"Found {len(charts)} charts to polish.\n")

    if "Meeting: Total Bookings" in charts:
        update_chart(charts["Meeting: Total Bookings"]["id"], "Total Bookings", {
            "header_font_size": 0.4,
            "subheader_font_size": 0.15,
            "y_axis_format": ",d",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        })

    if "Meeting: Total Hours Booked" in charts:
        update_chart(charts["Meeting: Total Hours Booked"]["id"], "Total Hours Booked", {
            "header_font_size": 0.4,
            "subheader_font_size": 0.15,
            "y_axis_format": ",.0f",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        })

    if "Meeting: Average Booking Duration" in charts:
        update_chart(charts["Meeting: Average Booking Duration"]["id"], "Average Booking Duration (Mins)", {
            "header_font_size": 0.4,
            "subheader_font_size": 0.15,
            "y_axis_format": ".0f",
            "subheader": "",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        })

    if "Meeting: Utilisation Rate" in charts:
        update_chart(charts["Meeting: Utilisation Rate"]["id"], "Utilisation Rate", {
            "header_font_size": 0.4,
            "subheader_font_size": 0.15,
            "y_axis_format": ".2f",
            "subheader": "%",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        })

    if "Meeting: Bookings by Floor Level (Donut)" in charts:
        update_chart(charts["Meeting: Bookings by Floor Level (Donut)"]["id"], "# of Bookings by Floor Level", {
            "color_scheme": "nsw_navy",
            "label_colors": FLOOR_COLORS,
            "donut": True,
            "innerRadius": 40,
            "show_labels": True,
            "show_legend": True,
            "show_labels_threshold": 5,
        })

    if "Meeting: Bookings by Time (Donut)" in charts:
        update_chart(charts["Meeting: Bookings by Time (Donut)"]["id"], "# of Bookings by Time", {
            "color_scheme": "nsw_navy",
            "donut": True,
            "innerRadius": 40,
            "show_labels": True,
            "show_legend": True,
        })

    if "Meeting: Bookings by Day of Week (Donut)" in charts:
        update_chart(charts["Meeting: Bookings by Day of Week (Donut)"]["id"], "# of Bookings by Day of Week", {
            "color_scheme": "nsw_navy",
            "label_colors": DOW_COLORS,
            "donut": True,
            "innerRadius": 40,
            "show_labels": True,
            "show_legend": True,
        })

    if "Meeting: Booking Heat Map (Peak Times)" in charts:
        update_chart(charts["Meeting: Booking Heat Map (Peak Times)"]["id"], "Booking Heat Map (Peak Times)", {
            "linear_color_scheme": "nsw_heatmap",
        })

    if "Meeting: Bookings by Floor Level (Bar)" in charts:
        update_chart(charts["Meeting: Bookings by Floor Level (Bar)"]["id"], "# of Bookings by Floor Level (Bar)", {
            "color_scheme": "nsw_navy",
        })

    if "Meeting: Bookings & Duration by Day of Week" in charts:
        update_chart(charts["Meeting: Bookings & Duration by Day of Week"]["id"], "# of Bookings & Duration by Day of Week", {
            "color_scheme": "nsw_navy",
        })

    if "Meeting: Bookings by Room" in charts:
        update_chart(charts["Meeting: Bookings by Room"]["id"], "# of Bookings by Room", {
            "color_scheme": "nsw_navy",
        })

    if "Meeting: Utilisation Rate by Room Name" in charts:
        update_chart(charts["Meeting: Utilisation Rate by Room Name"]["id"], "Utilisation Rate by Room Name", {
            "color_scheme": "nsw_navy",
        })

    if "Meeting: Bookings by Date" in charts:
        update_chart(charts["Meeting: Bookings by Date"]["id"], "# of Bookings by Date", {
            "color_scheme": "nsw_navy",
        })

    print(f"\nDone. {len(charts)} charts polished.")


if __name__ == "__main__":
    main()
