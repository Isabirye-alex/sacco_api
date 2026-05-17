"""
Loans & Repayments
==================
LoanProduct         – configurable loan product (Emergency, Business, School fees…)
LoanApplication     – application before disbursement
Loan                – active / completed loan
LoanGuarantor       – who is guaranteeing the loan
LoanCollateral      – physical assets pledged
LoanRepaymentSchedule – generated amortisation / flat-rate schedule
LoanRepayment       – actual payment received
LoanPenalty         – late/missed payment charges
"""

import enum
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, Integer,
    Enum as SAEnum, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.config.base_file import Base, TimestampMixin


# ─── Enumerations ────────────────────────────────────────────────────────────

class RepaymentFrequencyEnum(str, enum.Enum):
    DAILY      = "DAILY"
    WEEKLY     = "WEEKLY"
    BIWEEKLY   = "BIWEEKLY"
    MONTHLY    = "MONTHLY"
    QUARTERLY  = "QUARTERLY"
    ANNUALLY   = "ANNUALLY"
    LUMP_SUM   = "LUMP_SUM"


class InterestMethodEnum(str, enum.Enum):
    FLAT_RATE       = "FLAT_RATE"         # interest on original principal
    REDUCING_BALANCE = "REDUCING_BALANCE"  # interest on outstanding balance


class LoanApplicationStatusEnum(str, enum.Enum):
    DRAFT     = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED  = "APPROVED"
    REJECTED  = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class LoanStatusEnum(str, enum.Enum):
    PENDING     = "PENDING"       # approved, not yet disbursed
    ACTIVE      = "ACTIVE"
    IN_ARREARS  = "IN_ARREARS"
    WRITTEN_OFF = "WRITTEN_OFF"
    CLOSED      = "CLOSED"


class CollateralTypeEnum(str, enum.Enum):
    LAND          = "LAND"
    VEHICLE       = "VEHICLE"
    BUILDING      = "BUILDING"
    EQUIPMENT     = "EQUIPMENT"
    SAVINGS       = "SAVINGS"     # savings-backed loan
    SHARES        = "SHARES"
    OTHER         = "OTHER"


class PenaltyTypeEnum(str, enum.Enum):
    LATE_PAYMENT   = "LATE_PAYMENT"
    MISSED_PAYMENT = "MISSED_PAYMENT"
    EARLY_CLOSURE  = "EARLY_CLOSURE"


# ─── Models ──────────────────────────────────────────────────────────────────

class LoanProduct(TimestampMixin, Base):
    """A configurable loan product (type/category)."""
    __tablename__ = "loan_products"

    organisation_id      = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True)
    name                 = Column(String(255), nullable=False)
    code                 = Column(String(20),  nullable=False)
    description          = Column(Text, nullable=True)

    # rules
    interest_rate_pa     = Column(Numeric(5, 2),  nullable=False)         # annual rate %
    interest_method      = Column(SAEnum(InterestMethodEnum), default=InterestMethodEnum.REDUCING_BALANCE, nullable=False)
    repayment_frequency  = Column(SAEnum(RepaymentFrequencyEnum), default=RepaymentFrequencyEnum.MONTHLY, nullable=False)
    min_term_months      = Column(Integer, default=1,  nullable=False)
    max_term_months      = Column(Integer, default=24, nullable=False)
    min_amount           = Column(Numeric(18, 4), nullable=False)
    max_amount           = Column(Numeric(18, 4), nullable=True)          # None = unlimited
    loan_to_savings_ratio= Column(Numeric(5, 2), nullable=True)           # e.g. 3× savings
    loan_to_shares_ratio = Column(Numeric(5, 2), nullable=True)           # e.g. 2× shares
    requires_guarantor   = Column(Boolean, default=True, nullable=False)
    min_guarantors       = Column(Integer, default=1, nullable=False)
    requires_collateral  = Column(Boolean, default=False, nullable=False)
    penalty_rate_per_day = Column(Numeric(5, 4), default=0.001, nullable=False)  # % of outstanding
    processing_fee_pct   = Column(Numeric(5, 2), default=1.00, nullable=False)   # % of loan amount
    is_active            = Column(Boolean, default=True, nullable=False)

    applications = relationship("LoanApplication", back_populates="product", lazy="dynamic")
    loans        = relationship("Loan",            back_populates="product", lazy="dynamic")


