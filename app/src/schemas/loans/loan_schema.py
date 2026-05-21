from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LoanProductCreate(BaseModel):

    name: str
    code: str
    description: Optional[str] = None
    interest_rate_pa: float
    interest_method: Optional[str] = "REDUCING_BALANCE"
    repayment_frequency: Optional[str] = "MONTHLY"
    min_term_months: int = 1
    max_term_months: int = 24
    min_amount: float
    max_amount: Optional[float] = None
    loan_to_savings_ratio: Optional[float] = None
    loan_to_shares_ratio: Optional[float] = None
    requires_guarantor: Optional[bool] = True
    min_guarantors: Optional[int] = 1
    requires_collateral: Optional[bool] = False
    penalty_rate_per_day: Optional[float] = 0.001
    processing_fee_pct: Optional[float] = 1.0
    is_active: Optional[bool] = True


class LoanProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID

    name: str
    code: str
    description: Optional[str] = None
    interest_rate_pa: float
    interest_method: str
    repayment_frequency: str
    min_term_months: int
    max_term_months: int
    min_amount: float
    max_amount: Optional[float] = None
    loan_to_savings_ratio: Optional[float] = None
    loan_to_shares_ratio: Optional[float] = None
    requires_guarantor: bool
    min_guarantors: int
    requires_collateral: bool
    penalty_rate_per_day: float
    processing_fee_pct: float
    is_active: bool


class LoanApplicationCreate(BaseModel):

    branch_id: UUID
    member_id: UUID
    product_id: UUID
    application_no: Optional[str] = None
    applied_amount: float
    approved_amount: Optional[float] = None
    term_months: int
    purpose: Optional[str] = None
    status: Optional[str] = "DRAFT"
    applied_date: Optional[date] = None
    reviewed_date: Optional[date] = None
    decision_date: Optional[date] = None
    reviewed_by_id: Optional[UUID] = None
    decision_by_id: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


class LoanApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID

    branch_id: UUID
    member_id: UUID
    product_id: UUID
    application_no: str
    applied_amount: float
    approved_amount: Optional[float] = None
    term_months: int
    purpose: Optional[str] = None
    status: str
    applied_date: date
    reviewed_date: Optional[date] = None
    decision_date: Optional[date] = None
    reviewed_by_id: Optional[UUID] = None
    decision_by_id: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


class LoanCreate(BaseModel):

    branch_id: UUID
    member_id: UUID
    product_id: UUID
    application_id: UUID
    loan_no: Optional[str] = None
    principal: float
    interest_rate_pa: float
    term_months: int
    interest_method: str
    repayment_frequency: str
    processing_fee: Optional[float] = 0.0
    total_interest: Optional[float] = 0.0
    total_payable: Optional[float] = 0.0
    outstanding_principal: float
    outstanding_interest: Optional[float] = 0.0
    outstanding_penalty: Optional[float] = 0.0
    total_paid: Optional[float] = 0.0
    disbursement_date: date
    first_payment_date: date
    maturity_date: date
    closed_date: Optional[date] = None
    status: Optional[str] = "PENDING"
    disbursed_by_id: Optional[UUID] = None
    ledger_entry_id: Optional[UUID] = None
    notes: Optional[str] = None


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID

    branch_id: UUID
    member_id: UUID
    product_id: UUID
    application_id: UUID
    loan_no: str
    principal: float
    interest_rate_pa: float
    term_months: int
    interest_method: str
    repayment_frequency: str
    processing_fee: float
    total_interest: float
    total_payable: float
    outstanding_principal: float
    outstanding_interest: float
    outstanding_penalty: float
    total_paid: float
    disbursement_date: date
    first_payment_date: date
    maturity_date: date
    closed_date: Optional[date] = None
    status: str
    disbursed_by_id: Optional[UUID] = None
    ledger_entry_id: Optional[UUID] = None
    notes: Optional[str] = None


class LoanGuarantorCreate(BaseModel):

    application_id: UUID
    guarantor_id: UUID
    guaranteed_amount: Optional[float] = None
    has_consented: Optional[bool] = False
    consent_date: Optional[date] = None
    notes: Optional[str] = None


class LoanGuarantorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID

    application_id: UUID
    guarantor_id: UUID
    guaranteed_amount: Optional[float] = None
    has_consented: bool
    consent_date: Optional[date] = None
    notes: Optional[str] = None


class LoanCollateralCreate(BaseModel):

    application_id: UUID
    collateral_type: str
    description: str
    estimated_value: float
    document_ref: Optional[str] = None
    notes: Optional[str] = None


class LoanCollateralResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID

    application_id: UUID
    collateral_type: str
    description: str
    estimated_value: float
    document_ref: Optional[str] = None
    notes: Optional[str] = None


class LoanRepaymentScheduleCreate(BaseModel):

    loan_id: UUID
    instalment_no: int
    due_date: date
    principal_due: float
    interest_due: float
    total_due: float
    principal_paid: Optional[float] = 0.0
    interest_paid: Optional[float] = 0.0
    penalty_paid: Optional[float] = 0.0
    is_paid: Optional[bool] = False
    paid_date: Optional[date] = None


class LoanRepaymentScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID

    loan_id: UUID
    instalment_no: int
    due_date: date
    principal_due: float
    interest_due: float
    total_due: float
    principal_paid: float
    interest_paid: float
    penalty_paid: float
    is_paid: bool
    paid_date: Optional[date] = None


class LoanRepaymentCreate(BaseModel):

    loan_id: UUID
    ledger_entry_id: Optional[UUID] = None
    amount: float
    principal_portion: Optional[float] = 0.0
    interest_portion: Optional[float] = 0.0
    penalty_portion: Optional[float] = 0.0
    payment_date: date
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    received_by_id: Optional[UUID] = None


class LoanRepaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID

    loan_id: UUID
    ledger_entry_id: Optional[UUID] = None
    amount: float
    principal_portion: float
    interest_portion: float
    penalty_portion: float
    payment_date: date
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    received_by_id: Optional[UUID] = None


class LoanPenaltyCreate(BaseModel):

    loan_id: UUID
    penalty_type: str
    days_overdue: Optional[int] = 0
    amount: float
    amount_paid: Optional[float] = 0.0
    is_waived: Optional[bool] = False
    waived_by_id: Optional[UUID] = None
    raised_date: date
    notes: Optional[str] = None


class LoanPenaltyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    id: UUID

    loan_id: UUID
    penalty_type: str
    days_overdue: int
    amount: float
    amount_paid: float
    is_waived: bool
    waived_by_id: Optional[UUID] = None
    raised_date: date
    notes: Optional[str] = None
