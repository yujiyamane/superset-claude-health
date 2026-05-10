# Superset x Claude MCP Healthcare Dashboard — Claude Code Implementation Guide

Execute end-to-end. TDD. No questions. PowerShell for all terminal commands.

## REPO LOCATION
`C:\Users\Admin\Documents\Life\Work\BI\superset-claude-health`

## PREREQUISITE CHECK
1. Docker Desktop running
2. Python 3.11+ available
3. gh CLI authenticated

---

## PHASE 1: Repository Setup + Data Generation (TDD)

### Step 1: Create repo structure
```powershell
cd C:\Users\Admin\Documents\Life\Work\BI
mkdir superset-claude-health
cd superset-claude-health
```
I will paste the following files from the downloaded artifacts. Write each file exactly as provided:
- README.md
- docker-compose.yml
- data/schema.sql
- superset/color_theme.py
- .gitignore
- requirements.txt

### Step 2: Write tests FIRST (Red)

Create `tests/test_colour_theme.py`:
```python
import re
import pytest
import sys
sys.path.insert(0, "superset")
from color_theme import PALETTE, CHART_SEQUENCE, HEATMAP_SCALE, SUPERSET_THEME

HEX_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")

def test_all_palette_values_are_valid_hex():
    for name, color in PALETTE.items():
        assert HEX_PATTERN.match(color), f"{name}: {color} is not valid hex"

def test_chart_sequence_has_5_colors():
    assert len(CHART_SEQUENCE) == 5

def test_chart_sequence_all_from_palette():
    palette_values = set(PALETTE.values())
    for color in CHART_SEQUENCE:
        assert color in palette_values

def test_no_duplicate_colors_in_palette():
    values = list(PALETTE.values())
    assert len(values) == len(set(values))

def test_heatmap_scale_bounds():
    assert HEATMAP_SCALE[0][0] == 0.0
    assert HEATMAP_SCALE[-1][0] == 1.0

def test_alert_is_red_dominant():
    r = int(PALETTE["alert"][1:3], 16)
    g = int(PALETTE["alert"][3:5], 16)
    b = int(PALETTE["alert"][5:7], 16)
    assert r > g and r > b

def test_superset_theme_has_required_keys():
    assert "colors" in SUPERSET_THEME
    assert "primary" in SUPERSET_THEME["colors"]
    assert "error" in SUPERSET_THEME["colors"]

def test_superset_theme_primary_matches_palette():
    assert SUPERSET_THEME["colors"]["primary"]["base"] == PALETTE["primary"]
```

Create `tests/test_data_integrity.py`:
```python
import pytest
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def test_generate_data_creates_csvs():
    from data.generate_data import generate_all
    generate_all(DATA_DIR)
    assert os.path.exists(os.path.join(DATA_DIR, "dim_hospital.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "dim_ward.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "dim_triage.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "dim_date.csv"))
    assert os.path.exists(os.path.join(DATA_DIR, "fact_ed_visits.csv"))

def test_fact_table_row_count():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    assert len(df) >= 100000

def test_fact_table_has_required_columns():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    required = [
        "visit_id", "hospital_id", "ward_id", "triage_id", "date_id",
        "arrival_time", "wait_time_minutes", "total_los_minutes",
        "four_hour_breach", "patient_age", "patient_gender"
    ]
    for col in required:
        assert col in df.columns

def test_dim_hospital_has_lhd():
    df = pd.read_csv(os.path.join(DATA_DIR, "dim_hospital.csv"))
    assert "lhd_name" in df.columns
    assert df["lhd_name"].nunique() >= 5

def test_triage_categories_1_to_5():
    df = pd.read_csv(os.path.join(DATA_DIR, "dim_triage.csv"))
    assert set(df["triage_category"]) == {1, 2, 3, 4, 5}

def test_no_null_visit_ids():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    assert df["visit_id"].notna().all()

def test_wait_times_are_positive():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    assert (df["wait_time_minutes"] >= 0).all()

def test_four_hour_breach_is_boolean():
    df = pd.read_csv(os.path.join(DATA_DIR, "fact_ed_visits.csv"))
    assert df["four_hour_breach"].isin([True, False, 0, 1]).all()
```

