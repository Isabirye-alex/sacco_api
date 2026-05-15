from fastapi import APIRouter
from app.src.api.endpoints.new_user_api_endpoint import router as user_route
from app.src.api.endpoints.login_logs_endpoint import router as login_logs_route
from app.src.api.endpoints.signin_endpoint import router as signin_route

api_router = APIRouter()

api_router.include_router(user_route, prefix="/users", tags=["users"])
api_router.include_router(signin_route, prefix="/auth", tags=["auth"])
api_router.include_router(login_logs_route, prefix="/login-logs", tags=["login-logs"])
