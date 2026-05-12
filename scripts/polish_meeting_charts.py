import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_put

FLOOR_COLORS = {
    "Level 2": "#ffb8c1",
    "Level 3": "#e89aab",
    "Level 4": "#d17c95",
    "Level 5": "#ba5e7f",
    "Level 6": "#a34069",
    "Level 7": "#8c2253",
    "Level 8": "#75043d",
    "Level 9": "#630019",
}

TIME_COLORS = {
    "8 AM": "#630019",
    "9 AM": "#8c2253",
    "10 AM": "#a34069",
    "11 AM": "#ba5e7f",
    "12 PM": "#d17c95",
    "1 PM": "#e89aab",
    "2 PM": "#ffb8c1",
    "3 PM": "#8ce0ff",
    "4 PM": "#2e808e",
    "5 PM": "#002664",
}

DOW_COLORS = {
    "Mon": "#002664",
    "Tue": "#ff6b35",
    "Wed": "#2e808e",
    "Thu": "#146cfd",
    "Fri": "#999999",
}


def get_dashboard_id():
    data = api_get("/api/v1/dashboard/")
    for d in data.get("result", []):
        if "Meeting" in d.get("dashboard_title", ""):
            return d["id"]
    raise RuntimeError("Meeting dashboard not found")


def get_dashboard_charts(dash_id):
    return api_get(f"/api/v1/dashboard/{dash_id}/charts").get("result", [])


def matches(ch, *keywords, exclude=None):
    name = ch.get("slice_name", "").lower()
    if not all(kw.lower() in name for kw in keywords):
        return False
    if exclude and any(ex.lower() in name for ex in exclude):
        return False
    return True


def viz(ch):
    return ch.get("form_data", {}).get("viz_type", "").lower()


def find(charts, *keywords, exclude=None, vt=None):
    for ch in charts:
        if not matches(ch, *keywords, exclude=exclude):
            continue
        if vt and vt.lower() not in viz(ch):
            continue
        return ch
    return None


def update_chart(chart_id, new_name, params_patch, set_viz_type=None):
    detail = api_get(f"/api/v1/chart/{chart_id}")
    params = json.loads(detail.get("result", {}).get("params", "{}"))
    for key in ["header_font_size", "subheader_font_size"]:
        params.pop(key, None)
    params.update(params_patch)
    if set_viz_type:
        params["viz_type"] = set_viz_type
    payload = {"slice_name": new_name, "params": json.dumps(params)}
    if set_viz_type:
        payload["viz_type"] = set_viz_type
    api_put(f"/api/v1/chart/{chart_id}", payload)
    print(f"  {new_name} (id={chart_id})")


