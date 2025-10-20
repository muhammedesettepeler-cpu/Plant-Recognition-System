from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Plant(Base):
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    scientific_name = Column(String(255), unique=True, index=True, nullable=False)
    scientific_name_full = Column(String(300))  # With author
    common_name = Column(String(255))  # Primary common name
    common_names = Column(JSON)  # All common names (list)
    family = Column(String(100), index=True)
    genus = Column(String(100))
    description = Column(Text)
    habitat = Column(Text)
    care_instructions = Column(Text)
    characteristics = Column(JSON)  # Leaf shape, flower color, etc.
    image_urls = Column(JSON)  # List of image URLs
    weaviate_id = Column(String(255))
    gbif_id = Column(String(100))  # Global Biodiversity Information Facility ID
    plantnet_verified = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserQuery(Base):
    __tablename__ = "user_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    query_type = Column(String(50))
    query_text = Column(Text)
    response = Column(Text)
    confidence_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
