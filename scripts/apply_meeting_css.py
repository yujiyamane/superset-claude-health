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
}
.superset-legacy-chart-big-number .header-line {
    color: #002664 !important;
}
.superset-legacy-chart-big-number .subheader-line {
    color: #666 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.dashboard-component-chart-holder {
    border-radius: 4px;
    border: 1px solid #e8e8e8;
}
.filter-bar {
    background-color: #f8fbff !important;
    border-right: 2px solid #002664 !important;
}
.dashboard-component-markdown {
    padding: 0 !important;
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
