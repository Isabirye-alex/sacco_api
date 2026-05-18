from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class GenderCreate(BaseModel):
    gender: str
    description: Optional[str] = None


class GenderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    gender: str
    description: Optional[str] = None


class MemberStatusCreate(BaseModel):
    status: str
    description: Optional[str] = None


class MemberStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    status: str
    description: Optional[str] = None


class MaritalStatusCreate(BaseModel):
    status: str


class MaritalStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    status: str


class RoleCreate(BaseModel):
    role: str
    description: Optional[str] = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    role: str
    description: Optional[str] = None


class NextOfKinCreate(BaseModel):
    member_id: UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    member_relationship: Optional[str] = None
    national_id: Optional[str] = None
    is_primary: Optional[bool] = False
    marital_status: UUID


class NextOfKinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    member_id: UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    member_relationship: Optional[str] = None
    national_id: Optional[str] = None
    is_primary: bool
    marital_status: UUID


class MemberCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    branch_id: UUID
    gender_id: UUID
    status_id: UUID
    user_id: UUID
    member_no: str
    date_of_birth: Optional[date] = None
    national_id: Optional[str] = None
    marital_status: Optional[UUID] = None
    photo_url: Optional[str] = None
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    country: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    joined_date: Optional[datetime] = None
    exit_date: Optional[datetime] = None
    exit_reason: Optional[str] = None


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    branch_id: UUID
    gender_id: UUID
    status_id: UUID
    user_id: UUID
    member_no: str
    date_of_birth: Optional[date] = None
    national_id: Optional[str] = None
    marital_status: Optional[UUID] = None
    photo_url: Optional[str] = None
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    country: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    joined_date: Optional[datetime] = None
    exit_date: Optional[datetime] = None
    exit_reason: Optional[str] = None
