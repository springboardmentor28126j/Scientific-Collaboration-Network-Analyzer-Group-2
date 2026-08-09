import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

url = os.environ["DATABASE_URL"]
# psycopg needs plain postgresql://, not postgresql+psycopg://
url = url.replace("postgresql+psycopg://", "postgresql://")

conn = psycopg.connect(url)
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
print("TABLES:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT version_num FROM alembic_version")
print("ALEMBIC VERSION:", cur.fetchall())

for table in ["conferences", "conference_attendances", "publications", "publication_authors"]:
    cur.execute(f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    print(f"\n{table}:")
    for row in cur.fetchall():
        print(" ", row)

        cur.execute("""
    SELECT t.typname, e.enumlabel
    FROM pg_enum e
    JOIN pg_type t ON e.enumtypid = t.oid
    WHERE t.typname LIKE '%role%' OR t.typname LIKE '%status%'
    ORDER BY t.typname, e.enumsortorder
""")
for row in cur.fetchall():
    print(row)