Create `tests/test_api_endpoints.py`:
```python
import pytest
import requests

BASE_URL = "http://localhost:8088"

@pytest.fixture(scope="module")
def auth_token():
    resp = requests.post(
        f"{BASE_URL}/api/v1/security/login",
        json={"username": "admin", "password": "admin", "provider": "db"}
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]

@pytest.fixture(scope="module")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

def test_superset_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200

def test_list_dashboards(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dashboard/", headers=headers)
    assert resp.status_code == 200

def test_list_datasets(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/dataset/", headers=headers)
    assert resp.status_code == 200

def test_list_charts(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/chart/", headers=headers)
    assert resp.status_code == 200

def test_rls_endpoint_exists(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/rowlevelsecurity/", headers=headers)
    assert resp.status_code in [200, 401, 403]

def test_security_roles_endpoint(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/security/roles/", headers=headers)
    assert resp.status_code == 200
```

Create `tests/test_rls_rules.py`:
```python
import pytest
import requests

BASE_URL = "http://localhost:8088"

@pytest.fixture(scope="module")
def auth_token():
    resp = requests.post(
        f"{BASE_URL}/api/v1/security/login",
        json={"username": "admin", "password": "admin", "provider": "db"}
    )
    return resp.json()["access_token"]

@pytest.fixture(scope="module")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

def test_rls_rules_exist(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/rowlevelsecurity/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 2

def test_lhd_manager_role_exists(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/security/roles/", headers=headers)
    roles = [r["name"] for r in resp.json()["result"]]
    assert "LHD_Manager" in roles

def test_ward_nurse_role_exists(headers):
    resp = requests.get(f"{BASE_URL}/api/v1/security/roles/", headers=headers)
    roles = [r["name"] for r in resp.json()["result"]]
    assert "Ward_Nurse" in roles
```

Create `tests/test_dashboard_export.py`:
```python
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
```

### Step 3: Run tests (should fail — Red phase)
```powershell
python -m pytest tests/test_colour_theme.py -v
```

### Step 4: Implement data generator (Green)

Create `data/generate_data.py` — reuse Case 2 logic but output CSVs matching the PostgreSQL schema above:
- 10 hospitals across 5 NSW LHDs (Sydney, Western Sydney, South Western Sydney, South Eastern Sydney, Northern Sydney)
- 100 wards (10 per hospital, types: Emergency, General, ICU, Surgical, Medical, Maternity, Paediatric, Mental Health, Rehabilitation, Oncology)
- 5 triage categories with ATS-compliant max wait times
- 730 days (FY2024-25 + FY2025-26)
- 200,000+ ED visit records with realistic distributions:
  - Wait times: lognormal, skewed by triage category
  - Four-hour breach: correlated with triage + wait time
  - Arrival times: bimodal (10am peak + 8pm peak)
  - Weekend/weekday variation

Run tests again → ALL GREEN for test_colour_theme.py and test_data_integrity.py.

### Step 5: Git init + GitHub push
```powershell
git init
git add -A
git commit -m "feat: initial repo structure with data generator and TDD"
gh repo create yujiyamane/superset-claude-health --public --source=. --push
gh repo edit yujiyamane/superset-claude-health --default-branch main
git branch -M main
git push -u origin main
```

---

## PHASE 2: Docker + Superset Setup

### Step 6: Create superset_config.py
```python
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
```

### Step 7: Start Docker
```powershell
docker compose up -d
# Wait for healthy status
docker compose ps
# Verify Superset is running
curl http://localhost:8088/health
```

### Step 8: Create data loader script
Create `scripts/load_data.py`:
- Connects to PostgreSQL (healthcare_db)
- Reads CSVs from data/ directory
- Loads into tables using pandas to_sql
- Verifies row counts after load

Run it:
```powershell
python scripts/load_data.py
```

### Step 9: Run API tests
```powershell
python -m pytest tests/test_api_endpoints.py -v
```
ALL GREEN before proceeding.

### Step 10: Git commit
```powershell
git add -A
git commit -m "feat: Docker Compose + PostgreSQL data load + API tests"
git push
```

---

## PHASE 3: Dashboard Creation via MCP

### Step 11: Configure Claude Desktop MCP connection

