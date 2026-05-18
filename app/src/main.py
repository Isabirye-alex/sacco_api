from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.src.api.routes.app_routes import api_router
from app.src.config.database import get_db
from app.src.dependencies.lookups import seed_lookups

# 1. Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Extract the session from the get_db generator
    db_generator = get_db()
    db = next(db_generator)
    try:
        seed_lookups(db)
    finally:
        # Ensure the generator closes/cleans up properly
        next(db_generator, None) 
        
    yield
    # Shutdown logic (if any) can go here

# 2. Pass the lifespan to the FastAPI instance
app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")

@app.get("/root")
def root():
    return {"status": "Health"}