import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "superset-claude-health-secret")

EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "nswHealth",
        "description": "NSW Health colour palette",
        "label": "NSW Health",
        "isDefault": False,
        "colors": ["#002664", "#146cfd", "#2e808e", "#8ce0ff", "#ffb8c1", "#630019", "#d1eeea"],
    },
    {
        "id": "nsw_navy",
        "description": "NSW Navy palette (extended 12-colour)",
        "label": "NSW Navy",
        "isDefault": False,
        "colors": [
            "#002664", "#146cfd", "#2e808e", "#8ce0ff",
            "#ffb8c1", "#630019", "#d1eeea", "#e89aab",
            "#d17c95", "#ba5e7f", "#a34069", "#8c2253",
        ],
    },
    {
        "id": "pink_red_gradient",
        "description": "Pink to Red gradient for meeting room charts",
        "label": "Pink Red Gradient",
        "isDefault": False,
        "colors": ["#ffb8c1", "#e89aab", "#d17c95", "#ba5e7f", "#a34069", "#8c2253", "#75043d", "#630019"],
    },
    {
        "id": "dark_red_palette",
        "description": "Dark red to pink palette",
        "label": "Dark Red Palette",
        "isDefault": False,
        "colors": ["#630019", "#75043d", "#8c2253", "#a34069", "#ba5e7f", "#d17c95", "#e89aab", "#ffb8c1"],
    },
]

EXTRA_SEQUENTIAL_COLOR_SCHEMES = [
    {
        "id": "white_pink_red",
        "description": "White to pink to red for heatmaps",
        "label": "White Pink Red",
        "isDefault": False,
        "colors": ["#ffffff", "#ffe0e6", "#ffb8c1", "#e89aab", "#d17c95", "#ba5e7f", "#a34069", "#8c2253", "#630019"],
    },
    {
        "id": "white_to_red",
        "description": "White to red heatmap (#FFFFFF -> #CC0000)",
        "label": "White to Red",
        "isDefault": False,
        "colors": ["#ffffff", "#ffe5e5", "#ffcccc", "#ff9999", "#ff6666", "#ff3333", "#ee1111", "#cc0000"],
    },
]

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://superset:superset@postgres:5432/superset_meta"
)

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_RBAC": True,
    "EMBEDDED_SUPERSET": True,
    "ALERT_REPORTS": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "DASHBOARD_CROSS_FILTERS": True,
}

HTML_SANITIZATION = False
MARKDOWN_SANITIZE_HTML = False

APP_NAME = "AIxBI Government"
APP_ICON = "/static/assets/images/aixbi-logo.svg"
APP_ICON_WIDTH = 220

MCP_ENABLED = True
MCP_PORT = 5008
MCP_HOST = "0.0.0.0"

ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": [r"/api/*"],
    "origins": ["*"],
}
