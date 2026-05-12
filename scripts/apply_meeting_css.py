import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_put

CSS = """
.dashboard-content {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.header-title {
    color: #002664 !important;
    font-weight: 700 !important;
    font-size: 24px !important;
}
.superset-legacy-chart-big-number .header-line {
    color: #002664 !important;
    font-size: 48px !important;
    font-weight: 700 !important;
}
.superset-legacy-chart-big-number .subheader-line {
    color: #002664 !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    text-transform: uppercase;
}
.dashboard-component-chart-holder {
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 38, 100, 0.08);
    border: 1px solid #d1eeea;
}
.filter-bar {
    background-color: #f8fbff !important;
    border-right: 2px solid #002664 !important;
}
"""


def get_meeting_dashboard_id():
    data = api_get("/api/v1/dashboard/")
    for d in data.get("result", []):
        if "Meeting" in d.get("dashboard_title", ""):
            return d["id"]
    raise RuntimeError("Meeting dashboard not found")


def main():
    dash_id = get_meeting_dashboard_id()
    api_put(f"/api/v1/dashboard/{dash_id}", {"css": CSS})
    print(f"CSS applied to dashboard id={dash_id}")


if __name__ == "__main__":
    main()
