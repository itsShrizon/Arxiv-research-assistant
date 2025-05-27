from pydantic_settings import BaseSettings, SettingsConfigDict

class UISettings(BaseSettings):
    """UI configuration settings."""
    API_URL: str = "http://localhost:8000"
    MAX_RESULTS: int = 50
    DEFAULT_CATEGORY: str = "cs.AI"
    PAPER_CACHE_DIR: str = "./cache"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )