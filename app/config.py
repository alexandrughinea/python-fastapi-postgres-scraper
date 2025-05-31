import json

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    api_keys: list
    scrape_interval_hours: int = 24
    browser_headless: bool = True
    max_concurrent_scrapes: int = 3
    scrape_timeout_seconds: int = 30
    log_level: str = "INFO"
    similarity_threshold: float = 0.85
    vector_dimension: int = 384
    respect_robots_txt: bool = True

    def __init__(self):
        super().__init__()
        # Check if api_keys is a string and parse it
        if isinstance(self.api_keys, str):
            self.api_keys = json.loads(self.api_keys)


settings = Settings()
