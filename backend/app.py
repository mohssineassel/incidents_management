from fastapi import FastAPI , Depends
from pydantic import BaseModel
from db import SessionLocal
from sqlalchemy.orm import Session
import db, models
from faiss_index import index, encode, build_index
from models import Incident

app = FastAPI()
build_index()
models.Base.metadata.create_all(bind=db.engine) 

class Query(BaseModel):
    description: str

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.get("/incidents/")
def read_incidents(db: Session = Depends(get_db)):
    return db.query(models.Incident).all()

class Item(BaseModel):
    name: str
    description: str 
    price: float



@app.post("/search/")
def search_similar(query: Query):
    vec = encode(query.description).reshape(1, -1)
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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/")
def read_items():
    items = [Item(name="Foo", description="A new item", price=45.2), 
             Item(name="Bar", description="Another item", price=10.5)]
    return items