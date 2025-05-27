from fastapi import FastAPI
from pydantic import BaseModel
from db import SessionLocal, Incident
from faiss_index import encode_text, index, build_index
from ..app.inc import fetch_inc

app = FastAPI()
build_index()

class Query(BaseModel):
    description: str


@app.post("/search/")
def search_similar(query: Query):
    vec = encode_text(query.description).reshape(1, -1)
    distances, indices = index.search(vec, k=5)
    session = SessionLocal()
    results = []
    for idx in indices[0]:
        if idx < 0:
            continue
        incident = session.query(Incident).offset(idx).limit(1).first()
        results.append({"id": incident.id, "description": incident.description})
    session.close()
    return {"query": query.description, "similar": results}