class LoanApplication(TimestampMixin, Base):
    """Loan application — created before disbursement."""
    __tablename__ = "loan_applications"

    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True)
    branch_id       = Column(UUID(as_uuid=True), ForeignKey("branches.id"),      nullable=False, index=True)
    member_id       = Column(UUID(as_uuid=True), ForeignKey("members.id"),       nullable=False, index=True)
    product_id      = Column(UUID(as_uuid=True), ForeignKey("loan_products.id"), nullable=False)

    application_no   = Column(String(50), nullable=False)
    applied_amount   = Column(Numeric(18, 4), nullable=False)
    approved_amount  = Column(Numeric(18, 4), nullable=True)
    term_months      = Column(Integer, nullable=False)
    purpose          = Column(Text, nullable=True)
    status           = Column(SAEnum(LoanApplicationStatusEnum), default=LoanApplicationStatusEnum.DRAFT, nullable=False)

    applied_date     = Column(Date, nullable=False)
    reviewed_date    = Column(Date, nullable=True)
    decision_date    = Column(Date, nullable=True)
    reviewed_by_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decision_by_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    notes            = Column(Text, nullable=True)

    product     = relationship("LoanProduct", back_populates="applications")
    loan        = relationship("Loan", back_populates="application", uselist=False)
    guarantors  = relationship("LoanGuarantor",  back_populates="application", lazy="dynamic")
    collaterals = relationship("LoanCollateral",  back_populates="application", lazy="dynamic")


class Loan(TimestampMixin, Base):
    """A disbursed loan — child of an approved LoanApplication."""
    __tablename__ = "loans"

    organisation_id  = Column(UUID(as_uuid=True), ForeignKey("organisations.id"),  nullable=False, index=True)
    branch_id        = Column(UUID(as_uuid=True), ForeignKey("branches.id"),       nullable=False, index=True)
    member_id        = Column(UUID(as_uuid=True), ForeignKey("members.id"),        nullable=False, index=True)
    product_id       = Column(UUID(as_uuid=True), ForeignKey("loan_products.id"),  nullable=False)
    application_id   = Column(UUID(as_uuid=True), ForeignKey("loan_applications.id"), nullable=False, unique=True)

    loan_no          = Column(String(50), nullable=False)
    principal        = Column(Numeric(18, 4), nullable=False)
    interest_rate_pa = Column(Numeric(5, 2),  nullable=False)   # snapshot at origination
    term_months      = Column(Integer, nullable=False)
    interest_method  = Column(SAEnum(InterestMethodEnum), nullable=False)
    repayment_frequency = Column(SAEnum(RepaymentFrequencyEnum), nullable=False)

    processing_fee   = Column(Numeric(18, 4), default=0, nullable=False)
    total_interest   = Column(Numeric(18, 4), default=0, nullable=False)   # pre-calculated
    total_payable    = Column(Numeric(18, 4), default=0, nullable=False)   # principal + interest

    outstanding_principal = Column(Numeric(18, 4), nullable=False)
    outstanding_interest  = Column(Numeric(18, 4), default=0, nullable=False)
    outstanding_penalty   = Column(Numeric(18, 4), default=0, nullable=False)
    total_paid            = Column(Numeric(18, 4), default=0, nullable=False)

    disbursement_date = Column(Date, nullable=False)
    first_payment_date= Column(Date, nullable=False)
    maturity_date     = Column(Date, nullable=False)
    closed_date       = Column(Date, nullable=True)

    status            = Column(SAEnum(LoanStatusEnum), default=LoanStatusEnum.PENDING, nullable=False)
    disbursed_by_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ledger_entry_id   = Column(UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=True)  # disbursement entry
    notes             = Column(Text, nullable=True)

    member      = relationship("Member",          back_populates="loans")
    product     = relationship("LoanProduct",     back_populates="loans")
    application = relationship("LoanApplication", back_populates="loan")
    schedule    = relationship("LoanRepaymentSchedule", back_populates="loan", lazy="dynamic", order_by="LoanRepaymentSchedule.due_date")
    repayments  = relationship("LoanRepayment",   back_populates="loan", lazy="dynamic")
    penalties   = relationship("LoanPenalty",     back_populates="loan", lazy="dynamic")


