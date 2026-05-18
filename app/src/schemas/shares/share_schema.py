from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ShareProductCreate(BaseModel):
    organisation_id: UUID
    name: str
    code: str
    product_type: Optional[str] = "ORDINARY"
    description: Optional[str] = None
    nominal_value: float
    min_shares: int = 1
    max_shares: Optional[int] = None
    is_transferable: Optional[bool] = True
    is_redeemable: Optional[bool] = False
    is_active: Optional[bool] = True


class ShareProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    name: str
    code: str
    product_type: str
    description: Optional[str] = None
    nominal_value: float
    min_shares: int
    max_shares: Optional[int] = None
    is_transferable: bool
    is_redeemable: bool
    is_active: bool


class ShareAccountCreate(BaseModel):
    organisation_id: UUID
    branch_id: UUID
    member_id: UUID
    product_id: UUID
    account_no: str
    shares_held: Optional[float] = 0.0
    total_value: Optional[float] = 0.0
    is_active: Optional[bool] = True


class ShareAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    branch_id: UUID
    member_id: UUID
    product_id: UUID
    account_no: str
    shares_held: float
    total_value: float
    is_active: bool


class ShareTransactionCreate(BaseModel):
    organisation_id: UUID
    account_id: UUID
    ledger_entry_id: Optional[UUID] = None
    tx_type: str
    shares: float
    price_per_share: float
    total_amount: float
    shares_after: float
    reference: Optional[str] = None
    description: Optional[str] = None
    transaction_date: date
    processed_by_id: Optional[UUID] = None


class ShareTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    account_id: UUID
    ledger_entry_id: Optional[UUID] = None
    tx_type: str
    shares: float
    price_per_share: float
    total_amount: float
    shares_after: float
    reference: Optional[str] = None
    description: Optional[str] = None
    transaction_date: date
    processed_by_id: Optional[UUID] = None


class DividendCreate(BaseModel):
    organisation_id: UUID
    product_id: UUID
    period_label: str
    period_start: date
    period_end: date
    rate_percent: float
    total_amount: float
    status: Optional[str] = "DRAFT"
    approved_by_id: Optional[UUID] = None
    approved_date: Optional[date] = None
    notes: Optional[str] = None


class DividendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    product_id: UUID
    period_label: str
    period_start: date
    period_end: date
    rate_percent: float
    total_amount: float
    status: str
    approved_by_id: Optional[UUID] = None
    approved_date: Optional[date] = None
    notes: Optional[str] = None


class DividendPaymentCreate(BaseModel):
    organisation_id: UUID
    dividend_id: UUID
    share_account_id: UUID
    member_id: UUID
    shares_at_record: float
    amount: float
    paid_date: Optional[date] = None
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    ledger_entry_id: Optional[UUID] = None


class DividendPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    dividend_id: UUID
    share_account_id: UUID
    member_id: UUID
    shares_at_record: float
    amount: float
    paid_date: Optional[date] = None
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    ledger_entry_id: Optional[UUID] = None
