"""User management endpoints for creating and registering application users."""

from fastapi import APIRouter, HTTPException, status, Depends
from app.src.config.database import get_db
from app.src.schemas.users.user_schema import UserCreate, UserResponse
from sqlalchemy.orm import Session
from app.src.crud.get_user_by_email import get_user_by_email
from app.src.crud.users.user_create_crud import create_new_user

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new application user account.

    This endpoint accepts a validated user payload, checks whether the supplied
    email address is already registered, and creates the account when the email
    is unique. If a duplicate is found, the API returns a client error instead of
    creating another user record.

    Returns:
        The newly created user payload returned by the persistence layer.

    Raises:
        HTTPException: If the email is already in use.
    """
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email Already registered")
    return create_new_user(db, user)
