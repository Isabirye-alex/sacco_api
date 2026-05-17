from fastapi import APIRouter
from app.src.api.endpoints.users import router as users_route
from app.src.api.endpoints.auth import router as auth_route
from app.src.api.endpoints.logs import router as logs_route

api_router = APIRouter()

api_router.include_router(users_route, prefix="/users", tags=["users"])
api_router.include_router(auth_route, prefix="/auth", tags=["auth"])
api_router.include_router(logs_route, prefix="/login-logs", tags=["login-logs"])
