"""Full-DB diagnostic: list every table and its columns, so we can see
everything that may have drifted from a second migration chain being run
against this same database (see check_notifications.py's alembic_version
finding: '0019_google_signin', which isn't a revision this project has).

Run from backend/: python check_full_schema.py
Safe to delete afterwards.
"""
from app.core.config import settings
from sqlalchemy import create_engine, inspect, text

e = create_engine(settings.DATABASE_URL)
insp = inspect(e)

print("--- alembic_version ---")
with e.connect() as conn:
    for r in conn.execute(text("SELECT * FROM alembic_version")).fetchall():
        print(" ", r)
print()

print("--- all tables (name: columns) ---")
for t in sorted(insp.get_table_names()):
    cols = [c["name"] for c in insp.get_columns(t)]
    print(f"{t}:")
    print(f"  {cols}")
print()

print("--- users table columns in detail (checking for google_sub etc.) ---")
for col in insp.get_columns("users"):
    print(f"  {col['name']:<20} {str(col['type']):<20} nullable={col['nullable']}")
