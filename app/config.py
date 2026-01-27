from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "FastAPI Application"
    app_version: str = "1.0.0"
    debug: bool = True
    database_url: str = "sqlite:///./bookshelf.db"
    secret_key: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"

settings = Settings()
