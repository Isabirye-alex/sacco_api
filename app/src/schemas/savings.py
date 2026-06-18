"""Module for app.src.schemas.savings."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SavingsDepositDTO(BaseModel):
    account_id: str
    amount: float
    transaction_date: date
    reference: Optional[str] = None
    description: Optional[str] = None
    processed_by_id: Optional[str] = None


class SavingsWithdrawDTO(BaseModel):
    account_id: str
    amount: float
    transaction_date: date
    reference: Optional[str] = None
    description: Optional[str] = None
    processed_by_id: Optional[str] = None


class SavingsAccountDTO(BaseModel):
    id: str
    account_no: str
    balance: float


class SavingsTransactionDTO(BaseModel):
    id: str
    account_id: str
    tx_type: str
    amount: float
    balance_after: float
    transaction_date: date
    reference: Optional[str]


class SavingsProductCreate(BaseModel):
    organisation_id: UUID
    name: str
    code: str
    product_type: Optional[str] = "ORDINARY"
    description: Optional[str] = None
    interest_rate_pa: float = 0.0
    min_opening_balance: float = 0.0
    min_balance: float = 0.0
    max_balance: Optional[float] = None
    withdrawal_allowed: Optional[bool] = True
    lock_period_days: Optional[int] = 0
    is_active: Optional[bool] = True


class SavingsProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    name: str
    code: str
    product_type: str
    description: Optional[str] = None
    interest_rate_pa: float
    min_opening_balance: float
    min_balance: float
    max_balance: Optional[float] = None
    withdrawal_allowed: bool
    lock_period_days: int
    is_active: bool


class SavingsAccountCreate(BaseModel):
  
    branch_id: UUID
    product_id: UUID
    account_no: Optional[str] = None
    member_id: UUID
    balance: Optional[float] = 0.0
    status_id: UUID
    opened_date: Optional[date] = None
    closed_date: Optional[date] = None
    maturity_date: Optional[date] = None
    notes: Optional[str] = None


class SavingsAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    branch_id: UUID
    product_id: UUID
    account_no: str
    member_id: UUID
    status_id: UUID
    balance: float
    opened_date: Optional[date] = None
    closed_date: Optional[date] = None
    maturity_date: Optional[date] = None
    notes: Optional[str] = None


class SavingsTransactionCreate(BaseModel):

    account_id: UUID
    ledger_entry_id: Optional[UUID] = None
    tx_type_id: Optional[UUID] = None  
    amount: float
    balance_after: Optional[float] = None
    reference: Optional[str] = None
    description: Optional[str] = None
    transaction_date: Optional[date] = None
    processed_by_id: Optional[UUID] = None
    payment_channel_code: str


class SavingsTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    account_id: UUID
    ledger_entry_id: Optional[UUID] = None
    tx_type_id: UUID  # UUID reference
    amount: float
    balance_after: float
    reference: Optional[str] = None
    description: Optional[str] = None
    transaction_date: date
    processed_by_id: Optional[UUID] = None
