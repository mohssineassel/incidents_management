

import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from db import SessionLocal, Base
from models import Incident

# Modèle BERT (MiniLM pour la performance)
model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384  # Dimension du modèle
index = faiss.IndexFlatL2(dimension)  # FAISS en L2 (cosinus possible avec normalisation)

def build_index():
    """Recharge les vecteurs depuis la base PostgreSQL et les insère dans l'index FAISS"""
    session = SessionLocal()
    try:
        incidents = session.query(Incident).all()
        vectors = []

        for inc in incidents:
            if inc.embedding:
                try:
                    embedding = np.array(json.loads(inc.embedding)).astype('float32')
                    vectors.append(embedding)
                except Exception as e:
                    print(f"Erreur d'embedding pour l'incident {inc.id} : {e}")

        if vectors:
            array = np.vstack(vectors)  # plus sûr que np.array si liste de vecteurs
            index.add(array)
            print(f"{len(vectors)} vecteurs ajoutés à l'index FAISS.")
        else:
            print("Aucun vecteur valide trouvé pour l'indexation.")

    except Exception as e:
        print(f"Erreur lors de la construction de l'index : {e}")

    finally:
        session.close()

def encode(text):
    """Encode une description en vecteur BERT"""
    vec = model.encode([text])
    return vec[0].astype('float32')

