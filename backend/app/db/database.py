from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URL)

# Configure engine with best practices
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Checks connection health before using it
    connect_args=settings.DATABASE_CONNECT_ARGS or {},  # Add any connection args from config
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db() -> Generator[Session, None, None]:
    """
    Creates a new database session for each request and ensures it's closed when done.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()