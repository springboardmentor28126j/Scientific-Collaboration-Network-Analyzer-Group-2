"""Replace temporary institution-based demonstration researcher names."""

from app.database import SessionLocal
from app.models import Researcher


NAMES = {
    24: "Wei Ming Tan", 25: "Aisha Rahman", 26: "Kavita Iyer",
    27: "Olivia Bennett", 28: "Marcus Hill", 29: "Sofia Turner",
    30: "Daniel Kim", 31: "Sofia Martinez", 32: "Ethan Park",
    33: "Lukas Meier", 34: "Elena Rossi", 35: "Nora Keller",
    36: "Amara Singh", 37: "Michael Chen", 38: "Grace Williams",
    39: "Li Wei", 40: "Zhang Min", 41: "Chen Yu",
    42: "Amelia Brown", 43: "Noah Wilson", 44: "Priya Kapoor",
}


def main():
    db = SessionLocal()
    try:
        updated = 0
        for researcher_id, name in NAMES.items():
            researcher = db.query(Researcher).filter(Researcher.id == researcher_id).first()
            if researcher and " Researcher " in researcher.full_name:
                researcher.full_name = name
                updated += 1
        db.commit()
        print(f"Renamed {updated} demonstration researchers.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
