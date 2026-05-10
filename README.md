# Superset × Claude MCP — Healthcare ED Dashboard

> **An AI-automated BI dashboard: Apache Superset + Claude MCP builds charts, configures RLS, and deploys — all from natural language.**

[![Superset](https://img.shields.io/badge/Apache_Superset-5.0+-002664?style=for-the-badge&logo=apache&logoColor=white)](https://superset.apache.org/)
[![Claude MCP](https://img.shields.io/badge/Claude_MCP-Integrated-146cfd?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.ai/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2e808e?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-002664?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

---

## What This Is

A complete Healthcare Emergency Department dashboard built **entirely through AI automation**. No manual chart creation, no clicking through UI wizards — Claude Code talks to Superset via MCP to:

1. **Create datasets** from PostgreSQL tables
2. **Build 12+ charts** (bar, line, heatmap, gauge, pie)
3. **Assemble dashboard layouts** with filters and cross-links
4. **Configure Row-Level Security** so each user sees only their authorised data
5. **Export everything as code** (JSON + Git versioned)

## Architecture

```
┌─────────────────────┐
│   PostgreSQL 16     │  200K+ synthetic ED records
│   (healthcare_db)   │  Star schema: fact_ed_visits + 4 dims
└────────┬────────────┘
         │ SQLAlchemy
┌────────▼────────────┐
│   Apache Superset   │  Dashboard engine
│   (Docker Compose)  │  Native RLS, RBAC, 60+ chart types
└────────┬────────────┘
         │ MCP Server (built-in, Superset 5.0+)
┌────────▼────────────┐
│   Claude Code /     │  Natural language → API calls
│   Claude Desktop    │  "Create a bar chart of wait times
└─────────────────────┘   by triage category from ed_visits"
```

### Claude MCP Interaction

![MCP Interaction](screenshots/mcp_interaction.png)

*Dashboard built entirely through natural language via Claude MCP*

## Dashboard Pages

### ED Performance Overview
KPI cards (presentations, ALOS, 4-hour rule %), monthly trend lines, LHD comparison bars.

### Triage & Wait Times
Wait time distributions by triage category, hourly presentation heatmaps, breach rate gauges.

### Capacity & Flow
Bed occupancy by ward type, patient flow Sankey diagrams, time-to-admission tracking.

### Preview

![Dashboard Overview](screenshots/dashboard_overview.png)

### KPI Cards
![KPI Cards](screenshots/kpi_cards.png)

### Triage Analysis
![Triage Chart](screenshots/triage_chart.png)

### Hourly Heatmap
![Heatmap](screenshots/heatmap.png)

## Row-Level Security

Three roles with automatic data filtering:

| Role | Sees | Filter |
|------|------|--------|
| Admin | All LHDs, all wards | No filter |
| LHD Manager | Their LHD only | `lhd_name = {{current_user.lhd}}` |
| Ward Nurse | Their ward only | `ward_id = {{current_user.ward}}` |

RLS rules are configured programmatically via Superset's REST API (8 endpoints), not through the UI.

### RLS in Action

![RLS Demo](screenshots/rls_demo.gif)

*Admin sees all data → LHD Manager sees Sydney only → Ward Nurse sees their ward only*

| Role | Screenshot |
|------|-----------|
| LHD Manager | ![LHD Manager View](screenshots/rls_lhd_manager.png) |
| Ward Nurse | ![Ward Nurse View](screenshots/rls_ward_nurse.png) |

## Colour Palette

| Role | HEX | Usage |
|------|-----|-------|
| Primary | `#002664` | Main KPIs, chart series 1 |
| Secondary | `#146cfd` | Chart series 2, emphasis |
| Teal | `#2e808e` | Chart series 3, categories |
| Baby Blue | `#8ce0ff` | Chart series 4, backgrounds |
| Soft Pink | `#ffb8c1` | Accent, light warnings |
| Alert | `#630019` | Threshold breaches |
| Neutral | `#d1eeea` | Gridlines, backgrounds |

## Quick Start

```bash
git clone https://github.com/yujiyamane/superset-claude-health.git
cd superset-claude-health

# Start Superset + PostgreSQL
docker compose up -d

# Load healthcare data
python scripts/load_data.py

# Connect Claude Desktop via MCP (see docs/mcp_setup.md)
# Then ask Claude: "Create the ED Performance dashboard"
```

## Repository Structure

```
├── README.md
├── docker-compose.yml          # Superset + PostgreSQL + MCP server
├── superset/
│   ├── superset_config.py      # Superset configuration + MCP + RLS
│   ├── dashboards/             # Exported dashboard JSON (Git-versioned)
│   └── datasets/               # Dataset definitions
├── data/
│   ├── generate_data.py        # Synthetic ED data generator (same as Case 2)
│   └── schema.sql              # PostgreSQL schema (star schema)
├── scripts/
│   ├── load_data.py            # Data loader: CSV → PostgreSQL
│   ├── setup_rls.py            # Programmatic RLS configuration via API
│   ├── setup_roles.py          # RBAC role creation via API
│   └── apply_theme.py          # Colour palette application via API
├── tests/
│   ├── test_data_integrity.py  # Data quality checks
│   ├── test_api_endpoints.py   # Superset API availability
│   ├── test_rls_rules.py       # RLS filtering validation
│   ├── test_colour_theme.py    # Palette consistency
│   └── test_dashboard_export.py # Dashboard-as-Code validation
├── docs/
│   ├── architecture.md         # System architecture
│   ├── mcp_setup.md            # Claude MCP connection guide
│   ├── rls_guide.md            # RLS implementation details
│   └── before_after.md         # Manual vs AI-automated comparison
└── screenshots/
    ├── dashboard_overview.png
    ├── rls_demo.gif
    └── mcp_interaction.png
```

## Key Metrics

| What | Manual BI Build | AI-Automated (This Project) |
|------|----------------|----------------------------|
| Dashboard creation | 2-3 days | ~30 minutes |
| RLS configuration | 2-4 hours | ~5 minutes (scripted) |
| Theme customisation | 1-2 hours | ~2 minutes (API) |
| Reproducibility | Manual screenshots | `docker compose up` + Git |

## Tech Stack

| Layer | Tool |
|-------|------|
| Data Store | PostgreSQL 16 |
| BI Platform | Apache Superset 5.0+ |
| AI Integration | Claude MCP (Model Context Protocol) |
| Data Generation | Python (pandas, numpy, Faker) |
| Orchestration | Docker Compose |
| Version Control | Git + GitHub |
| Testing | pytest |

## Related Projects

| Case | Focus | Repo |
|------|-------|------|
| Case 1 | Power BI × Healthcare KPI | [powerbi-claude-health](https://github.com/yujiyamane/powerbi-claude-health) |
| Case 2 | Streamlit × ED Performance | [streamlit-claude-health](https://github.com/yujiyamane/streamlit-claude-health) |
| Case 3 | Life OS × Personal Analytics | [lifeos-claude-dashboard](https://github.com/yujiyamane/lifeos-claude-dashboard) |
| **Case 4** | **Superset × Claude MCP × RLS** | **This repo** |

## Author

**Yuji Yamane** — BI Developer @ NSW Health | AI-augmented analytics
