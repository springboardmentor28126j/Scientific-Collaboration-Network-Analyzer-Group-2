from fastapi import APIRouter

router = APIRouter()


researchers = []


@router.post("/researchers")
def create_researcher(researcher: dict):
    researchers.append(researcher)
    return {
        "message": "Researcher added successfully",
        "researcher": researcher
    }


@router.get("/researchers")
def get_researchers():
    return researchers