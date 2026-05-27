from app.src.config.settings import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError(f"Invalid DATABASE_URL")

engine = create_engine(
    DATABASE_URL, pool_pre_ping=True, connect_args={"application_name": "sacco_api"}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
