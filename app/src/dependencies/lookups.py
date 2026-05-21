"""
seeds/lookups.py
Seeds all admin-managed lookup tables that back the Member & Auth models.

Called once on application starts up (it is idempotent).
These are global tables (not per-organisation) so they are seeded once
for the whole platform.
"""

from sqlalchemy.orm import Session

from app.src.models.member import Gender, MemberStatus, MaritalStatus, Role, UserType
from app.src.models.loans import (
    LoanInterestMethod,
    LoanRepaymentFrequency,
    LoanApplicationStatus,
    LoanStatus,
    LoanCollateralType,
    LoanPenaltyType,
)
from app.src.models.ledger import (
    LedgerAccountType,
    LedgerAccountCategory,
    LedgerEntryType,
    LedgerDrCr,
    LedgerEntryStatus,
)
from app.src.models.savings import (
    SavingsProductType,
    SavingsAccountStatus,
    SavingsTxType,
    SavingsProduct,
)
from app.src.models.shares import (
    ShareProductType,
    ShareTransactionType,
    DividendStatus,
)
from app.src.models.tenant import Organisation

# Roles

_ROLES = [
    {
        "role": "MEMBER",
        "description": "Regular SACCO member — portal access only.",
        "is_system": True,
    },
    {
        "role": "LOAN_OFFICER",
        "description": "Reviews and processes loan applications.",
        "is_system": True,
    },
    {
        "role": "TREASURER",
        "description": "Full access to savings, shares, and the ledger.",
        "is_system": True,
    },
    {
        "role": "BRANCH_MANAGER",
        "description": "Manages all operations within a single branch.",
        "is_system": True,
    },
    {
        "role": "ADMIN",
        "description": "Organisation-wide administration.",
        "is_system": True,
    },
    {
        "role": "SUPER_ADMIN",
        "description": "Platform-level access across all organisations.",
        "is_system": True,
    },
]


# Gender
_GENDERS = [
    {"gender": "Male", "description": None},
    {"gender": "Female", "description": None},
    {"gender": "Other", "description": None},
    {"gender": "Prefer not to say", "description": None},
]


#  Member Status

_MEMBER_STATUSES = [
    {"status": "Pending", "description": "Application submitted, awaiting approval."},
    {"status": "Active", "description": "Fully registered and active member."},
    {"status": "Dormant", "description": "No account activity for more than 6 months."},
    {
        "status": "Suspended",
        "description": "Temporarily suspended pending investigation.",
    },
    {
        "status": "Exited",
        "description": "Member has voluntarily withdrawn from the SACCO.",
    },
]


# Authentication / User Types
_USER_TYPES = [
    {"code": "MEMBER", "description": "Regular member portal user."},
    {"code": "STAFF", "description": "Staff or administrator account."},
]


# Loan lookups
_LOAN_INTEREST_METHODS = [
    {"code": "FLAT_RATE", "description": "Interest on original principal."},
    {"code": "REDUCING_BALANCE", "description": "Interest on outstanding balance."},
]

_LOAN_REPAYMENT_FREQUENCIES = [
    {"code": "DAILY", "description": "Daily repayment frequency."},
    {"code": "WEEKLY", "description": "Weekly repayment frequency."},
    {"code": "BIWEEKLY", "description": "Biweekly repayment frequency."},
    {"code": "MONTHLY", "description": "Monthly repayment frequency."},
    {"code": "QUARTERLY", "description": "Quarterly repayment frequency."},
    {"code": "ANNUALLY", "description": "Annual repayment frequency."},
    {"code": "LUMP_SUM", "description": "One-time lump sum repayment."},
]

_LOAN_APPLICATION_STATUSES = [
    {"code": "DRAFT", "description": "Draft application."},
    {"code": "SUBMITTED", "description": "Submitted for review."},
    {"code": "UNDER_REVIEW", "description": "Under review by staff."},
    {"code": "APPROVED", "description": "Approved loan application."},
    {"code": "REJECTED", "description": "Rejected application."},
    {"code": "WITHDRAWN", "description": "Withdrawn by applicant."},
]

