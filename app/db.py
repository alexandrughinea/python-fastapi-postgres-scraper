from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ScrapedData(Base):
    __tablename__ = "scraped_data"
    id = Column(Integer, primary_key=True)
    url = Column(String)
    content = Column(Text)
    embedding = Column(Vector(settings.vector_dimension))
    scraped_at = Column(DateTime, default=datetime.utcnow)