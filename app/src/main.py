"""Module for app.src.main."""

import logging  # 1. Import logging
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.src.api.routes.app_routes import api_router
from app.src.config.database import get_db
from app.src.dependencies.lookups import seed_lookups

# 2. Configure and define the logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]


# 1. Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_generator = None
    try:
        logger.info("Initializing database session...")
        db_generator = get_db()
        db = next(db_generator)
        
        logger.info("Running database migrations...")
        alembic_cfg = Config(str(ROOT_DIR / "alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(ROOT_DIR / "alembic"))
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Seeding lookup tables...")
        try:
            seed_lookups(db)
            db.commit()  # Cleanly seal the startup insertions
        except Exception as seed_err:
            db.rollback()  # 👈 CRITICAL: If seed fails/duplicates on Render, rollback instantly!
            logger.warning(f"Seeding skipped or encountered conflict: {seed_err}")

        logger.info("Database initialization successful.")
    except Exception as e:
        logger.error(f"CRITICAL: Database startup sequence failed: {e}", exc_info=True)
    finally:
        if db_generator is not None:
            next(db_generator, None)

    yield  # 👈 CRITICAL: Tells FastAPI startup is done; ready to receive requests!

# 2. Pass the lifespan to the FastAPI instance

app = FastAPI(
    lifespan=lifespan,
    servers=[
        {"url": "https://sacco-api-pb2n.onrender.com", "description": "Production environment"},
        {"url": "http://localhost:8000", "description": "Local environment"}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=False,
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")

@app.get("/root")
def root():
    return {"status": "Health"}