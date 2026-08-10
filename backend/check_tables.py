"""One-off diagnostic: list all tables in the Supabase Postgres DB.
Run from the backend folder with the venv active:  python check_tables.py
Delete this file once you're done -- it's not part of the app.
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg://postgres:Group-1Infy123@db.cktzlxnzykebqfzcfnlr.supabase.co:5432/postgres?sslmode=require"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    rows = conn.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
    )
    for (name,) in rows:
        print(name)
