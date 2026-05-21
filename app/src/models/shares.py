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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.models.base_file import Base, TimestampMixin


class ShareProductType(TimestampMixin, Base):
    __tablename__ = "share_product_types"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    products = relationship(
        "ShareProduct",
        back_populates="product_type_obj",
        lazy="select",
        foreign_keys="ShareProduct.product_type",
    )


class ShareTransactionType(TimestampMixin, Base):
    __tablename__ = "share_transaction_types"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    transactions = relationship(
        "ShareTransaction",
        back_populates="tx_type_obj",
        lazy="select",
        foreign_keys="ShareTransaction.tx_type",
    )


class DividendStatus(TimestampMixin, Base):
    __tablename__ = "dividend_statuses"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    dividends = relationship(
        "Dividend",
        back_populates="status_obj",
        lazy="select",
        foreign_keys="Dividend.status",
    )


# Models


class ShareProduct(TimestampMixin, Base):
    """A class / category of shares offered by the SACCO."""

    __tablename__ = "share_products"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=False)
    product_type = Column(
        String(50),
        ForeignKey("share_product_types.code"),
        default="ORDINARY",
        nullable=False,
    )
    product_type_obj = relationship(
        "ShareProductType",
        back_populates="products",
        uselist=False,
        lazy="joined",
        foreign_keys=[product_type],
    )
    description = Column(Text, nullable=True)

    nominal_value = Column(Numeric(18, 4), nullable=False)  # face value per share
    min_shares = Column(Integer, default=1, nullable=False)  # min a member must hold
    max_shares = Column(Integer, nullable=True)  # None = unlimited
    is_transferable = Column(Boolean, default=True, nullable=False)
    is_redeemable = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    accounts = relationship("ShareAccount", back_populates="product", lazy="select")
    dividends = relationship("Dividend", back_populates="product", lazy="select")


class ShareAccount(TimestampMixin, Base):
    """A member's shareholding in a given ShareProduct."""

    __tablename__ = "share_accounts"

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
        UUID(as_uuid=True), ForeignKey("share_products.id"), nullable=False
    )

    account_no = Column(String(50), nullable=False)
    shares_held = Column(Numeric(18, 4), default=0, nullable=False)  # quantity
    total_value = Column(
        Numeric(18, 4), default=0, nullable=False
    )  # shares_held × nominal_value
    is_active = Column(Boolean, default=True, nullable=False)

    member = relationship("Member", back_populates="share_accounts")
    product = relationship("ShareProduct", back_populates="accounts")
    transactions = relationship(
        "ShareTransaction",
        back_populates="account",
        lazy="joined",
    )
    dividend_payments = relationship(
        "DividendPayment", back_populates="share_account", lazy="select"
    )


class ShareTransaction(TimestampMixin, Base):
    """Records every change to a member's share holding."""

    __tablename__ = "share_transactions"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    account_id = Column(
        UUID(as_uuid=True), ForeignKey("share_accounts.id"), nullable=False, index=True
    )
    ledger_entry_id = Column(
        UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=True
    )

    tx_type = Column(
        String(50),
        ForeignKey("share_transaction_types.code"),
        nullable=False,
    )
    tx_type_obj = relationship(
        "ShareTransactionType",
        back_populates="transactions",
        uselist=False,
        lazy="joined",
        foreign_keys=[tx_type],
    )
    shares = Column(Numeric(18, 4), nullable=False)
    price_per_share = Column(Numeric(18, 4), nullable=False)
    total_amount = Column(Numeric(18, 4), nullable=False)
    shares_after = Column(Numeric(18, 4), nullable=False)
    reference = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    transaction_date = Column(Date, nullable=False)

    # for transfers: counterpart account
    processed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    account = relationship(
        "ShareAccount", foreign_keys=[account_id], back_populates="transactions"
    )
    ledger_entry = relationship("LedgerEntry")
    processed_by = relationship("User")


class Dividend(TimestampMixin, Base):
    """A declared dividend for a share product covering a given financial period."""

    __tablename__ = "dividends"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("share_products.id"), nullable=False
    )

    period_label = Column(String(50), nullable=False)  # e.g. "FY2024"
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    rate_percent = Column(Numeric(5, 2), nullable=False)  # dividend rate %
    total_amount = Column(Numeric(18, 4), nullable=False)  # total pool declared
    status = Column(
        String(50),
        ForeignKey("dividend_statuses.code"),
        default="DRAFT",
        nullable=False,
    )
    status_obj = relationship(
        "DividendStatus",
        back_populates="dividends",
        uselist=False,
        lazy="joined",
        foreign_keys=[status],
    )
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    product = relationship("ShareProduct", back_populates="dividends")
    payments = relationship(
        "DividendPayment", back_populates="dividend", lazy="select"
    )


class DividendPayment(TimestampMixin, Base):
    """Per-member disbursement record for a declared Dividend."""

    __tablename__ = "dividend_payments"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    dividend_id = Column(
        UUID(as_uuid=True), ForeignKey("dividends.id"), nullable=False, index=True
    )
    share_account_id = Column(
        UUID(as_uuid=True), ForeignKey("share_accounts.id"), nullable=False, index=True
    )
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)

    shares_at_record = Column(Numeric(18, 4), nullable=False)  # holding at record date
    amount = Column(Numeric(18, 4), nullable=False)
    paid_date = Column(Date, nullable=True)
    payment_method = Column(String(50), nullable=True)  # e.g. "CASH", "MOBILE_MONEY"
    reference = Column(String(100), nullable=True)
    ledger_entry_id = Column(
        UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=True
    )

    dividend = relationship("Dividend", back_populates="payments")
    share_account = relationship("ShareAccount", back_populates="dividend_payments")
    ledger_entry = relationship("LedgerEntry")
