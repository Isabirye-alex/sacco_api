"""
Savings & Accounts
==================
SavingsProduct    – configurable product (Ordinary Savings, Fixed Deposit, etc.)
SavingsAccount    – a member's instance of a product
SavingsTransaction– individual credit / debit entries (sourced from the ledger)
"""

import enum
from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
    Boolean,
    Date,
    Integer,
    Enum as SAEnum,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.config.base_file import Base, TimestampMixin

# ─── Enumerations ────────────────────────────────────────────────────────────


class SavingsProductTypeEnum(str, enum.Enum):
    ORDINARY = "ORDINARY"  # regular passbook savings
    FIXED_DEPOSIT = "FIXED_DEPOSIT"  # locked for a term
    GOAL = "GOAL"  # target / purpose savings
    EMERGENCY = "EMERGENCY"  # emergency fund
    CHRISTMAS = "CHRISTMAS"  # seasonal


class SavingsAccountStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DORMANT = "DORMANT"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class SavingsTxTypeEnum(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    INTEREST = "INTEREST"
    CHARGE = "CHARGE"
    TRANSFER = "TRANSFER"


# ─── Models ──────────────────────────────────────────────────────────────────


class SavingsProduct(TimestampMixin, Base):
    """
    A configurable savings product defined at Organisation level.
    Branches inherit these products; product-level overrides can be
    added later if needed.
    """

    __tablename__ = "savings_products"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=False)
    product_type = Column(
        SAEnum(SavingsProductTypeEnum),
        nullable=False,
        default=SavingsProductTypeEnum.ORDINARY,
    )
    description = Column(Text, nullable=True)

    # rates & rules
    interest_rate_pa = Column(
        Numeric(5, 2), default=0.00, nullable=False
    )  # % per annum
    min_opening_balance = Column(Numeric(18, 4), default=0, nullable=False)
    min_balance = Column(Numeric(18, 4), default=0, nullable=False)
    max_balance = Column(Numeric(18, 4), nullable=True)  # None = unlimited
    withdrawal_allowed = Column(Boolean, default=True, nullable=False)
    lock_period_days = Column(Integer, default=0, nullable=False)  # for fixed deposits

    is_active = Column(Boolean, default=True, nullable=False)

    accounts = relationship("SavingsAccount", back_populates="product", lazy="dynamic")


class SavingsAccount(TimestampMixin, Base):
    """One member can hold multiple savings accounts (one per product type)."""

    __tablename__ = "savings_accounts"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    branch_id = Column(
        UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True
    )
    member_id = Column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("savings_products.id"), nullable=False
    )

    account_no = Column(String(50), nullable=False)  # human-readable
    balance = Column(Numeric(18, 4), default=0, nullable=False)
    status = Column(
        SAEnum(SavingsAccountStatusEnum),
        default=SavingsAccountStatusEnum.ACTIVE,
        nullable=False,
    )
    opened_date = Column(Date, nullable=True)
    closed_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)  # for fixed deposits
    notes = Column(Text, nullable=True)

    # relationships
    member = relationship("Member", back_populates="savings_accounts")
    product = relationship("SavingsProduct", back_populates="accounts")
    transactions = relationship(
        "SavingsTransaction", back_populates="account", lazy="dynamic"
    )


class SavingsTransaction(TimestampMixin, Base):
    """
    Individual debit / credit entries on a savings account.
    Always linked to a LedgerEntry for double-entry integrity.
    """

    __tablename__ = "savings_transactions"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("savings_accounts.id"),
        nullable=False,
        index=True,
    )
    ledger_entry_id = Column(
        UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=True
    )

    tx_type = Column(SAEnum(SavingsTxTypeEnum), nullable=False)
    amount = Column(Numeric(18, 4), nullable=False)
    balance_after = Column(Numeric(18, 4), nullable=False)  # snapshot for quick reads
    reference = Column(String(100), nullable=True)  # e.g. mobile money ref
    description = Column(Text, nullable=True)
    transaction_date = Column(Date, nullable=False)
    processed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    account = relationship("SavingsAccount", back_populates="transactions")
    ledger_entry = relationship("LedgerEntry")
    processed_by = relationship("User")
