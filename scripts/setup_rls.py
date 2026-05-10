import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.superset_client import api_get, api_post


def get_dataset_id(table_name):
    data = api_get("/api/v1/dataset/")
    for ds in data.get("result", []):
        if ds.get("table_name") == table_name:
            return ds["id"]
    raise RuntimeError(f"Dataset not found: {table_name}")


def rls_rule_exists(name):
    data = api_get("/api/v1/rowlevelsecurity/")
    for rule in data.get("result", []):
        if rule.get("name") == name:
            return rule["id"]
    return None


def get_role_id(role_name):
    data = api_get("/api/v1/rowlevelsecurity/related/roles")
    for role in data.get("result", []):
        if role.get("text") == role_name or role.get("value", {}).get("name") == role_name:
            v = role.get("value")
            if isinstance(v, dict):
                return v.get("id")
            return v
    return None


def create_rls_rule(name, clause, table_ids, group_key, filter_type="Regular"):
    existing = rls_rule_exists(name)
    if existing:
        print(f"  RLS rule already exists: {name} id={existing}")
        return existing

    payload = {
        "name": name,
        "clause": clause,
        "filter_type": filter_type,
        "group_key": group_key,
        "roles": [],
        "tables": table_ids,
    }

    result = api_post("/api/v1/rowlevelsecurity/", payload)
    rid = result.get("id")
    print(f"  RLS rule created: {name} id={rid}")
    return rid


def main():
    print("Getting dataset IDs...")
    fact_id = get_dataset_id("fact_ed_visits")
    print(f"  fact_ed_visits: {fact_id}")

    print("\nCreating RLS rules...")

    create_rls_rule(
        name="LHD Manager Filter",
        clause="hospital_id IN (SELECT hospital_id FROM dim_hospital WHERE lhd_name = '{{ current_username() }}')",
        table_ids=[fact_id],
        group_key="lhd",
        filter_type="Regular",
    )

    create_rls_rule(
        name="Ward Nurse Filter",
        clause="ward_id = {{ current_username() | int }}",
        table_ids=[fact_id],
        group_key="ward",
        filter_type="Regular",
    )

    count = api_get("/api/v1/rowlevelsecurity/")["count"]
    print(f"\nRLS setup complete. Total rules: {count}")
    return count


if __name__ == "__main__":
    main()
