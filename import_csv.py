import csv
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="scientific_collabration",
    user="postgres",
    password="Divya@123",
    port="5432"
)

cur = conn.cursor()

with open("data/research_papers.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cur.execute("""
            INSERT INTO research_papers
            (title, authors, abstract, publication_year, source, doi)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row["title"],
            row["authors"],
            row["abstract"],
            int(row["publication_year"]),
            row["source"],
            row["doi"]
        ))

conn.commit()

print("CSV data imported successfully!")

cur.close()
conn.close()