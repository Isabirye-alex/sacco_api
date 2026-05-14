from fastapi import FastAPI
from app.src.api.routes.app_routes import api_router

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")


@app.get("/root")
def root():
    return {"status": "Health"}
