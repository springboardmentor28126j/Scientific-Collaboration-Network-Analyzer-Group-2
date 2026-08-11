from typing import List, Optional
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1/publications",
    tags=["Publications"],
)

class PublicationSchema(BaseModel):
    title: str
    abstract: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    conference: Optional[str] = None
    publication_year: Optional[int] = 2024
    publication_type: Optional[str] = "Journal Article"
    status: Optional[str] = "Published"
    url: Optional[str] = None
    citation_count: Optional[int] = 0

# Mock DB store for backend API
publications_db = [
    {
        "id": 1,
        "title": "Graph Neural Networks for Collaboration Prediction",
        "authors": "A. Sharma, P. Nair",
        "abstract": "Scientific collaboration prediction is essential for understanding research dynamics.",
        "journal": "IEEE Transactions on Knowledge and Data Engineering",
        "conference": "IEEE TKDE 2024",
        "publication_year": 2024,
        "publication_type": "Journal Article",
        "status": "Published",
        "url": "https://doi.org/10.1109/TKDE.2024.3210451",
        "doi": "10.1109/TKDE.2024.3210451",
        "citation_count": 45,
        "file_name": "GNN_Collaboration_Prediction.pdf",
    },
    {
        "id": 2,
        "title": "Optimizing Centrality Algorithms in Large Social Graphs",
        "authors": "R. Kumar, S. Patel",
        "abstract": "Centrality metrics identify key hubs in academic networks.",
        "journal": "ACM Computing Surveys",
        "conference": "ACM CS 2023",
        "publication_year": 2023,
        "publication_type": "Survey Article",
        "status": "Published",
        "url": "https://doi.org/10.1145/3541289.3541290",
        "doi": "10.1145/3541289.3541290",
        "citation_count": 89,
        "file_name": "Centrality_Optimization.pdf",
    }
]

@router.get("/", response_model=List[dict])
def get_all_publications():
    return publications_db

@router.get("/{pub_id}")
def get_publication(pub_id: int):
    for pub in publications_db:
        if pub["id"] == pub_id:
            return pub
    raise HTTPException(status_code=404, detail="Publication not found")

@router.post("/", status_code=201)
def create_publication(pub: PublicationSchema):
    new_id = len(publications_db) + 1
    new_pub = pub.dict()
    new_pub["id"] = new_id
    new_pub["authors"] = "Registered Author"
    publications_db.append(new_pub)
    return new_pub

@router.put("/{pub_id}")
def update_publication(pub_id: int, pub: PublicationSchema):
    for idx, existing in enumerate(publications_db):
        if existing["id"] == pub_id:
            updated = pub.dict()
            updated["id"] = pub_id
            publications_db[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Publication not found")

@router.delete("/{pub_id}")
def delete_publication(pub_id: int):
    global publications_db
    publications_db = [p for p in publications_db if p["id"] != pub_id]
    return {"message": "Publication deleted"}

@router.post("/{pub_id}/upload")
def upload_file(pub_id: int, file: UploadFile = File(...)):
    for pub in publications_db:
        if pub["id"] == pub_id:
            pub["file_name"] = file.filename
            return {"message": "File uploaded successfully", "file_name": file.filename}
    return {"message": "File uploaded successfully", "file_name": file.filename}
