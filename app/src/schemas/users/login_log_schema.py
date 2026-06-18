from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LoginLogCreate(BaseModel):
  member_id: Optional[UUID] = None
  status: Optional[str] = "success"
  failure_reason: Optional[str] = None
  attempts: Optional[int] = None
  session_id: Optional[str] = None
  location_country: Optional[str] = None
  location_city: Optional[str] = None


class LoginLogResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  log_id: UUID
  member_id: Optional[UUID] = None
  login_at: Optional[datetime] = None
  ip_address: Optional[str] = None
  user_agent: Optional[str] = None
  status: Optional[str] = None
  failure_reason: Optional[str] = None
  attempts: Optional[int] = None
  session_id: Optional[str] = None
  location_country: Optional[str] = None
  location_city: Optional[str] = None
