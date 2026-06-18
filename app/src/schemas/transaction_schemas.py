"""Module for app.src.schemas.transaction_schemas."""

from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# ============ SAVINGS WITHDRAWAL & TRANSFER ============


class SavingsWithdrawalRequest(BaseModel):
    account_id: UUID
    amount: float
    reference: str
    payment_channel_code: str
    description: Optional[str] = None


class FundTransferRequest(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: float
    reference: str
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    amount: float
    balance_after: float
    reference: str
    description: Optional[str]
    transaction_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ LOAN FEATURES ============


class LoanApplicationRequest(BaseModel):
    product_id: UUID
    requested_amount: float
    proposed_term_months: int
    purpose: Optional[str] = None
    guarantor_ids: Optional[List[UUID]] = []
    collateral_description: Optional[str] = None


class LoanApprovalRequest(BaseModel):
    application_id: UUID
    approved_amount: float


class LoanRepaymentRequest(BaseModel):
    loan_id: UUID
    amount: float
    reference: str
    payment_channel_code: str


class LoanRepaymentResponse(BaseModel):
    id: UUID
    loan_id: UUID
    amount: float
    principal_amount: float
    interest_amount: float
    payment_date: date
    reference: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoanApplicationResponse(BaseModel):
    id: UUID
    member_id: UUID
    product_id: UUID
    requested_amount: float
    approved_amount: Optional[float]
    status: str
    created_at: datetime
    approved_date: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class LoanResponse(BaseModel):
    id: UUID
    member_id: UUID
    product_id: UUID
    principal_amount: float
    outstanding_balance: float
    interest_rate: float
    term_months: int
    disbursal_date: date
    maturity_date: date
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ SHARE PURCHASE & DIVIDENDS ============


class SharePurchaseRequest(BaseModel):
    product_id: UUID
    num_shares: int
    price_per_share: float
    reference: str
    payment_channel_code: str


class SharePurchaseResponse(BaseModel):
    id: UUID
    account_id: UUID
    shares: int
    price_per_share: float
    total_amount: float
    shares_after: int
    transaction_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DividendDeclarationRequest(BaseModel):
    product_id: UUID
    period_label: str
    period_start: date
    period_end: date
    rate_percent: float


class DividendResponse(BaseModel):
    id: UUID
    product_id: UUID
    period_label: str
    period_start: date
    period_end: date
    rate_percent: float
    total_amount: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShareAccountResponse(BaseModel):
    id: UUID
    member_id: UUID
    product_id: UUID
    account_no: str
    shares_held: float
    total_value: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ============ MOBILE MONEY PAYMENT ============


class MobileMoneyPaymentRequest(BaseModel):
    phone_number: str
    amount: float
    transaction_type: str  # DEPOSIT, WITHDRAWAL, LOAN_PAYMENT
    reference: str
    account_id: Optional[UUID] = None  # for deposits/withdrawals
    loan_id: Optional[UUID] = None  # for loan payments


class MobileMoneyPaymentResponse(BaseModel):
    id: UUID
    phone_number: str
    amount: float
    transaction_type: str
    status: str  # PENDING, SUCCESS, FAILED
    reference: str
    transaction_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ TRANSACTION HISTORY & REPORTS ============


class AccountTransactionHistoryRequest(BaseModel):
    account_id: UUID
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = 0
    limit: int = 50


class AccountStatementResponse(BaseModel):
    account_id: UUID
    account_no: str
    current_balance: float
    transactions: List[TransactionResponse]


class LoanStatementResponse(BaseModel):
    loan_id: UUID
    principal_amount: float
    outstanding_balance: float
    interest_rate: float
    term_months: int
    status: str
    repayments: List[LoanRepaymentResponse]


# ============ NOTIFICATIONS ============


class NotificationPreference(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    notification_email: Optional[str] = None
    notification_phone: Optional[str] = None