_LOAN_STATUSES = [
    {"code": "PENDING", "description": "Approved, not yet disbursed."},
    {"code": "ACTIVE", "description": "Active loan."},
    {"code": "IN_ARREARS", "description": "Loan in arrears."},
    {"code": "WRITTEN_OFF", "description": "Loan written off."},
    {"code": "CLOSED", "description": "Closed loan."},
]

_LOAN_COLLATERAL_TYPES = [
    {"code": "LAND", "description": "Land collateral."},
    {"code": "VEHICLE", "description": "Vehicle collateral."},
    {"code": "BUILDING", "description": "Building collateral."},
    {"code": "EQUIPMENT", "description": "Equipment collateral."},
    {"code": "SAVINGS", "description": "Savings-backed collateral."},
    {"code": "SHARES", "description": "Shares-backed collateral."},
    {"code": "OTHER", "description": "Other collateral."},
]

_LOAN_PENALTY_TYPES = [
    {"code": "LATE_PAYMENT", "description": "Late payment penalty."},
    {"code": "MISSED_PAYMENT", "description": "Missed payment penalty."},
    {"code": "EARLY_CLOSURE", "description": "Early closure penalty."},
]


# Ledger lookups
_LEDGER_ACCOUNT_TYPES = [
    {"code": "ASSET", "description": "Asset account."},
    {"code": "LIABILITY", "description": "Liability account."},
    {"code": "EQUITY", "description": "Equity account."},
    {"code": "INCOME", "description": "Income account."},
    {"code": "EXPENSE", "description": "Expense account."},
]

_LEDGER_ACCOUNT_CATEGORIES = [
    {"code": "CASH", "description": "Cash account."},
    {"code": "BANK", "description": "Bank account."},
    {"code": "MOBILE_MONEY", "description": "Mobile money account."},
    {"code": "LOANS_RECEIVABLE", "description": "Loans receivable."},
    {"code": "INTEREST_RECEIVABLE", "description": "Interest receivable."},
    {"code": "MEMBER_SAVINGS", "description": "Member savings liability."},
    {"code": "MEMBER_SHARES", "description": "Member shares liability."},
    {"code": "DIVIDENDS_PAYABLE", "description": "Dividends payable liability."},
    {"code": "RETAINED_EARNINGS", "description": "Retained earnings."},
    {"code": "RESERVE_FUND", "description": "Reserve fund."},
    {"code": "INTEREST_INCOME", "description": "Interest income."},
    {"code": "FEE_INCOME", "description": "Fee income."},
    {"code": "PENALTY_INCOME", "description": "Penalty income."},
    {"code": "OPERATING_EXPENSE", "description": "Operating expense."},
    {"code": "INTEREST_EXPENSE", "description": "Interest expense."},
    {"code": "LOAN_LOSS_PROVISION", "description": "Loan loss provision."},
]

_LEDGER_ENTRY_TYPES = [
    {"code": "SAVINGS_DEPOSIT", "description": "Savings deposit entry."},
    {"code": "SAVINGS_WITHDRAWAL", "description": "Savings withdrawal entry."},
    {"code": "SAVINGS_INTEREST", "description": "Savings interest posting."},
    {"code": "SHARE_PURCHASE", "description": "Share purchase entry."},
    {"code": "SHARE_REDEMPTION", "description": "Share redemption entry."},
    {"code": "DIVIDEND_PAYMENT", "description": "Dividend payment entry."},
    {"code": "LOAN_DISBURSEMENT", "description": "Loan disbursement entry."},
    {"code": "LOAN_REPAYMENT", "description": "Loan repayment entry."},
    {"code": "LOAN_PENALTY", "description": "Loan penalty entry."},
    {"code": "FEE_CHARGE", "description": "Fee charge entry."},
    {"code": "JOURNAL", "description": "Journal entry."},
    {"code": "TRANSFER", "description": "Transfer entry."},
]

_LEDGER_DR_CR = [
    {"code": "DEBIT", "description": "Debit line."},
    {"code": "CREDIT", "description": "Credit line."},
]

_LEDGER_ENTRY_STATUSES = [
    {"code": "PENDING", "description": "Pending ledger posting."},
    {"code": "POSTED", "description": "Posted ledger entry."},
    {"code": "REVERSED", "description": "Reversed entry."},
    {"code": "VOIDED", "description": "Voided entry."},
]


