import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "superset-claude-health-secret")

EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "nswHealth",
        "description": "NSW Health colour palette",
        "label": "NSW Health",
        "isDefault": False,
        "colors": ["#002664", "#146cfd", "#2e808e", "#8ce0ff", "#ffb8c1", "#630019", "#d1eeea"],
    }
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
}

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
