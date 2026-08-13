"""Diagnostic: does the shared DB's project_members table already have
status/invited_by_id/responded_at columns (and a projectmemberstatus
enum type) from the reference project's own migration chain, before we
write a migration for the invite/accept handshake feature?
Run from backend/: python check_project_members_columns.py
Safe to delete afterwards.
"""
from app.core.config import settings
from sqlalchemy import create_engine, inspect, text

e = create_engine(settings.DATABASE_URL)
insp = inspect(e)

print("--- project_members columns (all) ---")
for c in insp.get_columns("project_members"):
    print(f"  {c['name']}: type={c['type']}  nullable={c['nullable']}  default={c.get('default')}")

print()
print("--- native enum type labels (if any exist) ---")
with e.connect() as conn:
    for enum_name in ["projectmemberstatus"]:
        rows = conn.execute(
            text(
                "SELECT e.enumlabel FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid "
                "WHERE t.typname = :name ORDER BY e.enumsortorder"
            ),
            {"name": enum_name},
        ).fetchall()
        print(f"  {enum_name}: {[r[0] for r in rows] if rows else '(does not exist)'}")
