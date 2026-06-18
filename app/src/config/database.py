from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.src.config.settings import settings

DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
  raise RuntimeError("DATABASE_URL is not configured")

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
