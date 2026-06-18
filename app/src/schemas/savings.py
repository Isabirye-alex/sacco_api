from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SavingsDepositDTO(BaseModel):
  account_id: UUID
  amount: Decimal = Field(gt=0)
  transaction_date: date
  reference: Optional[str] = None
  description: Optional[str] = None
  processed_by_id: Optional[UUID] = None


class SavingsWithdrawDTO(BaseModel):
  account_id: UUID
  amount: Decimal = Field(gt=0)
  transaction_date: date
  reference: Optional[str] = None
  description: Optional[str] = None
  processed_by_id: Optional[UUID] = None


class SavingsAccountResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: UUID
  organisation_id: UUID
  branch_id: UUID
  member_id: UUID
  product_id: UUID
  account_no: str
  balance: Decimal
  status: str
  opened_date: Optional[date] = None
  closed_date: Optional[date] = None
  maturity_date: Optional[date] = None


class SavingsTransactionResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: UUID
  organisation_id: UUID
  account_id: UUID
  tx_type: str
  amount: Decimal
  balance_after: Decimal
  transaction_date: date
  reference: Optional[str] = None
  description: Optional[str] = None
  processed_by_id: Optional[UUID] = None
  created_at: Optional[datetime] = None
