from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Plant(Base):
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    scientific_name = Column(String(255), unique=True, index=True)
    common_name = Column(String(255))
    family = Column(String(100))
    description = Column(Text)
    habitat = Column(Text)
    care_instructions = Column(Text)
    image_urls = Column(JSON)
    weaviate_id = Column(String(255))
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
