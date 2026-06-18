from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.src.api.routes.app_routes import api_router
from app.src.config.database import get_db
from app.src.dependencies.lookups import seed_lookups

ROOT_DIR = Path(__file__).resolve().parents[2]


# 1. Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: run database migrations first so lookup tables exist.
    db_generator = get_db()
    db = next(db_generator)
    try:
        alembic_cfg = Config(str(ROOT_DIR / "alembic.ini"))
        alembic_cfg.set_main_option(
            "script_location", str(ROOT_DIR / "alembic")
        )
        command.upgrade(alembic_cfg, "head")
        seed_lookups(db)
    finally:
        # Ensure the generator closes/cleans up properly.
        next(db_generator, None)

    yield
    # Shutdown logic (if any) can go here

# 2. Pass the lifespan to the FastAPI instance

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")

@app.get("/root")
def root():
    return {"status": "Health"}