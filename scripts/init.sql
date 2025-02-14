CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS scraped_data (
                                            id SERIAL PRIMARY KEY,
                                            url VARCHAR NOT NULL,
                                            content TEXT,
                                            embedding vector(384),
                                            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON scraped_data USING ivfflat (embedding vector_cosine_ops);