"""Module for app.src.models.savings."""

from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
    Boolean,
    Date,
    Integer,
    ForeignKey,
)
from sqlalchemy import UUID
from sqlalchemy.orm import relationship

from app.src.models.base_file import Base, TimestampMixin


class SavingsProductType(TimestampMixin, Base):
    __tablename__ = "savings_product_types"

    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    products = relationship(
        "SavingsProduct",
        back_populates="product_type_obj",
        lazy="select",
    )


class SavingsAccountStatus(TimestampMixin, Base):
    __tablename__ = "savings_account_statuses"

    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    accounts = relationship(
        "SavingsAccount",
        back_populates="status_obj",
        lazy="select",
    )


class SavingsTxType(TimestampMixin, Base):
    __tablename__ = "savings_tx_types"

    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    transactions = relationship(
        "SavingsTransaction",
        back_populates="tx_type_obj",
        lazy="select",
    )


# Models


class SavingsProduct(TimestampMixin, Base):
    """
    A configurable savings product defined at Organisation level.
    Branches inherit these products; product-level overrides can be
    added later if needed.
    """

    __tablename__ = "savings_products"

    name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=False)
    product_type = Column(
        String(50),
        nullable=False,
        default="ORDINARY",
    )
    product_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("savings_product_types.id"),
        nullable=True,
        index=True,
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

    accounts = relationship("SavingsAccount", back_populates="product", lazy="select")
    product_type_obj = relationship(
        "SavingsProductType",
        back_populates="products",
        lazy="joined",
        uselist=False,
    )
    savings_control_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chart_of_accounts.id"),
        nullable=False,
    )
    interest_expense_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chart_of_accounts.id"),
        nullable=True,
    )


class SavingsAccount(TimestampMixin, Base):
    """One member can hold multiple savings accounts (one per product type)."""

    __tablename__ = "savings_accounts"

    branch_id = Column(
        UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True
    )
    member_id = Column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("savings_products.id"), nullable=False
    )

    account_no = Column(String(50), nullable=False)
    balance = Column(Numeric(18, 4), default=0, nullable=False)

    status_id = Column(
        UUID(as_uuid=True),
        ForeignKey("savings_account_statuses.id"),
        nullable=True,
        index=True,
    )
    opened_date = Column(Date, nullable=True)
    closed_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # relationships
    member = relationship("Member", back_populates="savings_accounts", lazy="select")
    product = relationship("SavingsProduct", back_populates="accounts", lazy="select")
    status_obj = relationship(
        "SavingsAccountStatus",
        back_populates="accounts",
        lazy="joined",
        uselist=False,
    )
    transactions = relationship(
        "SavingsTransaction", back_populates="account", lazy="select"
    )


class SavingsTransaction(TimestampMixin, Base):
    """
    Individual debit / credit entries on a savings account.
    Always linked to a LedgerEntry for double-entry integrity.
    """

    __tablename__ = "savings_transactions"

    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("savings_accounts.id"),
        nullable=False,
        index=True,
    )
    ledger_entry_id = Column(
        UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=True
    )

    # 1. Change field name to clarify it stores a UUID
    tx_type_id = Column(
        UUID(as_uuid=True), ForeignKey("savings_tx_types.id"), nullable=False
    )
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    # 2. Update your relationship mapping to explicitly use the new key
    amount = Column(Numeric(18, 4), nullable=False)
    balance_after = Column(Numeric(18, 4), nullable=False)  # snapshot for quick reads
    reference = Column(String(100), nullable=True)  # e.g. mobile money ref
    description = Column(Text, nullable=True)
    transaction_date = Column(Date, nullable=False)
    processed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    member = relationship("Member", back_populates="transactions")
    account = relationship("SavingsAccount", back_populates="transactions")
    tx_type_obj = relationship(
        "SavingsTxType",
        back_populates="transactions",
        lazy="joined",
        uselist=False,
    )
    ledger_entry = relationship("LedgerEntry")
    processed_by = relationship("User")


class PaymentChannelConfiguration(TimestampMixin, Base):
    """
    System-wide configuration mapping user-friendly channels (CASH, MPESA, BANK)
    to actual ChartOfAccount asset endpoints.
    """

    __tablename__ = "payment_channel_configurations"

    channel_code = Column(
        String(50), primary_key=True, unique=True, index=True
    )  # "CASH", "MOBILE_MONEY"
    channel_name = Column(String(100), nullable=False)

    asset_account_id = Column(
        UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=False
    )
