import json
from db import SessionLocal
from models import Incident
from sentence_transformers import SentenceTransformer

# Chargement du modèle SBERT
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connexion à la base
session = SessionLocal()
incidents = session.query(Incident).all()

for inc in incidents:
    if inc.description and not inc.embedding:
        try:
            emb = model.encode(inc.description)
            emb_json = json.dumps(emb.tolist())
            inc.embedding = emb_json
            print(f"✅ Embedding enregistré pour incident ID {inc.id}")
        except Exception as e:
            print(f"❌ Erreur pour incident ID {inc.id} : {e}")

session.commit()
session.close()
print("✅ Tous les embeddings ont été générés et stockés.")
