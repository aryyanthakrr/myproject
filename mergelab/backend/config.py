import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application
    APP_NAME: str = "MergeLab"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # HuggingFace
    HF_TOKEN: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./mergelab.db"
    
    # Storage
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024 * 1024  # 50GB
    
    # Rate Limiting
    RATE_LIMIT_FREE: int = 5  # merges per hour
    RATE_LIMIT_PRO: int = -1  # unlimited
    
    # Payment (Razorpay)
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    
    # Auth
    NEXTAUTH_SECRET: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "https://mergelab.intellectlabs.ai"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