# Share lookups
_SHARE_PRODUCT_TYPES = [
    {"code": "ORDINARY", "description": "Ordinary share product."},
    {"code": "PREFERENCE", "description": "Preference share product."},
    {"code": "BONUS", "description": "Bonus share product."},
]

_SHARE_TX_TYPES = [
    {"code": "PURCHASE", "description": "Share purchase transaction."},
    {"code": "TRANSFER", "description": "Share transfer transaction."},
    {"code": "REDEMPTION", "description": "Share redemption transaction."},
    {"code": "BONUS", "description": "Bonus share transaction."},
    {"code": "CORRECTION", "description": "Correction transaction."},
]

_DIVIDEND_STATUSES = [
    {"code": "DRAFT", "description": "Draft dividend."},
    {"code": "APPROVED", "description": "Approved dividend."},
    {"code": "PAID", "description": "Paid dividend."},
    {"code": "REVERSED", "description": "Reversed dividend."},
]


# Marital Status

_MARITAL_STATUSES = [
    {"status": "Single", "description": None},
    {"status": "Married", "description": None},
    {"status": "Widowed", "description": None},
    {"status": "Divorced", "description": None},
    {"status": "Separated", "description": None},
]


# Savings lookup definitions
_SAVINGS_PRODUCT_TYPES = [
    {"code": "ORDINARY", "description": "Regular passbook savings."},
    {"code": "FIXED_DEPOSIT", "description": "Locked for a term."},
    {"code": "GOAL", "description": "Target / purpose savings."},
    {"code": "EMERGENCY", "description": "Emergency fund."},
    {"code": "CHRISTMAS", "description": "Seasonal savings."},
]

_SAVINGS_ACCOUNT_STATUSES = [
    {"code": "ACTIVE", "description": "Account is active."},
    {"code": "DORMANT", "description": "Account is dormant."},
    {"code": "FROZEN", "description": "Account is frozen."},
    {"code": "CLOSED", "description": "Account is closed."},
]

_SAVINGS_TX_TYPES = [
    {"code": "DEPOSIT", "description": "Deposit transaction."},
    {"code": "WITHDRAWAL", "description": "Withdrawal transaction."},
    {"code": "INTEREST", "description": "Interest posting."},
    {"code": "CHARGE", "description": "Fee or charge."},
    {"code": "TRANSFER", "description": "Transfer transaction."},
]

_SAVINGS_PRODUCTS = [
    {
        "name": "Ordinary Savings",
        "code": "ORDINARY",
        "product_type": "ORDINARY",
        "description": "Regular savings with flexible deposits and withdrawals.",
        "interest_rate_pa": 8.5,
        "min_opening_balance": 50000,
        "min_balance": 50000,
        "max_balance": None,
        "withdrawal_allowed": True,
        "lock_period_days": 0,
        "is_active": True,
    },
    {
        "name": "Fixed Deposit",
        "code": "FIXED_DEPOSIT",
        "product_type": "FIXED_DEPOSIT",
        "description": "Locked deposit account with a fixed term.",
        "interest_rate_pa": 10.0,
        "min_opening_balance": 100000,
        "min_balance": 100000,
        "max_balance": None,
        "withdrawal_allowed": False,
        "lock_period_days": 365,
        "is_active": True,
    },
    {
        "name": "Goal Savings",
        "code": "GOAL",
        "product_type": "GOAL",
        "description": "Purpose-driven savings for a specific goal.",
        "interest_rate_pa": 8.0,
        "min_opening_balance": 10000,
        "min_balance": 0,
        "max_balance": None,
        "withdrawal_allowed": True,
        "lock_period_days": 0,
        "is_active": True,
    },
    {
        "name": "Emergency Savings",
        "code": "EMERGENCY",
        "product_type": "EMERGENCY",
        "description": "Savings for unplanned emergencies.",
        "interest_rate_pa": 7.5,
        "min_opening_balance": 10000,
        "min_balance": 0,
        "max_balance": None,
        "withdrawal_allowed": True,
        "lock_period_days": 0,
        "is_active": True,
    },
    {
        "name": "Christmas Savings",
        "code": "CHRISTMAS",
        "product_type": "CHRISTMAS",
        "description": "Seasonal savings for festive spending.",
        "interest_rate_pa": 8.0,
        "min_opening_balance": 10000,
        "min_balance": 0,
        "max_balance": None,
        "withdrawal_allowed": True,
        "lock_period_days": 0,
        "is_active": True,
    },
]


