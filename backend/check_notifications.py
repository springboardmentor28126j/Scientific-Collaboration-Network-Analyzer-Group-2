"""Diagnostic: check whether the pre-existing 'notifications' table (from
the earlier schema drift) will collide with migration 0018_notifications.py,
which does CREATE TABLE notifications. Run from backend/: python check_notifications.py
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

if "notifications" in insp.get_table_names():
    print("--- notifications columns (TABLE ALREADY EXISTS) ---")
    for col in insp.get_columns("notifications"):
        print(f"  {col['name']:<20} {str(col['type']):<20} nullable={col['nullable']}")
    with e.connect() as conn:
        n = conn.execute(text("SELECT COUNT(*) FROM notifications")).scalar()
        print(f"\n  row count: {n}")
        if n:
            print("  sample rows:")
            for r in conn.execute(text("SELECT * FROM notifications LIMIT 5")).fetchall():
                print("   ", r)
else:
    print("--- notifications table does NOT exist -- migration 0018 will create it cleanly ---")
