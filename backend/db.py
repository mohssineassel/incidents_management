from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2



DATABASE_URL = "postgresql://postgres:test@localhost/Incidents"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# # class Incident(Base):
# #     __tablename__ = "incidents"
# #     id = Column(Integer, primary_key=True, index=True)
# #     description = Column(Text)
# #     embedding = Column(Text)  # Stockage temporaire en JSON string

# # Base.metadata.create_all(bind=engine)

# engine = create_engine(DATABASE_URL)

# # Création de la session
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base pour les modèles
# Base = declarative_base()


# conn = psycopg2.connect(
#     dbname="Incidents",
#     user="postgres",
#     password="test",   
#     host="localhost",
#     port="5432"
# )

# cur = conn.cursor()

# cur.execute("SELECT * FROM incidents;")
# rows = cur.fetchall()
# for row in rows:
#     print(row)
# # Fermeture de la connexion
# cur.close()
# conn.close()

# incidents = [
#     ("Erreur 500 sur la page login", "Web", "Élevé", "Critique"),
#     ("Serveur SMTP non accessible", "Email", "Moyen", "Haute"),
#     ("Problème d'impression", "Support", "Faible", "Faible"),
#     ("Perte de connectivité réseau", "Infrastructure", "Élevé", "Moyenne"),
# ]

# # Requête SQL d'insertion
# insert_query = """
# INSERT INTO incidents (description, category, impact, priority)
# VALUES (%s, %s, %s, %s);
# """

# # Insertion en lot
# cur.executemany(insert_query, incidents)
# conn.commit()

# print("✅ Données insérées avec succès.")

# cur.close()
# conn.close()