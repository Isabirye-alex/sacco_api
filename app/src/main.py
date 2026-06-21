"""Module for app.src.main."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.src.api.routes.app_routes import api_router
# 1. Import your raw engine alongside get_db
from app.src.config.database import get_db, engine 
from app.src.dependencies.lookups import seed_lookups

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_generator = None
    try:
        logger.info("Initializing database session for startup tasks...")
        db_generator = get_db()
        db = next(db_generator)
        
        logger.info("Running database migrations...")
        alembic_cfg = Config(str(ROOT_DIR / "alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(ROOT_DIR / "alembic"))
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Seeding lookup tables...")
        try:
            seed_lookups(db)
            db.commit()
        except Exception as seed_err:
            db.rollback()
            logger.warning(f"Seeding encountered an expected conflict or was skipped: {seed_err}")

        logger.info("Database initialization successful.")
    except Exception as e:
        logger.error(f"CRITICAL: Database startup sequence failed: {e}", exc_info=True)
    finally:
        if db_generator is not None:
            next(db_generator, None)
        
        # 2. CRITICAL FIX: Trash the startup connection state and reset the pool
        logger.info("Disposing startup connection pool to prevent session leaks...")
        engine.dispose() 

    yield

# Pass the lifespan to the FastAPI instance
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