# Seed functions


def seed_roles(db: Session) -> None:
    """Insert system roles if they don't exist."""
    existing = {r.role for r in db.query(Role).all()}
    for row in _ROLES:
        if row["role"] not in existing:
            db.add(Role(**row))
    db.commit()


def seed_genders(db: Session) -> None:
    existing = {g.gender for g in db.query(Gender).all()}
    for row in _GENDERS:
        if row["gender"] not in existing:
            db.add(Gender(**row))
    db.commit()


def seed_member_statuses(db: Session) -> None:
    existing = {s.status for s in db.query(MemberStatus).all()}
    for row in _MEMBER_STATUSES:
        if row["status"] not in existing:
            db.add(MemberStatus(**row))
    db.commit()


def seed_user_types(db: Session) -> None:
    existing = {u.code for u in db.query(UserType).all()}
    for row in _USER_TYPES:
        if row["code"] not in existing:
            db.add(UserType(**row))
    db.commit()


def seed_marital_statuses(db: Session) -> None:
    existing = {s.status for s in db.query(MaritalStatus).all()}
    for row in _MARITAL_STATUSES:
        if row["status"] not in existing:
            db.add(MaritalStatus(**row))
    db.commit()


def seed_savings_product_types(db: Session) -> None:
    existing = {item.code for item in db.query(SavingsProductType).all()}
    for row in _SAVINGS_PRODUCT_TYPES:
        if row["code"] not in existing:
            db.add(SavingsProductType(**row))
    db.commit()


def seed_savings_account_statuses(db: Session) -> None:
    existing = {item.code for item in db.query(SavingsAccountStatus).all()}
    for row in _SAVINGS_ACCOUNT_STATUSES:
        if row["code"] not in existing:
            db.add(SavingsAccountStatus(**row))
    db.commit()


def seed_savings_tx_types(db: Session) -> None:
    existing = {item.code for item in db.query(SavingsTxType).all()}
    for row in _SAVINGS_TX_TYPES:
        if row["code"] not in existing:
            db.add(SavingsTxType(**row))
    db.commit()


def seed_savings_products(db: Session) -> None:
    # 1. Fetch ALL existing system-wide product codes into a set
    existing_codes = {item.code for item in db.query(SavingsProduct.code).all()}

    any_new_items = False

    for row in _SAVINGS_PRODUCTS:
        if row["code"] in existing_codes:
            continue

        product_type_code = row["product_type"]
        product_type = (
            db.query(SavingsProductType).filter_by(code=product_type_code).first()
        )

        if not product_type:
            product_type = SavingsProductType(
                code=product_type_code,
                description=product_type_code.replace(
                    "_", " "
                ).title(),  # Clean look: "FIXED_DEPOSIT" -> "Fixed Deposit"
            )
            db.add(product_type)
            db.flush()  # Flushes to get the product_type.id immediately

        # We extract 'product_type' so it doesn't break model unpacking with unexpected fields
        product_data = {k: v for k, v in row.items() if k != "product_type"}

        # 5. Build and stage the global product record
        db.add(SavingsProduct(product_type_id=product_type.id, **product_data))
        any_new_items = True

    # 6. Single atomic save for the entire system update
    if any_new_items:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise


def seed_loan_interest_methods(db: Session) -> None:
    existing = {item.code for item in db.query(LoanInterestMethod).all()}
    for row in _LOAN_INTEREST_METHODS:
        if row["code"] not in existing:
            db.add(LoanInterestMethod(**row))
    db.commit()


def seed_loan_repayment_frequencies(db: Session) -> None:
    existing = {item.code for item in db.query(LoanRepaymentFrequency).all()}
    for row in _LOAN_REPAYMENT_FREQUENCIES:
        if row["code"] not in existing:
            db.add(LoanRepaymentFrequency(**row))
    db.commit()


def seed_loan_application_statuses(db: Session) -> None:
    existing = {item.code for item in db.query(LoanApplicationStatus).all()}
    for row in _LOAN_APPLICATION_STATUSES:
        if row["code"] not in existing:
            db.add(LoanApplicationStatus(**row))
    db.commit()


