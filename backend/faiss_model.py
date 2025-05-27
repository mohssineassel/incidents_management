import numpy as np
import faiss
import json
import re
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer

# 1️⃣ --- Connexion PostgreSQL ---
DATABASE_URL = "postgresql://yassine:password@localhost/incidents_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True)
    description = Column(Text)
    embedding = Column(Text)

Base.metadata.create_all(bind=engine)

# 2️⃣ --- BERT + Prétraitement ---
model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384

def nettoyer_texte(texte):
    texte = texte.lower()
    texte = re.sub(r'[^\w\s]', '', texte)
    texte = re.sub(r'\s+', ' ', texte).strip()
    return texte

def encoder_description(description):
    description = nettoyer_texte(description)
    vecteur = model.encode([description])[0]
    return vecteur.astype('float32')

# 3️⃣ --- FAISS + Mapping ---
index_faiss = faiss.IndexFlatL2(dimension)
faiss_to_postgres = {}

# 4️⃣ --- Ajouter un incident ---
def ajouter_incident(description):
    vecteur = encoder_description(description)
    # Stocker dans PostgreSQL
    session = SessionLocal()
    incident = Incident(description=description, embedding=json.dumps(vecteur.tolist()))
    session.add(incident)
    session.commit()
    db_id = incident.id
    session.close()
    # Indexer dans FAISS
    index_faiss.add(np.array([vecteur]))
    faiss_id = index_faiss.ntotal - 1
    faiss_to_postgres[faiss_id] = db_id
    print(f"Incident ajouté : {description} (DB ID {db_id} / FAISS ID {faiss_id})")

# 5️⃣ --- Recherche similaire ---
def rechercher_incidents(query, k=5):
    vecteur_query = encoder_description(query).reshape(1, -1)
    distances, indices = index_faiss.search(vecteur_query, k)
    session = SessionLocal()
    for faiss_idx, dist in zip(indices[0], distances[0]):
        db_id = faiss_to_postgres.get(faiss_idx)
        if db_id is not None:
            incident = session.query(Incident).filter_by(id=db_id).first()
            if incident:
                print(f"Incident #{incident.id}: {incident.description}")
                print(f"Distance: {dist:.4f}")
                print("-" * 40)
    session.close()

# 6️⃣ --- Option : Sauvegarde/Chargement FAISS ---
def sauvegarder_faiss(fichier="faiss_index.bin"):
    faiss.write_index(index_faiss, fichier)
    print("Index FAISS sauvegardé.")

def charger_faiss(fichier="faiss_index.bin"):
    global index_faiss
    index_faiss = faiss.read_index(fichier)
    print("Index FAISS chargé.")
