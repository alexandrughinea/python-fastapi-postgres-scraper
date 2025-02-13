CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS scraped_data (
    id SERIAL PRIMARY KEY,
    url VARCHAR NOT NULL,
    content TEXT,
    embedding vector(384),  -- Dimension matches the model
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON scraped_data USING ivfflat (embedding vector_cosine_ops);
