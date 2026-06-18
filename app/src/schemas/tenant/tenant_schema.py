"""Module for app.src.schemas.tenant.tenant_schema."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class OrganisationCreate(BaseModel):
    name: str
    short_code: str
    registration_no: str
    email: EmailStr
    phone: str
    address: str
    logo_url: str
    is_active: Optional[bool] | None

    # settings
    default_currency: str
    min_share_value: float
    loan_interest_rate: float
    savings_interest_rate: float


class OrganisationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    name: str
    short_code: str
    registration_no: str
    email: EmailStr
    phone: str
    address: str
    logo_url: str
    is_active: bool

    # settings
    default_currency: str
    min_share_value: float
    loan_interest_rate: float
    savings_interest_rate: float


class BranchCreate(BaseModel):
    organisation_id: UUID
    branch_name: str
    code: str
    location: Optional[str] = None
    manager_name: Optional[str] = None
    branch_phone: Optional[str] = None
    branch_email: Optional[EmailStr] = None
    is_active: Optional[bool] = True


class BranchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    branch_name: str
    code: str
    location: Optional[str] = None
    manager_name: Optional[str] = None
    branch_phone: Optional[str] = None
    branch_email: Optional[EmailStr] = None
    is_active: bool
