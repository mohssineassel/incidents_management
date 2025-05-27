

import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from db import SessionLocal, Incident

# Modèle BERT (MiniLM pour la performance)
model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384  # Dimension du modèle
index = faiss.IndexFlatL2(dimension)  # FAISS en L2 (cosinus possible avec normalisation)

def build_index():
    """Recharge les vecteurs depuis la base PostgreSQL et les insère dans FAISS"""
    session = SessionLocal()
    incidents = session.query(Incident).all()
    vectors = []
    for inc in incidents:
        embedding = np.array(json.loads(inc.embedding)).astype('float32')
        vectors.append(embedding)
    if vectors:
        index.add(np.array(vectors))
    session.close()

def encode(text):
    """Encode une description en vecteur BERT"""
    vec = model.encode([text])
    return vec[0].astype('float32')

