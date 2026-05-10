# Manual vs AI-Automated: Before & After

## The Traditional BI Build Process

Building a healthcare dashboard with RLS manually involves:

### Before (Manual)

| Task | Time | Pain Points |
|------|------|-------------|
| Schema design + SQL | 2-4 hours | Iterative ERD sessions, multiple revisions |
| Synthetic data generation | 3-5 hours | Getting realistic distributions right |
| Docker/Superset setup | 1-2 hours | Config files, admin setup, troubleshooting |
| Dataset registration (5 tables) | 30-60 min | Click through UI 5 times, set joins manually |
| Chart creation (12 charts) | 4-6 hours | Configure each chart type, tune formatting |
| Dashboard layout | 1-2 hours | Drag-and-drop grid, save/reload cycle |
| RBAC role setup | 1-2 hours | Navigate security UI, assign permissions |
| RLS configuration | 2-4 hours | SQL clause writing, testing with each user |
| Documentation | 1-2 hours | |
| **Total** | **~16-27 hours** | High context-switching cost |

### After (AI-Automated — This Project)

| Task | Script | Execution Time |
|------|--------|---------------|
| Schema + data generation | `data/generate_data.py` | 4.5 min (208K rows) |
| Docker setup | `docker-compose.yml` | ~2 min first run |
| Dataset registration | `scripts/setup_datasets.py` | <5 seconds |
| 12 charts | `scripts/create_charts.py` | <10 seconds |
| Dashboard assembly | `scripts/create_dashboard.py` | <5 seconds |
| RBAC roles + users | `scripts/setup_roles.py` | ~30 seconds |
| RLS rules | `scripts/setup_rls.py` | <5 seconds |
| **Total execution** | **All scripts** | **~8 minutes** |

## What AI Adds

Beyond raw speed, the AI-automated approach provides:

1. **Reproducibility** — `docker compose down -v && docker compose up -d && python scripts/load_data.py` rebuilds everything from scratch
2. **Version control** — Dashboard JSON, RLS rules, and chart configs are in Git
3. **TDD confidence** — 29 automated tests catch regressions
4. **Documentation as code** — `data/generate_data.py` is the authoritative spec for the data model

## What AI Cannot Replace

- Clinical domain expertise (knowing what metrics matter to ED clinicians)
- Stakeholder interviews to understand the "so what" of each chart
- UX design for the dashboard layout and colour choices
- Production security review of RLS clauses
- Data governance sign-off on synthetic vs real patient data

## Key Metrics

| Metric | Value |
|--------|-------|
| Lines of code | ~1,200 |
| Automated tests | 29 |
| Charts created | 12 |
| Data rows | 208,955 |
| Setup time (cold start) | ~10 minutes |
| Rebuild time (from scratch) | ~8 minutes |
