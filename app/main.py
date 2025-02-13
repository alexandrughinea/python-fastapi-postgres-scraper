# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

# SQLAlchemy imports
from sqlalchemy.orm import Session
from sqlalchemy import or_, text, select, func

# Project imports
from . import auth, db
from .db import ScrapedData, SessionLocal
from .scraper import scrape_url, scrape_batch
from .embeddings import embedder

# Scheduler
from apscheduler.schedulers.background import BackgroundScheduler

# Standard library
from datetime import datetime
from typing import List, Optional

# Pydantic
from pydantic import BaseModel

app = FastAPI()

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

class SimilaritySearch(BaseModel):
    text: str
    limit: int = 5
    threshold: float = 0.7

@app.get("/data/similar/{data_id}", dependencies=[Depends(auth.get_api_key)])
def find_similar_by_id(
    data_id: int,
    limit: int = Query(5, description="Number of similar items to return"),
    threshold: float = Query(0.7, description="Minimum similarity score"),
    db: Session = Depends(get_db)
):
    """Find similar content based on existing entry ID"""
    base_item = db.query(ScrapedData).filter(ScrapedData.id == data_id).first()
    if not base_item:
        return JSONResponse(status_code=404, content={"detail": "Content not found"})

    query = select(
        ScrapedData,
        func.cosine_similarity(ScrapedData.embedding, base_item.embedding).label('similarity')
    ).filter(
        ScrapedData.id != data_id,
        func.cosine_similarity(ScrapedData.embedding, base_item.embedding) > threshold
    ).order_by(
        text('similarity DESC')
    ).limit(limit)

    results = db.execute(query).all()
    
    return JSONResponse(content=[{
        "id": item.ScrapedData.id,
        "url": item.ScrapedData.url,
        "similarity": float(item.similarity),
        "scraped_at": item.ScrapedData.scraped_at
    } for item in results])

@app.post("/data/search", dependencies=[Depends(auth.get_api_key)])
def search_similar_content(
    search: SimilaritySearch,
    db: Session = Depends(get_db)
):
    """Search for similar content using text input"""
    # Generate embedding for search text
    embedding = embedder.generate(search.text)
    
    query = select(
        ScrapedData,
        func.cosine_similarity(ScrapedData.embedding, embedding).label('similarity')
    ).filter(
        func.cosine_similarity(ScrapedData.embedding, embedding) > search.threshold
    ).order_by(
        text('similarity DESC')
    ).limit(search.limit)

    results = db.execute(query).all()
    
    return [{
        "id": item.ScrapedData.id,
        "url": item.ScrapedData.url,
        "similarity": float(item.similarity),
        "scraped_at": item.ScrapedData.scraped_at,
        "content": item.ScrapedData.content[:200] + "..."  # Preview only
    } for item in results]


@app.get("/data/", dependencies=[Depends(auth.get_api_key)])
def get_scraped_data(
    search: Optional[str] = Query(None, description="Search in content"),
    url: Optional[str] = Query(None, description="Filter by URL"),
    limit: int = Query(100, description="Max number of results"),
    offset: int = Query(0, description="Results offset"),
    db: Session = Depends(get_db)
):
    """Get scraped data with optional filtering."""
    query = db.query(ScrapedData)
    if search:
        query = query.filter(ScrapedData.content.ilike(f"%{search}%"))
    if url:
        query = query.filter(ScrapedData.url == url)
    results = query.offset(offset).limit(limit).all()
    
    return JSONResponse(content=[{
        "id": item.id,
        "url": item.url,
        "content": item.content[:200] + "...",  
        "scraped_at": item.scraped_at
    } for item in results])

@app.post("/scrape/", dependencies=[Depends(auth.get_api_key)])
def trigger_scrape(urls: List[str], db: Session = Depends(get_db)):
    results = []
    for url in urls:
        success = scrape_url(url, db)
        results.append({"url": url, "success": success})
    return results

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

@app.on_event("startup")
async def startup_event():
    db.Base.metadata.create_all(bind=db.engine)
