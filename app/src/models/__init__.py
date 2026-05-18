"""
app.src.models
==============
Central export point for all ORM models.
Alembic's env.py imports from here to register all models on Base.metadata.
"""

from app.src.config.base_file import Base, TimestampMixin  # noqa: F401

# ── Multi-tenancy ──────────────────────────────────────────────────────────
from app.src.models.tenant import Organisation, Branch  # noqa: F401

# ── Members & Auth ─────────────────────────────────────────────────────────
from app.src.models.member import (
    MaritalStatus,
    MemberStatus,
    Member,
    NextOfKin,
    User,
    Role,
    UserTypeEnum,
)

# ── Savings ────────────────────────────────────────────────────────────────
from app.src.models.savings import (
    SavingsProduct,
    SavingsAccount,
    SavingsTransaction,
    SavingsProductTypeEnum,
    SavingsAccountStatusEnum,
    SavingsTxTypeEnum,
)

# ── Shares / Equity ───────────────────────────────────────────────────────-
from app.src.models.shares import (  # noqa: F401
    ShareProduct,
    ShareAccount,
    ShareTransaction,
    Dividend,
    DividendPayment,
    ShareProductTypeEnum,
    ShareTxTypeEnum,
    DividendStatusEnum,
)

# ── Loans & Repayments ───────────────────────────────────────────────────-
from app.src.models.loans import (  # noqa: F401
    LoanProduct,
    LoanApplication,
    Loan,
    LoanGuarantor,
    LoanCollateral,
    LoanRepaymentSchedule,
    LoanRepayment,
    LoanPenalty,
    RepaymentFrequencyEnum,
    InterestMethodEnum,
    LoanApplicationStatusEnum,
    LoanStatusEnum,
    CollateralTypeEnum,
    PenaltyTypeEnum,
)

# ── Ledger / Double-Entry ─────────────────────────────────────────────────
from app.src.models.ledger import (  # noqa: F401
    ChartOfAccount,
    LedgerEntry,
    LedgerLine,
    JournalEntry,
    AccountTypeEnum,
    AccountCategoryEnum,
    LedgerEntryTypeEnum,
    DrCrEnum,
    LedgerEntryStatusEnum,
)

# ── Users & Auth (existing) ───────────────────────────────────────────────
from app.src.models.users.login_logs import LoginLogs  # noqa: F401

__all__ = [
    "Base",
    "TimestampMixin",
    # tenant
    "Organisation",
    "Branch",
    # member
    "MaritalStatus",
    "MemberStatus",
    "Member",
    "User",
    "NextOfKin",
    "Role",
    "UserTypeEnum",
    # savings
    "SavingsProduct",
    "SavingsAccount",
    "SavingsTransaction",
    "SavingsProductTypeEnum",
    "SavingsAccountStatusEnum",
    "SavingsTxTypeEnum",
    # shares
    "ShareProduct",
    "ShareAccount",
    "ShareTransaction",
    "Dividend",
    "DividendPayment",
    "ShareProductTypeEnum",
    "ShareTxTypeEnum",
    "DividendStatusEnum",
    # loans
    "LoanProduct",
    "LoanApplication",
    "Loan",
    "LoanGuarantor",
    "LoanCollateral",
    "LoanRepaymentSchedule",
    "LoanRepayment",
    "LoanPenalty",
    "RepaymentFrequencyEnum",
    "InterestMethodEnum",
    "LoanApplicationStatusEnum",
    "LoanStatusEnum",
    "CollateralTypeEnum",
    "PenaltyTypeEnum",
    # ledger
    "ChartOfAccount",
    "LedgerEntry",
    "LedgerLine",
    "JournalEntry",
    "AccountTypeEnum",
    "AccountCategoryEnum",
    "LedgerEntryTypeEnum",
    "DrCrEnum",
    "LedgerEntryStatusEnum",
    # users (existing)
    "LoginLogs",
]