Add to Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "superset": {
      "url": "http://localhost:5008/mcp"
    }
  }
}
```

### Step 12: Create datasets via MCP or API

Create `scripts/setup_datasets.py`:
- POST to /api/v1/dataset/ for each table (fact_ed_visits, dim_hospital, dim_ward, dim_triage, dim_date)
- Configure join relationships

### Step 13: Build charts via API

Create `scripts/create_charts.py`:
- Use POST /api/v1/chart/ to create each chart programmatically
- Apply colour palette from color_theme.py
- Charts to create:
  1. KPI Card: Total Presentations
  2. KPI Card: Average Wait Time
  3. KPI Card: 4-Hour Rule Compliance %
  4. KPI Card: Average LOS
  5. Bar Chart: Presentations by Hospital
  6. Line Chart: Monthly Presentation Trend
  7. Stacked Bar: Triage Category Distribution
  8. Heatmap: Hour x Day-of-Week Presentations
  9. Bar Chart: Wait Time by Triage Category
  10. Gauge: 4-Hour Breach Rate
  11. Pie Chart: Departure Status Distribution
  12. Bar Chart: LHD Comparison

### Step 14: Assemble dashboard
Create `scripts/create_dashboard.py`:
- POST /api/v1/dashboard/ with position_json layout
- Add all 12 charts to dashboard
- Configure cross-filters

### Step 15: Export dashboard as JSON
```powershell
python scripts/export_dashboard.py
# Saves to superset/dashboards/ed_performance.json
```

### Step 16: Run dashboard export tests
```powershell
python -m pytest tests/test_dashboard_export.py -v
```

### Step 17: Git commit
```powershell
git add -A
git commit -m "feat: 12 charts + dashboard created via Superset API"
git push
```

---

## PHASE 4: RLS + RBAC Configuration

### Step 18: Create roles
Create `scripts/setup_roles.py`:
- POST /api/v1/security/roles/ to create:
  - LHD_Manager (with dashboard read, chart read, dataset read)
  - Ward_Nurse (with dashboard read, chart read, dataset read)
- Create test users:
  - admin / admin (Admin role)
  - lhd_manager_syd / password (LHD_Manager, lhd=Sydney)
  - ward_nurse_ed1 / password (Ward_Nurse, ward_id=1)

### Step 19: Create RLS rules
Create `scripts/setup_rls.py`:
- POST /api/v1/rowlevelsecurity/ to create:
  - Rule 1: LHD_Manager sees only their LHD
    - clause: `lhd_name = '{{current_user.lhd}}'`
    - tables: [fact_ed_visits joined to dim_hospital]
  - Rule 2: Ward_Nurse sees only their ward
    - clause: `ward_id = {{current_user.ward}}`
    - tables: [fact_ed_visits]

### Step 20: Run RLS tests
```powershell
python scripts/setup_roles.py
python scripts/setup_rls.py
python -m pytest tests/test_rls_rules.py -v
```
ALL GREEN.

### Step 21: Git commit
```powershell
git add -A
git commit -m "feat: RBAC roles + RLS rules configured via API"
git push
```

---

## PHASE 5: Documentation + Screenshots

### Step 22: Create docs
- `docs/architecture.md` — system architecture with diagrams
- `docs/mcp_setup.md` — Claude MCP connection guide
- `docs/rls_guide.md` — RLS implementation details
- `docs/before_after.md` — manual vs AI-automated comparison

### Step 23: Take screenshots
- Open http://localhost:8088 in browser
- Screenshot dashboard overview → screenshots/dashboard_overview.png
- Record RLS demo (switch users, show filtered data) → screenshots/rls_demo.gif
- Screenshot MCP interaction → screenshots/mcp_interaction.png

### Step 24: Final commit + push
```powershell
git add -A
git commit -m "docs: architecture, MCP setup, RLS guide, screenshots"
git push
```

### Step 25: Add .gitignore entry to Life repo
```powershell
cd C:\Users\Admin\Documents\Life
echo "Work/BI/superset-claude-health/" >> .gitignore
git add .gitignore
git commit -m "chore: add superset-claude-health to gitignore"
git push
```

---

## RULES
- No comments in generated code
- TDD: tests first, then implementation, then verify GREEN
- All API interactions scripted (no manual UI clicks)
- Colour palette from color_theme.py — no hardcoded hex in scripts
- PowerShell for all terminal commands
- After ALL changes, run full test suite: `python -m pytest tests/ -v`
- Docker must be running before Phase 2+
