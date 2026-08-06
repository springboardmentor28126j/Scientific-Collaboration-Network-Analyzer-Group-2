"""Bring the demonstration dataset to a balanced minimum for analytics screens.

This script is idempotent: rerunning it adds only missing balancing records.
"""

from datetime import date

from app.database import SessionLocal
from app.models import Collaboration, Conference, ConferenceParticipation, Institution, Publication, Researcher


MIN_RESEARCHERS = 3
MIN_PUBLICATIONS = 5
STATUS_VALUES = ("published", "submitted", "draft", "archived", "published")
TYPE_VALUES = ("Journal Article", "Conference Paper", "Book Chapter", "Journal Article", "Conference Paper")


def main():
    db = SessionLocal()
    added = {"researchers": 0, "publications": 0, "collaborations": 0, "conferences": 0, "participations": 0}
    try:
        institutions = db.query(Institution).order_by(Institution.id).all()
        for institution in institutions:
            researchers = db.query(Researcher).filter(Researcher.institution_id == institution.id).order_by(Researcher.id).all()
            for position in range(len(researchers) + 1, MIN_RESEARCHERS + 1):
                researcher = Researcher(
                    full_name=f"{institution.name} Researcher {position}",
                    department="Research and Innovation",
                    skills="Data analysis, scientific collaboration",
                    research_interest="Research networks and analytics",
                    designation="Research Fellow",
                    institution_id=institution.id,
                )
                db.add(researcher)
                researchers.append(researcher)
                added["researchers"] += 1
            db.flush()

            publications = db.query(Publication).filter(Publication.institution_id == institution.id).order_by(Publication.id).all()
            for position in range(len(publications) + 1, MIN_PUBLICATIONS + 1):
                doi = f"10.5555/scna-balanced-{institution.id}-{position}"
                if db.query(Publication).filter(Publication.doi == doi).first():
                    continue
                publication = Publication(
                    title=f"Collaborative Research Analytics Study {institution.id}-{position}",
                    abstract="Balancing record for the Scientific Collaboration Network Analyzer demonstration dataset.",
                    doi=doi,
                    publication_type=TYPE_VALUES[(institution.id + position) % len(TYPE_VALUES)],
                    status=STATUS_VALUES[(institution.id + position) % len(STATUS_VALUES)],
                    publication_date=date(2022 + ((institution.id + position) % 5), 2 + ((position - 1) % 5) * 2, 10 + position),
                    journal_or_venue="Scientific Collaboration Review",
                    institution_id=institution.id,
                )
                publication.authors = [researchers[(position - 1) % len(researchers)], researchers[position % len(researchers)]]
                db.add(publication)
                publications.append(publication)
                added["publications"] += 1
            db.flush()

            for position in range(len(researchers) - 1):
                first, second = researchers[position], researchers[position + 1]
                exists = db.query(Collaboration).filter(
                    ((Collaboration.researcher1_id == first.id) & (Collaboration.researcher2_id == second.id)) |
                    ((Collaboration.researcher1_id == second.id) & (Collaboration.researcher2_id == first.id))
                ).first()
                if not exists:
                    db.add(Collaboration(researcher1_id=first.id, researcher2_id=second.id, publication_id=publications[position % len(publications)].id, project="Analytics Data Enrichment"))
                    added["collaborations"] += 1

        current_conferences = db.query(Conference).count()
        for position in range(current_conferences + 1, 16):
            year = 2022 + ((position - 1) % 5)
            db.add(Conference(name=f"Scientific Collaboration Forum {year}", location="International Research Hub", start_date=date(year, 9, 10), end_date=date(year, 9, 12)))
            added["conferences"] += 1
        db.flush()

        conferences = db.query(Conference).order_by(Conference.id).all()
        researchers = db.query(Researcher).order_by(Researcher.id).all()
        for index, researcher in enumerate(researchers):
            conference = conferences[index % len(conferences)]
            exists = db.query(ConferenceParticipation).filter(ConferenceParticipation.researcher_id == researcher.id, ConferenceParticipation.conference_id == conference.id).first()
            if not exists:
                db.add(ConferenceParticipation(researcher_id=researcher.id, conference_id=conference.id, presentation_title="Research Collaboration Analytics"))
                added["participations"] += 1

        db.commit()
        print(
            "Added " + ", ".join(f"{key}={value}" for key, value in added.items()) + "."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
