from playwright.sync_api import sync_playwright
from sqlalchemy import select
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import Session
from .db import ScrapedData
from .embeddings import embedder
from .config import settings
import logging
from typing import List, Optional
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(html_content: str) -> str:
    """Clean HTML content to get meaningful text"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and clean whitespace
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def check_similarity(db: Session, url: str, embedding: List[float], threshold: float = 0.85) -> bool:
    """Check similarity using pgvector"""
    query = select(func.cosine_similarity(ScrapedData.embedding, embedding).label('similarity'))\
        .filter(ScrapedData.url == url)\
        .order_by(ScrapedData.scraped_at.desc())\
        .limit(1)
    
    result = db.execute(query).first()
    
    if result:
        similarity = result[0]
        logger.info(f"Similarity score for {url}: {similarity}")
        return similarity > threshold
    
    return False

def scrape_url(url: str, db: Session) -> bool:
    """
    Scrape URL and store if content is sufficiently different.
    Returns True if new content was stored.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=settings.browser_headless)
            page = browser.new_page()
            
            logger.info(f"Scraping {url}")
            page.goto(url, timeout=settings.scrape_timeout_seconds * 1000)
            content = page.content()
            browser.close()

            # Clean content
            cleaned_content = clean_text(content)
            
            # Generate embedding
            embedding = embedder.generate(cleaned_content)

            # Check similarity
            if check_similarity(db, url, embedding, settings.similarity_threshold):
                logger.info(f"Content too similar for {url}")
                return False

            # Save new content
            scraped = ScrapedData(
                url=url, 
                content=cleaned_content,
                embedding=embedding
            )
            db.add(scraped)
            db.commit()
            logger.info(f"Successfully scraped {url}")
            return True

    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return False

def scrape_batch(urls: List[str], db: Session) -> dict:
    """
    Scrape multiple URLs and return results
    """
    results = {
        'successful': [],
        'failed': [],
        'skipped': []  # for similar content
    }
    
    for url in urls:
        try:
            success = scrape_url(url, db)
            if success:
                results['successful'].append(url)
            else:
                results['skipped'].append(url)
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            results['failed'].append({"url": url, "error": str(e)})
    
    return results