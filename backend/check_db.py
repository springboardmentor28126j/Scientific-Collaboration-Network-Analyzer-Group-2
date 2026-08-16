import psycopg2

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/internship"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'user'
        ORDER BY ordinal_position
    """)
    print("CONNECTED OK")
    print("\nuser table columns:")
    for row in cur.fetchall():
        print(" ", row)

    cur.execute("SELECT user_id, email, role, auth_provider, google_sub, is_email_verified FROM \"user\"")
    print("\nExisting users:")
    for row in cur.fetchall():
        print(" ", row)

    cur.close()
    conn.close()
except Exception as e:
    print("CONNECTION FAILED")
    print(type(e).__name__, "-", e)