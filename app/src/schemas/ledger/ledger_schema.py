from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChartOfAccountCreate(BaseModel):
    organisation_id: UUID
    code: str
    name: str
    account_type: str
    account_category: Optional[str] = None
    parent_id: Optional[UUID] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True


class ChartOfAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    code: str
    name: str
    account_type: str
    account_category: Optional[str] = None
    parent_id: Optional[UUID] = None
    description: Optional[str] = None
    is_active: bool


class LedgerEntryCreate(BaseModel):
    organisation_id: UUID
    branch_id: UUID
    entry_no: str
    entry_type: str
    entry_date: date
    description: Optional[str] = None
    reference: Optional[str] = None
    total_debit: float
    total_credit: float
    status: Optional[str] = "POSTED"
    reversal_of_id: Optional[UUID] = None
    created_by_id: Optional[UUID] = None
    notes: Optional[str] = None


class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    branch_id: UUID
    entry_no: str
    entry_type: str
    entry_date: date
    description: Optional[str] = None
    reference: Optional[str] = None
    total_debit: float
    total_credit: float
    status: str
    reversal_of_id: Optional[UUID] = None
    created_by_id: Optional[UUID] = None
    notes: Optional[str] = None


class LedgerLineCreate(BaseModel):

    entry_id: UUID
    account_id: UUID
    dr_cr: Optional[str]=None
    amount: float
    description: Optional[str] = None
    member_id: Optional[UUID] = None


class LedgerLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    entry_id: UUID
    account_id: UUID
    # dr_cr: Optional[str] = None
    amount: float
    description: Optional[str] = None
    member_id: Optional[UUID] = None


class JournalEntryCreate(BaseModel):
    organisation_id: UUID
    branch_id: UUID
    ledger_entry_id: UUID
    narration: str
    prepared_by_id: UUID
    approved_by_id: Optional[UUID] = None
    approved_date: Optional[date] = None
    is_approved: Optional[bool] = False


class JournalEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID
    organisation_id: UUID
    branch_id: UUID
    ledger_entry_id: UUID
    narration: str
    prepared_by_id: UUID
    approved_by_id: Optional[UUID] = None
    approved_date: Optional[date] = None
    is_approved: bool
