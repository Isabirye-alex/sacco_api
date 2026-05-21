from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
    Boolean,
    Date,
    Integer,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.models.base_file import Base, TimestampMixin

LEDGER_ACCOUNT_TYPE_ASSET = "ASSET"
LEDGER_ACCOUNT_TYPE_EXPENSE = "EXPENSE"
DR_CR_DEBIT = "DEBIT"
DR_CR_CREDIT = "CREDIT"


class LedgerAccountType(TimestampMixin, Base):
    __tablename__ = "ledger_account_types"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    accounts = relationship(
        "ChartOfAccount",
        back_populates="account_type_obj",
        lazy="dynamic",
        foreign_keys="ChartOfAccount.account_type",
    )


class LedgerAccountCategory(TimestampMixin, Base):
    __tablename__ = "ledger_account_categories"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    accounts = relationship(
        "ChartOfAccount",
        back_populates="account_category_obj",
        lazy="dynamic",
        foreign_keys="ChartOfAccount.account_category",
    )


class LedgerEntryType(TimestampMixin, Base):
    __tablename__ = "ledger_entry_types"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    entries = relationship(
        "LedgerEntry",
        back_populates="entry_type_obj",
        lazy="dynamic",
        foreign_keys="LedgerEntry.entry_type",
    )


class LedgerDrCr(TimestampMixin, Base):
    __tablename__ = "ledger_dr_crs"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    lines = relationship(
        "LedgerLine",
        back_populates="dr_cr_obj",
        lazy="dynamic",
        foreign_keys="LedgerLine.dr_cr",
    )


class LedgerEntryStatus(TimestampMixin, Base):
    __tablename__ = "ledger_entry_statuses"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    entries = relationship(
        "LedgerEntry",
        back_populates="status_obj",
        lazy="dynamic",
        foreign_keys="LedgerEntry.status",
    )


class ChartOfAccount(TimestampMixin, Base):
    """
    The organisation's chart of accounts.
    Standard accounts can be seeded at org creation; custom ones can be added.
    """

    __tablename__ = "chart_of_accounts"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False, unique=True)
    account_type = Column(
        String(50),
        ForeignKey("ledger_account_types.code"),
        nullable=False,
    )
    account_category = Column(
        String(50),
        ForeignKey("ledger_account_categories.code"),
        nullable=True,
    )
    parent_id = Column(
        UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=True
    )
    account_type_obj = relationship(
        "LedgerAccountType",
        back_populates="accounts",
        uselist=False,
        lazy="joined",
        foreign_keys=[account_type],
    )
    account_category_obj = relationship(
        "LedgerAccountCategory",
        back_populates="accounts",
        uselist=False,
        lazy="joined",
        foreign_keys=[account_category],
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
    def normal_balance(self) -> str:
        if self.account_type in (
            LEDGER_ACCOUNT_TYPE_ASSET,
            LEDGER_ACCOUNT_TYPE_EXPENSE,
        ):
            return DR_CR_DEBIT
        return DR_CR_CREDIT


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
    entry_type = Column(
        String(50),
        ForeignKey("ledger_entry_types.code"),
        nullable=False,
    )
    entry_type_obj = relationship(
        "LedgerEntryType",
        back_populates="entries",
        uselist=False,
        lazy="joined",
        foreign_keys=[entry_type],
    )
    entry_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    reference = Column(
        String(100), nullable=True
    )  # external ref (e.g. mobile money ID)

    total_debit = Column(Numeric(18, 4), nullable=False)
    total_credit = Column(Numeric(18, 4), nullable=False)

    status = Column(
        String(50),
        ForeignKey("ledger_entry_statuses.code"),
        default="POSTED",
        nullable=False,
    )
    status_obj = relationship(
        "LedgerEntryStatus",
        back_populates="entries",
        uselist=False,
        lazy="joined",
        foreign_keys=[status],
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

    dr_cr = Column(
        String(50),
        ForeignKey("ledger_dr_crs.code"),
        nullable=False,
    )
    dr_cr_obj = relationship(
        "LedgerDrCr",
        back_populates="lines",
        uselist=False,
        lazy="joined",
        foreign_keys=[dr_cr],
    )
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
