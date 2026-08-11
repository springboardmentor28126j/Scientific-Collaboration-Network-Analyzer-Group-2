from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- 1. Import added
from app.api.routes.network import router as network_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as user_router
from app.api.routes.researchers import router as researcher_router
from app.api.routes.institutions import router as institution_router
from app.api.routes.departments import router as department_router
from app.api.routes import reports


from app.api.routes.publications import router as publication_router
from app.api.routes.conferences import router as conference_router

app = FastAPI(
    title="Scientific Collaboration Network Analyzer",
    version="1.0.0",
)

# <-- 2. CORS Middleware added
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Frontend will connect smoothly)
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(researcher_router)
app.include_router(institution_router)
app.include_router(department_router)
app.include_router(network_router)
app.include_router(publication_router)
app.include_router(conference_router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "message": "Scientific Collaboration Network Analyzer API"
    }
# --- DASHBOARD STATS & GRAPH ENDPOINTS ---

@app.get("/api/v1/network/stats")
def get_network_stats():
    return {
        "researchers_count": 1240,
        "publications_count": 3850,
        "collaboration_density": 0.74,
    }

@app.get("/api/v1/network/graph")
def get_graph_data(query: str = ""):
    nodes = [
        {"id": "1", "label": "Dr. Alice Smith", "role": "Principal Investigator"},
        {"id": "2", "label": "Dr. Bob Jones", "role": "Co-Author"},
        {"id": "3", "label": "Prof. Carol Vance", "role": "Reviewer"},
    ]
    edges = [
        {"source": "1", "target": "2", "weight": 5},
        {"source": "1", "target": "3", "weight": 2},
    ]
    
    if query:
        nodes = [n for n in nodes if query.lower() in n["label"].lower()]
        
    return {"nodes": nodes, "edges": edges}