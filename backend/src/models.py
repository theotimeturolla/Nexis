from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
# 👇 C'est cette ligne qui change (ajout de 'src.')
from src.database import Base 

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, index=True)
    source = Column(String)
    topic = Column(String)
    published_date = Column(DateTime, nullable=True)
    
    content = Column(Text, nullable=True)
    
    sentiment_score = Column(Float)
    sentiment_label = Column(String)
    
    summary = Column(Text, nullable=True)
    reliability_score = Column(Integer, default=50)
    source_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())