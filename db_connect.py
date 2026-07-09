import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="scientific_collabration",
        user="postgres",
        password="Divya@123",
        port="5432"
    )

    print("Database connected successfully!")

    cur = conn.cursor()
    cur.execute("SELECT * FROM research_papers;")

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()

except Exception as e:
    print("Error:", e)