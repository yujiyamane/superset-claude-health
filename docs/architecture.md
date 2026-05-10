# System Architecture

## Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                       │
│  PostgreSQL 16 (healthcare_db)                                    │
│                                                                   │
│  fact_ed_visits (208,955 rows)                                    │
│  ├── dim_hospital  (10 NSW hospitals, 5 LHDs)                     │
│  ├── dim_ward      (100 wards, 10 types)                          │
│  ├── dim_triage    (5 ATS categories)                             │
│  └── dim_date      (730 days: FY2024-25 + FY2025-26)             │
└───────────────────────────┬──────────────────────────────────────┘
                            │ SQLAlchemy / psycopg2
┌───────────────────────────▼──────────────────────────────────────┐
│  BI LAYER                                                         │
│  Apache Superset 5.0 (Docker)                                     │
│                                                                   │
│  Datasets → Charts → Dashboard                                    │
│  RLS Rules: LHD scope + Ward scope                               │
│  RBAC: Admin / LHD_Manager / Ward_Nurse                          │
└───────────────────────────┬──────────────────────────────────────┘
                            │ MCP Server (port 5008)
┌───────────────────────────▼──────────────────────────────────────┐
│  AI LAYER                                                         │
│  Claude Code / Claude Desktop                                     │
│                                                                   │
│  Natural language → Superset REST API calls                      │
│  "Create a bar chart of wait times by triage category"           │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### PostgreSQL 16

- **superset_meta** database: Superset's internal state (dashboards, charts, users, roles)
- **healthcare_db** database: Star schema with NSW Emergency Department data
- Initialised via `data/schema.sql` on first container start
- Data loaded via `scripts/load_data.py` using pandas + SQLAlchemy

### Apache Superset 5.0

- Custom Docker image (`Dockerfile`) adds `psycopg2-binary` and `flask-cors` to the venv
- Configured via `superset/superset_config.py` (MCP, RBAC, CORS feature flags)
- Exposes REST API on port 8088 and MCP server on port 5008
- Admin initialised automatically on first start (`superset init`)

### Star Schema

```
dim_date ──────┐
dim_triage ────┤
dim_hospital ──┼──► fact_ed_visits
dim_ward ──────┘
```

Key fact table columns:
- `arrival_time`, `wait_time_minutes`, `total_los_minutes`
- `four_hour_breach` (BOOLEAN) — core KPI for Australian ED targets
- `departure_status` — Discharged / Admitted / Transferred / Did Not Wait / Deceased
- `patient_age`, `patient_gender`

### Data Generation (`data/generate_data.py`)

Realistic synthetic NSW ED data:
- **Arrival distribution**: bimodal (10am peak + 8pm peak)
- **Wait times**: lognormal by triage category (ATS-compliant maxima)
- **Four-hour breach**: correlated with total LOS > 240 minutes
- **Weekend variation**: ~15% higher weekend presentation volume

## Ports

| Port | Service |
|------|---------|
| 5432 | PostgreSQL |
| 8088 | Superset UI + REST API |
| 5008 | Superset MCP Server |
