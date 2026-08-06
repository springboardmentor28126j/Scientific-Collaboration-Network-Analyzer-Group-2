"""Add idempotent 2022-2026 sample publications for analytics demonstrations."""

from datetime import date

from app.database import SessionLocal
from app.models import Institution, Publication, Researcher


YEARS = range(2022, 2027)
STATUSES = ("published", "submitted", "draft", "archived", "published")
TYPES = ("Journal Article", "Conference Paper", "Book Chapter", "Journal Article", "Conference Paper")


def main():
    db = SessionLocal()
    try:
        institutions = db.query(Institution).order_by(Institution.id).all()
        researchers = db.query(Researcher).order_by(Researcher.id).all()
        if not institutions or not researchers:
            raise RuntimeError("Create at least one institution and researcher before adding analytics sample data.")

        added = 0
        for year_index, year in enumerate(YEARS):
            for item_index in range(5):
                doi = f"10.5555/scna-analytics-{year}-{item_index + 1}"
                if db.query(Publication).filter(Publication.doi == doi).first():
                    continue
                institution = institutions[(year_index + item_index) % len(institutions)]
                institution_researchers = [researcher for researcher in researchers if researcher.institution_id == institution.id]
                authors = institution_researchers or researchers
                primary_author = authors[item_index % len(authors)]
                secondary_author = authors[(item_index + 1) % len(authors)]
                publication = Publication(
                    title=f"Analytics Demonstration Study {year}-{item_index + 1}",
                    abstract="Sample record added to demonstrate reporting and analytics charts.",
                    doi=doi,
                    publication_type=TYPES[item_index],
                    status=STATUSES[item_index],
                    publication_date=date(year, 2 + item_index * 2, 10 + item_index),
                    journal_or_venue="SCNA Research Forum",
                    institution_id=institution.id,
                )
                publication.authors = [primary_author] if primary_author.id == secondary_author.id else [primary_author, secondary_author]
                db.add(publication)
                added += 1
        db.commit()
        print(f"Added {added} analytics demonstration publications for 2022-2026.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