def main():
    dash_id = get_dashboard_id()
    charts = get_dashboard_charts(dash_id)
    print(f"Found {len(charts)} charts.\n")
    updated = 0

    ch = find(charts, "total", "booking", exclude=["room", "floor", "day", "time", "date", "hour"])
    if not ch:
        ch = find(charts, "total bookings")
    if ch:
        update_chart(ch["id"], "Total Bookings", {
            "y_axis_format": ",.2s",
            "number_format": ",.2s",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        })
        updated += 1

    ch = find(charts, "hours")
    if ch:
        update_chart(ch["id"], "Total Hours Booked", {
            "y_axis_format": ",.2s",
            "number_format": ",.2s",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        })
        updated += 1

    ch = find(charts, "duration", exclude=["day", "week", "&"])
    if not ch:
        ch = find(charts, "average booking")
    if ch:
        update_chart(ch["id"], "Average Booking Duration (Mins)", {
            "y_axis_format": ".0f",
            "number_format": ".0f",
            "subheader": "mins avg",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        })
        updated += 1

    ch = find(charts, "utilisation", exclude=["room", "name"])
    if ch:
        update_chart(ch["id"], "Utilisation Rate", {
            "y_axis_format": ".2f",
            "number_format": ".2f",
            "subheader": "%",
            "color_picker": {"r": 0, "g": 38, "b": 100, "a": 1},
        })
        updated += 1

    ch = find(charts, "floor", vt="pie")
    if not ch:
        ch = find(charts, "floor", "level", exclude=["bar", "(bar)"])
    if ch:
        update_chart(ch["id"], "# of Bookings by Floor Level", {
            "color_scheme": "",
            "label_colors": FLOOR_COLORS,
            "donut": True,
            "innerRadius": 40,
            "show_labels": True,
            "show_legend": True,
            "show_labels_threshold": 5,
        })
        updated += 1

    ch = find(charts, "time", vt="pie")
    if not ch:
        ch = find(charts, "time", exclude=["day", "week", "heat", "date", "duration"])
    if ch:
        update_chart(ch["id"], "# of Bookings by Time", {
            "color_scheme": "",
            "label_colors": TIME_COLORS,
            "donut": True,
            "innerRadius": 40,
            "show_labels": True,
            "show_legend": True,
        })
        updated += 1

    ch = find(charts, "day of week", vt="pie")
    if not ch:
        ch = find(charts, "day of week", exclude=["duration", "&"])
    if not ch:
        ch = find(charts, "day", "week", exclude=["duration", "&"])
    if ch:
        update_chart(ch["id"], "# of Bookings by Day of Week", {
            "color_scheme": "",
            "label_colors": DOW_COLORS,
            "donut": True,
            "innerRadius": 40,
            "show_labels": True,
            "show_legend": True,
        })
        updated += 1

    ch = find(charts, "heat")
    if ch:
        detail = api_get(f"/api/v1/chart/{ch['id']}")
        old_p = json.loads(detail.get("result", {}).get("params", "{}"))
        heatmap_params = {
            "viz_type": "heatmap_v2",
            "datasource": old_p.get("datasource", "8__table") or "8__table",
            "x_axis": "day_of_week",
            "groupby": ["hour_ampm"],
            "metric": {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "COUNT(*)"},
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
        api_put(f"/api/v1/chart/{ch['id']}", {
            "slice_name": "Booking Heat Map (Peak Times)",
            "viz_type": "heatmap_v2",
            "params": json.dumps(heatmap_params),
        })
        print(f"  Booking Heat Map (Peak Times) (id={ch['id']})")
        updated += 1

    ch = find(charts, "floor", exclude=["donut", "pie"])
    if not ch:
        ch = find(charts, "floor", "level")
        if ch and "pie" in viz(ch):
            ch = None
    if ch:
        update_chart(ch["id"], "# of Bookings by Floor Level", {
            "color_scheme": "pink_red_gradient",
            "label_colors": FLOOR_COLORS,
            "orient": "horizontal",
            "sort_bars": True,
            "order_desc": False,
        })
        updated += 1

    ch = find(charts, "duration", "day")
    if not ch:
        ch = find(charts, "&", "duration")
    if ch:
        update_chart(ch["id"], "# of Bookings & Duration by Day of Week", {
            "color_scheme": "pink_red_gradient",
            "show_bar_value": True,
        })
        updated += 1

    ch = find(charts, "room", exclude=["utilisation", "rate", "duration", "name"])
    if not ch:
        ch = find(charts, "bookings by room")
    if ch:
        update_chart(ch["id"], "# of Bookings by Room", {
            "color_scheme": "dark_red_palette",
            "label_colors": {},
            "orient": "horizontal",
            "order_desc": True,
        })
        updated += 1

    ch = find(charts, "utilisation", "room")
    if not ch:
        ch = find(charts, "utilisation rate by room")
    if ch:
        update_chart(ch["id"], "Utilisation Rate by Room Name", {
            "color_scheme": "dark_red_palette",
            "label_colors": {},
            "orient": "horizontal",
            "order_desc": True,
            "y_axis_format": ".1%",
        })
        updated += 1

    ch = find(charts, "date")
    if ch:
        update_chart(ch["id"], "# of Bookings by Date", {
            "color_scheme": "nsw_navy",
            "area": True,
            "opacity": 0.7,
        })
        updated += 1

    print(f"\nDone. {updated}/13 charts updated.")


if __name__ == "__main__":
    main()
