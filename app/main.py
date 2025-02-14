from fastapi import FastAPI, Depends, Query
from fastapi.responses import JSONResponse
import numpy as np
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel

from .db import SessionLocal, ScrapedData, Base
from .scraper import scrape_url, async_scrape_batch
from .embeddings import embedder
from . import auth

app = FastAPI()


def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


class SimilaritySearch(BaseModel):
    text: str
    limit: int = 5
    threshold: float = 0.7


class ScrapeRequest(BaseModel):
    urls: List[str]


@app.get("/v1/search", dependencies=[Depends(auth.get_api_key)])
def search_similar_content(
    text: str = Query(..., description="Text to search for similar content"),
    limit: int = Query(5, description="Number of similar items to return"),
    threshold: float = Query(0.7, description="Minimum similarity score"),
    db: Session = Depends(get_db),
):
    """Search for similar content using text input"""
    try:
        search_embedding = embedder.generate(text)
        all_data = db.query(ScrapedData).all()

        similarity_results = []
        for item in all_data:
            if item.embedding is not None:
                item_embedding = np.array(item.embedding)
                search_embedding_np = np.array(search_embedding)

                item_norm = np.linalg.norm(item_embedding)
                search_norm = np.linalg.norm(search_embedding_np)

                if item_norm > 0 and search_norm > 0:
                    # Calculate cosine similarity with the dot product between item_embedding and search_embedding_np
                    similarity = np.dot(item_embedding, search_embedding_np) / (
                        item_norm * search_norm
                    )

                    if similarity > threshold:
                        similarity_results.append(
                            {
                                "id": item.id,
                                "url": item.url,
                                "content": item.content[:200] + "...",
                                "similarity": float(similarity),
                            }
                        )

        similarity_results.sort(key=lambda x: x["similarity"], reverse=True)
        result_list = similarity_results[:limit]

        return result_list
    except Exception as e:
        print(f"Search error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An error occurred during the search. Please try again with different parameters."
            },
        )

    return result_list


@app.get("/v1/data/{data_id}", dependencies=[Depends(auth.get_api_key)])
def get_scraped_data_by_id(data_id: int, db: Session = Depends(get_db)):
    """Get a specific scraped content item by ID."""
    item = db.query(ScrapedData).filter(ScrapedData.id == data_id).first()
    if not item:
        return JSONResponse(status_code=404, content={"detail": "Content not found"})

    return JSONResponse(
        content={
            "id": item.id,
            "url": item.url,
            "content": item.content,
            "scraped_at": item.scraped_at.isoformat() if item.scraped_at else None,
        }
    )


@app.get("/v1/data/", dependencies=[Depends(auth.get_api_key)])
def get_scraped_data(
    search: Optional[str] = Query(None, description="Search in content"),
    url: Optional[str] = Query(None, description="Filter by URL"),
    limit: int = Query(100, description="Max number of results"),
    offset: int = Query(0, description="Results offset"),
    db: Session = Depends(get_db),
):
    """Get scraped data with optional filtering."""
    query = db.query(ScrapedData)
    if search:
        query = query.filter(ScrapedData.content.ilike(f"%{search}%"))
    if url:
        query = query.filter(ScrapedData.url == url)
    results = query.offset(offset).limit(limit).all()

    return JSONResponse(
        content=[
            {
                "id": item.id,
                "url": item.url,
                "content": item.content[:200] + "...",
                "scraped_at": item.scraped_at.isoformat() if item.scraped_at else None,
            }
            for item in results
        ]
    )


@app.post("/v1/scrape/", dependencies=[Depends(auth.get_api_key)])
def trigger_scrape(request: ScrapeRequest, db: Session = Depends(get_db)):
    results = []
    for url in request.urls:
        success = scrape_url(url, db)
        results.append({"url": url, "success": success})

    return JSONResponse(content=results)


@app.post("/v1/scrape/batch/", dependencies=[Depends(auth.get_api_key)])
async def scrape_batch_endpoint(request: ScrapeRequest, db: Session = Depends(get_db)):
    """Uses the async version of scrape_batch"""
    results = await async_scrape_batch(request.urls, db)
    return JSONResponse(content=results)


@app.get("/v1/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=SessionLocal.kw["bind"])
    scheduler.start()

    yield

    scheduler.shutdown(wait=False)
