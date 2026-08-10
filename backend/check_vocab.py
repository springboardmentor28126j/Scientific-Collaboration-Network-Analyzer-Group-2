"""Diagnostic: exact current status/role vocabulary + types, needed before
rewriting model code to match the DB as-is (no ALTER TABLE will be run).
Run from backend/: python check_vocab.py
Safe to delete afterwards.
"""
from app.core.config import settings
from sqlalchemy import create_engine, inspect, text

e = create_engine(settings.DATABASE_URL)
insp = inspect(e)

for table, col in [("projects", "status"), ("project_members", "role")]:
    print(f"--- {table}.{col} ---")
    for c in insp.get_columns(table):
        if c["name"] == col:
            print(f"  type: {c['type']}  nullable: {c['nullable']}  default: {c.get('default')}")
    with e.connect() as conn:
        rows = conn.execute(text(f"SELECT DISTINCT {col} FROM {table}")).fetchall()
        print(f"  distinct values in use: {[r[0] for r in rows]}")
    print()

print("--- native enum type labels (if any still exist) ---")
with e.connect() as conn:
    for enum_name in ["projectstatus", "projectmemberrole"]:
        rows = conn.execute(
            text(
                "SELECT e.enumlabel FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid "
                "WHERE t.typname = :name ORDER BY e.enumsortorder"
            ),
            {"name": enum_name},
        ).fetchall()
        print(f"  {enum_name}: {[r[0] for r in rows] if rows else '(does not exist -- plain varchar)'}")
