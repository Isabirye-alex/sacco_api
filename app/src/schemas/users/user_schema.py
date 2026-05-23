from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    # Required DB Fields

    role_name: Optional[str] = None
    email: EmailStr
    first_name: str
    last_name: str
    user_type: str = "MEMBER"

    password: str

    # Optional DB Fields
    phone: Optional[str] | None
    member_id: Optional[UUID] = None


class UserSignIn(BaseModel):
    email: EmailStr
    password: str
    location_country: Optional[str] | None = None
    location_city: Optional[str] | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    # Auth Data (for user Model)
    email: EmailStr
    first_name: str
    last_name: str
    member_id: UUID
    
class UserResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"