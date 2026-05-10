import subprocess
import sys

ROLES = ["LHD_Manager", "Ward_Nurse"]

USERS = [
    ("lhd_manager_syd", "Firstname", "LHD", "lhd_manager@health.nsw.gov.au", "password", "LHD_Manager"),
    ("ward_nurse_ed1", "Ward", "Nurse", "ward_nurse@health.nsw.gov.au", "password", "Ward_Nurse"),
]


def run_in_container(python_code):
    cmd = ["docker", "exec", "superset_app", "/app/.venv/bin/python", "-c", python_code]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  STDERR: {result.stderr[:500]}")
    return result.stdout.strip(), result.returncode


def create_roles():
    print("Creating roles...")
    code = """
from superset import create_app
from superset.extensions import db
from flask_appbuilder.security.sqla.models import Role

app = create_app()
with app.app_context():
    sm = app.appbuilder.sm
    for role_name in {roles}:
        existing = sm.find_role(role_name)
        if existing:
            print(f"Role already exists: {{role_name}}")
        else:
            sm.add_role(role_name)
            print(f"Role created: {{role_name}}")
    db.session.commit()
""".format(roles=repr(ROLES))

    stdout, rc = run_in_container(code)
    print(f"  {stdout}" if stdout else "  (no output)")
    return rc == 0


def create_users():
    print("Creating test users...")
    for username, first, last, email, password, role in USERS:
        code = f"""
from superset import create_app
from superset.extensions import db

app = create_app()
with app.app_context():
    sm = app.appbuilder.sm
    existing = sm.find_user(username='{username}')
    if existing:
        print(f"User already exists: {username}")
    else:
        role = sm.find_role('{role}')
        user = sm.add_user(
            username='{username}',
            first_name='{first}',
            last_name='{last}',
            email='{email}',
            role=role,
            password='{password}'
        )
        if user:
            print(f"User created: {username}")
        else:
            print(f"Failed to create: {username}")
    db.session.commit()
"""
        stdout, rc = run_in_container(code)
        print(f"  {stdout}" if stdout else f"  (no output for {username})")


def verify_roles():
    print("Verifying roles in database...")
    code = """
from superset import create_app
app = create_app()
with app.app_context():
    sm = app.appbuilder.sm
    roles = sm.get_all_roles()
    names = [r.name for r in roles]
    print(','.join(names))
"""
    stdout, _ = run_in_container(code)
    role_names = stdout.split(",") if stdout else []
    print(f"  Roles found: {role_names}")
    return role_names


def main():
    if create_roles():
        print("  Roles created successfully")
    create_users()
    roles = verify_roles()
    assert "LHD_Manager" in roles, "LHD_Manager role not found"
    assert "Ward_Nurse" in roles, "Ward_Nurse role not found"
    print("\nRBAC setup complete.")


if __name__ == "__main__":
    main()
