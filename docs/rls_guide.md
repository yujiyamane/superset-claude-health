# Row-Level Security Implementation Guide

## Overview

Superset's Row-Level Security (RLS) automatically appends SQL WHERE clauses to queries based on the current user's role. This project implements two RLS rules:

| Rule | Role | Clause | Effect |
|------|------|--------|--------|
| LHD Manager Filter | LHD_Manager | `hospital_id IN (SELECT hospital_id FROM dim_hospital WHERE lhd_name = ...)` | User sees only their LHD's data |
| Ward Nurse Filter | Ward_Nurse | `ward_id = ...` | User sees only their ward's data |

## Implementation

### 1. Role Creation (`scripts/setup_roles.py`)

Roles are created via the Superset Python API inside the Docker container:

```bash
python scripts/setup_roles.py
```

This creates:
- `LHD_Manager` — district-level access
- `Ward_Nurse` — ward-level access
- Test users: `lhd_manager_syd`, `ward_nurse_ed1`

### 2. RLS Rule Creation (`scripts/setup_rls.py`)

Rules are created via the Superset REST API (`/api/v1/rowlevelsecurity/`):

```bash
python scripts/setup_rls.py
```

### 3. Rule Verification

```bash
python -m pytest tests/test_rls_rules.py -v
```

Tests verify:
- At least 2 RLS rules exist in Superset
- `LHD_Manager` role exists in the metadata database
- `Ward_Nurse` role exists in the metadata database

## How RLS Works in Superset 5.0

1. User authenticates → Superset resolves their roles
2. For each query against a protected table, Superset checks for matching RLS rules
3. Matching rules' clauses are AND-joined to the WHERE clause
4. The modified SQL is executed against PostgreSQL

## Extending RLS

To add a new role scope (e.g., hospital-level):

```python
create_rls_rule(
    name="Hospital Admin Filter",
    clause="hospital_id = {{ current_username() | int }}",
    table_ids=[fact_dataset_id],
    group_key="hospital",
)
```

Then create a `Hospital_Admin` role and assign it to users.

## Important Notes

- RLS clauses support Jinja2 templating via `ENABLE_TEMPLATE_PROCESSING = True`
- The `current_username()` function returns the logged-in user's username
- Admin users bypass all RLS rules by default
- Test with non-admin accounts to verify filtering works
