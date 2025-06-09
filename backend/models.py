from sqlalchemy import Column, Integer, String
from db import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    category = Column(String)
    impact = Column(String)
    priority = Column(String)
    embedding = Column(String)  # Stockage temporaire en JSON string
