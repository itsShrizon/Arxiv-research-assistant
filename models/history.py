from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True)
    query = Column(String)
    categories = Column(JSON)
    relevance_scores = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    paper_ids = Column(JSON)