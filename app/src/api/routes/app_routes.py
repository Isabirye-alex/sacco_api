from fastapi import APIRouter
from app.src.api.endpoints.new_user_api_endpoint import router as user_route
api_router = APIRouter()

api_router.include_router(user_route, prefix="/users", tags=["users"])
