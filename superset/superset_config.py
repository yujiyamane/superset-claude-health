import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "superset-claude-health-secret")
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://superset:superset@postgres:5432/superset_meta"
)

EXTRA_DATABASES = {
    "healthcare_db": {
        "sqlalchemy_uri": "postgresql+psycopg2://superset:superset@postgres:5432/healthcare_db",
        "expose_in_sqllab": True,
    }
}

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
