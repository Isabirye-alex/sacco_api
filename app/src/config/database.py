"""Database configuration and session management for the application."""

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.src.config.settings import settings

# Load environment variables from the local .env file if present.
load_dotenv()

# Use the configured primary database URL for runtime connections.
DATABASE_URL = settings.ONLINE_DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("ONLINE_DATABASE_URL is not configured.")

# Create the SQLAlchemy engine for database access.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"application_name": "sacco_api"},
)

# Session factory used by FastAPI dependencies to obtain database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    Yield a database session for each request.

    The session is closed automatically after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
