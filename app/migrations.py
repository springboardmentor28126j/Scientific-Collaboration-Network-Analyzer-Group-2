"""Lightweight compatibility migrations for existing demo databases.

For a classroom project this keeps existing Supabase data working after a
feature update.  New production deployments should run versioned Alembic
migrations before starting the application.
"""
from sqlalchemy import inspect, text


def apply_compatibility_migrations(engine) -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    additions = {
        "researcher_id": "INTEGER",
        "institution_id": "INTEGER",
        "rejection_reason": "VARCHAR",
        "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
        "updated_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
    }
    with engine.begin() as connection:
        for name, sql_type in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {sql_type}"))
        # Indexes make account-to-workspace lookup and approval screens quick.
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_users_institution_id ON users (institution_id)"))
    if "audit_logs" in inspector.get_table_names():
        audit_columns = {column["name"] for column in inspector.get_columns("audit_logs")}
        with engine.begin() as connection:
            if "actor_role" not in audit_columns:
                connection.execute(text("ALTER TABLE audit_logs ADD COLUMN actor_role VARCHAR"))
            if "ip_address" not in audit_columns:
                connection.execute(text("ALTER TABLE audit_logs ADD COLUMN ip_address VARCHAR"))
