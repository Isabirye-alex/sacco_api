from fastapi import FastAPI

from app.src.api.routes.app_routes import api_router

app = FastAPI(
  title="SACCO API",
  description="Savings and Credit Cooperative Organization management API",
  version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/root")
def root():
  return {"status": "ok", "message": "SACCO API is running"}
