"""Module for app.src.schemas.users.login_log_schema."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LoginLogCreate(BaseModel):
    user_id: Optional[UUID]
    status: Optional[str] = "success"
    failure_reason: Optional[str] = None
    attempts: Optional[int] = None
    session_id: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None


class LoginLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    log_id: UUID
    user_id: Optional[UUID]
    login_at: Optional[datetime]
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: Optional[str]
    failure_reason: Optional[str]
    attempts: Optional[int]
    session_id: Optional[str]
    location_country: Optional[str]
    location_city: Optional[str]
