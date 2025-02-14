# FastAPI PostgreSQL Web Scraper with Vector Similarity Search

A powerful web scraping and content similarity search application built with FastAPI, PostgreSQL with pgvector extension, and Playwright.

## Features

- **Web Scraping**: Scrape web content using Playwright with headless browser support
- **Vector Embeddings**: Convert scraped content to vector embeddings using sentence-transformers
- **Similarity Search**: Find similar content using cosine similarity via pgvector
- **API Authentication**: Secure API endpoints with API key authentication
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Batch Processing**: Support for scraping multiple URLs in a single request
- **Content Deduplication**: Skip storing content that is too similar to existing entries

## Architecture

The application consists of the following components:

- **FastAPI Backend**: RESTful API for triggering scrapes and searching content
- **PostgreSQL Database**: Stores scraped content and vector embeddings
- **pgvector Extension**: Enables efficient vector similarity search
- **Playwright**: Handles browser automation for web scraping
- **Sentence Transformers**: Generates embeddings from text content

## API Endpoints

All endpoints are prefixed with `/v1` for API versioning.

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/v1/scrape/` | POST | Trigger scraping for one or more URLs | API Key |
| `/v1/scrape/batch/` | POST | Batch scrape multiple URLs | API Key |
| `/v1/data/` | GET | Get scraped data with optional filtering | API Key |
| `/v1/data/{data_id}` | GET | Get specific scraped content by ID | API Key |
| `/v1/search` | GET | Search for similar content using text input | API Key |
| `/v1/health` | GET | Health check endpoint | None |

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- PostgreSQL with pgvector extension (for local development without Docker)

### Environment Variables

Copy the example environment file and adjust as needed:

```bash
cp .env.example .env.production
```

Key environment variables:

- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `API_KEYS`: List of valid API keys for authentication
- `SCRAPE_INTERVAL_HOURS`: Interval for scheduled scraping
- `BROWSER_HEADLESS`: Whether to run browser in headless mode
- `MAX_CONCURRENT_SCRAPES`: Maximum number of concurrent scrapes
- `SCRAPE_TIMEOUT_SECONDS`: Timeout for scraping operations
- `SIMILARITY_THRESHOLD`: Threshold for content similarity detection
- `VECTOR_DIMENSION`: Dimension of the vector embeddings
- `RESPECT_ROBOTS_TXT`: Whether to respect robots.txt rules (default: true)

### API Key Management

**Note on Security**: The current implementation uses a simple list of API keys defined in the environment variables for authentication. This approach is suitable for development and testing but has limitations for production use.

For a more robust security implementation in production environments, consider:

- Implementing a proper API key management system with rotation policies
- Using a database or key management service to store and validate API keys
- Adding rate limiting to prevent abuse
- Implementing token expiration and refresh mechanisms
- Using OAuth2 or JWT for more advanced authentication scenarios
- Logging authentication attempts for security monitoring
- Implementing IP-based restrictions for additional security

These enhancements would require modifications to the authentication middleware in `auth.py`.

### Running with Docker

1. Build and start the containers:

```bash
# Using the default .env file
docker-compose up -d

# OR explicitly specify the environment file (recommended)
docker-compose --env-file .env.production up -d
```

2. The API will be available at http://localhost:8000

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
playwright install --with-deps chromium
```

3. Set up PostgreSQL with pgvector extension

4. Create a `.env` file with the required environment variables

5. Run the application:

```bash
uvicorn app.main:app --reload
```

## Usage Examples

### Trigger a Scrape

```bash
curl -X POST http://localhost:8000/v1/scrape/ \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}'
```

### Search for Similar Content

```bash
curl -X GET "http://localhost:8000/v1/search?text=example%20search%20text&limit=5&threshold=0.7" \
  -H "X-API-Key: your_api_key"
```

### Get Scraped Data

```bash
curl -X GET "http://localhost:8000/v1/data/?search=example&limit=10" \
  -H "X-API-Key: your_api_key"
```

### Get Content by ID

```bash
curl -X GET "http://localhost:8000/v1/data/1" \
  -H "X-API-Key: your_api_key"
```

### Batch Scrape Multiple URLs

```bash
curl -X POST http://localhost:8000/v1/scrape/batch/ \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://example.org", "https://example.net"]}'
```

### Health Check

```bash
curl -X GET "http://localhost:8000/v1/health"
```

The health endpoint returns a JSON response with the current status and timestamp:

```json
{
  "status": "healthy",
  "timestamp": "2025-05-19T09:30:24.651605+00:00"
}
```

This endpoint is useful for monitoring and can be integrated with health check systems to ensure the API is running properly.

## Project Structure

```
python-fastapi-postgres-scraper/
├── app/
│   ├── auth.py           # API authentication
│   ├── config.py         # Application configuration
│   ├── db.py             # Database models and connection
│   ├── embeddings.py     # Vector embedding generation
│   ├── main.py           # FastAPI application and routes
│   └── scraper.py        # Web scraping functionality
├── docs/                 # API documentation
├── scripts/
│   ├── entrypoint.sh     # Docker container entrypoint
│   └── init.sql          # Database initialization
├── .env.example          # Example environment variables
├── .env.production       # Production environment variables
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker build configuration
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/): Modern, fast web framework for building APIs
- [PostgreSQL](https://www.postgresql.org/): Relational database
- [pgvector](https://github.com/pgvector/pgvector): PostgreSQL extension for vector similarity search
- [Playwright](https://playwright.dev/): Browser automation for web scraping
- [Sentence Transformers](https://www.sbert.net/): Text embedding models
- [SQLAlchemy](https://www.sqlalchemy.org/): SQL toolkit and ORM
- [Docker](https://www.docker.com/): Containerization platform

## License

MIT
