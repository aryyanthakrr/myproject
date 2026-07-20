from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings
import os

# Ensure storage directory exists
os.makedirs(settings.STORAGE_PATH, exist_ok=True)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL.replace("sqlite:///", "sqlite:///"),
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MergeJob(Base):
    """Database model for merge jobs."""
    __tablename__ = "merge_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    model_a = Column(String, nullable=False)
    model_b = Column(String, nullable=False)
    method = Column(String, nullable=False)
    ratio = Column(Float, default=0.5)
    output_format = Column(String, default="gguf-4bit")
    output_name = Column(String, nullable=False)
    
    # Status tracking
    status = Column(String, default="pending")  # pending, downloading, merging, quantizing, verifying, completed, failed
    progress_percent = Column(Integer, default=0)
    current_step = Column(String, default="Initializing...")
    
    # Output info
    output_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    sha256_hash = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Metadata
    metadata_json = Column(JSON, default=dict)


class User(Base):
    """Database model for users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    provider = Column(String, nullable=False)  # github, google, credentials
    
    # Subscription
    is_pro = Column(Boolean, default=False)
    merges_count = Column(Integer, default=0)
    storage_used = Column(Integer, default=0)  # bytes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    
    # API keys
    api_keys = Column(JSON, default=list)


class DeployedModel(Base):
    """Database model for deployed models."""
    __tablename__ = "deployed_models"
    
    id = Column(Integer, primary_key=True, index=True)
    deploy_id = Column(String, unique=True, index=True, nullable=False)
    job_id = Column(String, nullable=False)
    model_path = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    api_url = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="active")  # active, paused, deleted
    requests_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
