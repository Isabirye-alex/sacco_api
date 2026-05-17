"""
Transactions & Ledger (Double-Entry Accounting)
================================================
ChartOfAccount    – the SACCO's chart of accounts
LedgerEntry       – a balanced journal entry (header)
LedgerLine        – individual debit / credit lines (must balance per entry)
JournalEntry      – manual/corrective journal entries
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
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.config.base_file import Base, TimestampMixin

# ─── Enumerations ────────────────────────────────────────────────────────────


class AccountTypeEnum(str, enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class AccountCategoryEnum(str, enum.Enum):
    # Assets
    CASH = "CASH"
    BANK = "BANK"
    MOBILE_MONEY = "MOBILE_MONEY"
    LOANS_RECEIVABLE = "LOANS_RECEIVABLE"
    INTEREST_RECEIVABLE = "INTEREST_RECEIVABLE"
    # Liabilities
    MEMBER_SAVINGS = "MEMBER_SAVINGS"
    MEMBER_SHARES = "MEMBER_SHARES"
    DIVIDENDS_PAYABLE = "DIVIDENDS_PAYABLE"
    # Equity
    RETAINED_EARNINGS = "RETAINED_EARNINGS"
    RESERVE_FUND = "RESERVE_FUND"
    # Income
    INTEREST_INCOME = "INTEREST_INCOME"
    FEE_INCOME = "FEE_INCOME"
    PENALTY_INCOME = "PENALTY_INCOME"
    # Expense
    OPERATING_EXPENSE = "OPERATING_EXPENSE"
    INTEREST_EXPENSE = "INTEREST_EXPENSE"
    LOAN_LOSS_PROVISION = "LOAN_LOSS_PROVISION"


class LedgerEntryTypeEnum(str, enum.Enum):
    SAVINGS_DEPOSIT = "SAVINGS_DEPOSIT"
    SAVINGS_WITHDRAWAL = "SAVINGS_WITHDRAWAL"
    SAVINGS_INTEREST = "SAVINGS_INTEREST"
    SHARE_PURCHASE = "SHARE_PURCHASE"
    SHARE_REDEMPTION = "SHARE_REDEMPTION"
    DIVIDEND_PAYMENT = "DIVIDEND_PAYMENT"
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    LOAN_REPAYMENT = "LOAN_REPAYMENT"
    LOAN_PENALTY = "LOAN_PENALTY"
    FEE_CHARGE = "FEE_CHARGE"
    JOURNAL = "JOURNAL"  # manual / corrective
    TRANSFER = "TRANSFER"


class DrCrEnum(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class LedgerEntryStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    POSTED = "POSTED"
    REVERSED = "REVERSED"
    VOIDED = "VOIDED"


# ─── Models ──────────────────────────────────────────────────────────────────


class ChartOfAccount(TimestampMixin, Base):
    """
    The organisation's chart of accounts.
    Standard accounts can be seeded at org creation; custom ones can be added.
    """

    __tablename__ = "chart_of_accounts"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    code = Column(String(20), nullable=False)  # e.g. "1001"
    name = Column(String(255), nullable=False)
    account_type = Column(SAEnum(AccountTypeEnum), nullable=False)
    account_category = Column(SAEnum(AccountCategoryEnum), nullable=True)
    parent_id = Column(
        UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=True
    )
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(
        Boolean, default=False, nullable=False
    )  # system-managed; cannot be deleted

    parent = relationship(
        "ChartOfAccount", remote_side="ChartOfAccount.id", backref="children"
    )
    lines = relationship("LedgerLine", back_populates="account", lazy="dynamic")

    # normal balance side (ASSET/EXPENSE = DEBIT; LIABILITY/EQUITY/INCOME = CREDIT)
    @property
    def normal_balance(self) -> DrCrEnum:
        if self.account_type in (AccountTypeEnum.ASSET, AccountTypeEnum.EXPENSE):
            return DrCrEnum.DEBIT
        return DrCrEnum.CREDIT


class LedgerEntry(TimestampMixin, Base):
    """
    A balanced journal entry (header).  Every financial transaction that
    hits the books creates exactly one LedgerEntry + ≥2 LedgerLines.
    The sum of all DEBIT lines must equal the sum of all CREDIT lines.
    """

    __tablename__ = "ledger_entries"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    branch_id = Column(
        UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True
    )

    entry_no = Column(String(50), nullable=False)  # sequential per org
    entry_type = Column(SAEnum(LedgerEntryTypeEnum), nullable=False)
    entry_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    reference = Column(
        String(100), nullable=True
    )  # external ref (e.g. mobile money ID)

    total_debit = Column(Numeric(18, 4), nullable=False)
    total_credit = Column(Numeric(18, 4), nullable=False)

    status = Column(
        SAEnum(LedgerEntryStatusEnum),
        default=LedgerEntryStatusEnum.POSTED,
        nullable=False,
    )
    reversal_of_id = Column(
        UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=True
    )
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    lines = relationship("LedgerLine", back_populates="entry", lazy="dynamic")
    reversal_of = relationship(
        "LedgerEntry", remote_side="LedgerEntry.id", foreign_keys=[reversal_of_id]
    )
    created_by = relationship("User")

    __table_args__ = (
        CheckConstraint("total_debit = total_credit", name="ck_ledger_balanced"),
    )


class LedgerLine(TimestampMixin, Base):
    """
    A single debit or credit line within a LedgerEntry.
    At least two lines per entry; debits must equal credits.
    """

    __tablename__ = "ledger_lines"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    entry_id = Column(
        UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=False, index=True
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chart_of_accounts.id"),
        nullable=False,
        index=True,
    )

    dr_cr = Column(SAEnum(DrCrEnum), nullable=False)
    amount = Column(Numeric(18, 4), nullable=False)
    description = Column(Text, nullable=True)

    # optional: which member this line relates to (for sub-ledger reporting)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)

    entry = relationship("LedgerEntry", back_populates="lines")
    account = relationship("ChartOfAccount", back_populates="lines")
    member = relationship("Member")

    __table_args__ = (CheckConstraint("amount > 0", name="ck_ledger_line_positive"),)


class JournalEntry(TimestampMixin, Base):
    """
    Manual / corrective journal entry.  Always linked to a LedgerEntry
    which carries the actual accounting impact.
    """

    __tablename__ = "journal_entries"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    branch_id = Column(
        UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True
    )
    ledger_entry_id = Column(
        UUID(as_uuid=True), ForeignKey("ledger_entries.id"), nullable=False, unique=True
    )

    narration = Column(Text, nullable=False)
    prepared_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    is_approved = Column(Boolean, default=False, nullable=False)

    ledger_entry = relationship("LedgerEntry")
    prepared_by = relationship("User", foreign_keys=[prepared_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
