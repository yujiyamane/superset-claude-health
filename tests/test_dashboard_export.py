import pytest
import json
import os

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "superset", "dashboards")

def test_dashboard_export_exists():
    files = os.listdir(EXPORT_DIR)
    json_files = [f for f in files if f.endswith(".json")]
    assert len(json_files) >= 1

def test_dashboard_json_is_valid():
    files = os.listdir(EXPORT_DIR)
    json_files = [f for f in files if f.endswith(".json")]
    for f in json_files:
        with open(os.path.join(EXPORT_DIR, f)) as fh:
            data = json.load(fh)
        assert "dashboard_title" in data or "metadata" in data