def seed_loan_statuses(db: Session) -> None:
    existing = {item.code for item in db.query(LoanStatus).all()}
    for row in _LOAN_STATUSES:
        if row["code"] not in existing:
            db.add(LoanStatus(**row))
    db.commit()


def seed_loan_collateral_types(db: Session) -> None:
    existing = {item.code for item in db.query(LoanCollateralType).all()}
    for row in _LOAN_COLLATERAL_TYPES:
        if row["code"] not in existing:
            db.add(LoanCollateralType(**row))
    db.commit()


def seed_loan_penalty_types(db: Session) -> None:
    existing = {item.code for item in db.query(LoanPenaltyType).all()}
    for row in _LOAN_PENALTY_TYPES:
        if row["code"] not in existing:
            db.add(LoanPenaltyType(**row))
    db.commit()


def seed_ledger_account_types(db: Session) -> None:
    existing = {item.code for item in db.query(LedgerAccountType).all()}
    for row in _LEDGER_ACCOUNT_TYPES:
        if row["code"] not in existing:
            db.add(LedgerAccountType(**row))
    db.commit()


def seed_ledger_account_categories(db: Session) -> None:
    existing = {item.code for item in db.query(LedgerAccountCategory).all()}
    for row in _LEDGER_ACCOUNT_CATEGORIES:
        if row["code"] not in existing:
            db.add(LedgerAccountCategory(**row))
    db.commit()


def seed_ledger_entry_types(db: Session) -> None:
    existing = {item.code for item in db.query(LedgerEntryType).all()}
    for row in _LEDGER_ENTRY_TYPES:
        if row["code"] not in existing:
            db.add(LedgerEntryType(**row))
    db.commit()


def seed_ledger_dr_cr(db: Session) -> None:
    existing = {item.code for item in db.query(LedgerDrCr).all()}
    for row in _LEDGER_DR_CR:
        if row["code"] not in existing:
            db.add(LedgerDrCr(**row))
    db.commit()


def seed_ledger_entry_statuses(db: Session) -> None:
    existing = {item.code for item in db.query(LedgerEntryStatus).all()}
    for row in _LEDGER_ENTRY_STATUSES:
        if row["code"] not in existing:
            db.add(LedgerEntryStatus(**row))
    db.commit()


def seed_share_product_types(db: Session) -> None:
    existing = {item.code for item in db.query(ShareProductType).all()}
    for row in _SHARE_PRODUCT_TYPES:
        if row["code"] not in existing:
            db.add(ShareProductType(**row))
    db.commit()


def seed_share_transaction_types(db: Session) -> None:
    existing = {item.code for item in db.query(ShareTransactionType).all()}
    for row in _SHARE_TX_TYPES:
        if row["code"] not in existing:
            db.add(ShareTransactionType(**row))
    db.commit()


def seed_dividend_statuses(db: Session) -> None:
    existing = {item.code for item in db.query(DividendStatus).all()}
    for row in _DIVIDEND_STATUSES:
        if row["code"] not in existing:
            db.add(DividendStatus(**row))
    db.commit()


def seed_lookups(db: Session) -> None:
    """
    Convenience function — seeds all lookup tables in one call.
    Call this on application startup before anything else.

    Usage in main.py:
        @app.on_event("startup")
        def startup():
            db = next(get_db())
            seed_lookups(db)

    This also creates default savings product blueprints for any existing organisations.
    """
    seed_roles(db)
    seed_genders(db)
    seed_user_types(db)
    seed_member_statuses(db)
    seed_marital_statuses(db)
    seed_savings_product_types(db)
    seed_savings_account_statuses(db)
    seed_savings_tx_types(db)
    seed_loan_interest_methods(db)
    seed_loan_repayment_frequencies(db)
    seed_loan_application_statuses(db)
    seed_loan_statuses(db)
    seed_loan_collateral_types(db)
    seed_loan_penalty_types(db)
    seed_ledger_account_types(db)
    seed_ledger_account_categories(db)
    seed_ledger_entry_types(db)
    seed_ledger_dr_cr(db)
    seed_ledger_entry_statuses(db)
    seed_share_product_types(db)
    seed_share_transaction_types(db)
    seed_dividend_statuses(db)
    seed_savings_products(db)
