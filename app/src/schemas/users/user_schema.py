from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
  organisation_id: UUID
  branch_id: UUID
  gender_id: UUID
  status_id: UUID
  role_id: UUID
  member_no: str
  first_name: str
  middle_name: Optional[str] = None
  last_name: str
  date_of_birth: Optional[date] = None
  national_id: Optional[str] = None
  phone_primary: Optional[str] = None
  phone_secondary: Optional[str] = None
  email: EmailStr
  password: str
  country: Optional[str] = None
  village: Optional[str] = None
  district: Optional[str] = None
  joined_date: Optional[date] = None


class UserSignIn(BaseModel):
  email: EmailStr
  password: str
  location_country: Optional[str] | None = None
  location_city: Optional[str] | None = None


class UserResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: UUID
  organisation_id: UUID
  member_id: Optional[UUID] = None
  email: EmailStr
  phone: Optional[str] = None
  is_active: bool
  is_verified: bool
  first_name: Optional[str] = None
  last_name: Optional[str] = None
  member_no: Optional[str] = None


class TokenResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"
  user: UserResponse