class LoanGuarantor(TimestampMixin, Base):
    """A member standing as guarantor for a loan application."""
    __tablename__ = "loan_guarantors"

    organisation_id  = Column(UUID(as_uuid=True), ForeignKey("organisations.id"),      nullable=False, index=True)
    application_id   = Column(UUID(as_uuid=True), ForeignKey("loan_applications.id"),  nullable=False, index=True)
    guarantor_id     = Column(UUID(as_uuid=True), ForeignKey("members.id"),            nullable=False)

    guaranteed_amount= Column(Numeric(18, 4), nullable=True)   # portion they're covering
    has_consented    = Column(Boolean, default=False, nullable=False)
    consent_date     = Column(Date, nullable=True)
    notes            = Column(Text, nullable=True)

    application = relationship("LoanApplication", back_populates="guarantors")
    guarantor   = relationship("Member", foreign_keys=[guarantor_id])


class LoanCollateral(TimestampMixin, Base):
    """Physical or financial asset pledged against a loan."""
    __tablename__ = "loan_collaterals"

    organisation_id  = Column(UUID(as_uuid=True), ForeignKey("organisations.id"),      nullable=False, index=True)
    application_id   = Column(UUID(as_uuid=True), ForeignKey("loan_applications.id"),  nullable=False, index=True)

    collateral_type  = Column(SAEnum(CollateralTypeEnum), nullable=False)
    description      = Column(Text, nullable=False)
    estimated_value  = Column(Numeric(18, 4), nullable=False)
    document_ref     = Column(String(255), nullable=True)   # title deed, logbook #, etc.
    notes            = Column(Text, nullable=True)

    application = relationship("LoanApplication", back_populates="collaterals")


class LoanRepaymentSchedule(TimestampMixin, Base):
    """
    Auto-generated amortisation / flat-rate schedule row.
    One row per instalment period.
    """
    __tablename__ = "loan_repayment_schedules"

    organisation_id   = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True)
    loan_id           = Column(UUID(as_uuid=True), ForeignKey("loans.id"),          nullable=False, index=True)

    instalment_no     = Column(Integer, nullable=False)
    due_date          = Column(Date, nullable=False)
    principal_due     = Column(Numeric(18, 4), nullable=False)
    interest_due      = Column(Numeric(18, 4), nullable=False)
    total_due         = Column(Numeric(18, 4), nullable=False)
    principal_paid    = Column(Numeric(18, 4), default=0, nullable=False)
    interest_paid     = Column(Numeric(18, 4), default=0, nullable=False)
    penalty_paid      = Column(Numeric(18, 4), default=0, nullable=False)
    is_paid           = Column(Boolean, default=False, nullable=False)
    paid_date         = Column(Date, nullable=True)

    loan = relationship("Loan", back_populates="schedule")


class LoanRepayment(TimestampMixin, Base):
    """An actual repayment received from the member."""
    __tablename__ = "loan_repayments"

    organisation_id  = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True)
    loan_id          = Column(UUID(as_uuid=True), ForeignKey("loans.id"),          nullable=False, index=True)
    ledger_entry_id  = Column(UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=True)

    amount           = Column(Numeric(18, 4), nullable=False)
    principal_portion= Column(Numeric(18, 4), default=0, nullable=False)
    interest_portion = Column(Numeric(18, 4), default=0, nullable=False)
    penalty_portion  = Column(Numeric(18, 4), default=0, nullable=False)

    payment_date     = Column(Date, nullable=False)
    payment_method   = Column(String(50), nullable=True)   # CASH, MOBILE_MONEY, BANK
    reference        = Column(String(100), nullable=True)
    notes            = Column(Text, nullable=True)
    received_by_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    loan         = relationship("Loan", back_populates="repayments")
    ledger_entry = relationship("LedgerEntry")
    received_by  = relationship("User")


class LoanPenalty(TimestampMixin, Base):
    """Penalty charges raised against a loan."""
    __tablename__ = "loan_penalties"

    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True)
    loan_id         = Column(UUID(as_uuid=True), ForeignKey("loans.id"),          nullable=False, index=True)

    penalty_type    = Column(SAEnum(PenaltyTypeEnum), nullable=False)
    days_overdue    = Column(Integer, default=0, nullable=False)
    amount          = Column(Numeric(18, 4), nullable=False)
    amount_paid     = Column(Numeric(18, 4), default=0, nullable=False)
    is_waived       = Column(Boolean, default=False, nullable=False)
    waived_by_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    raised_date     = Column(Date, nullable=False)
    notes           = Column(Text, nullable=True)

    loan = relationship("Loan", back_populates="penalties")