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
    LoanProduct,
)
from app.src.models.ledger import (
    LedgerAccountType,
    LedgerAccountCategory,
    LedgerEntryType,
    LedgerDrCr,
    LedgerEntryStatus,
    ChartOfAccount,
)
from app.src.models.savings import (
    SavingsProductType,
    SavingsAccountStatus,
    SavingsTxType,
    SavingsProduct,
    PaymentChannelConfiguration,
)
from app.src.models.shares import (
    ShareProductType,
    ShareTransactionType,
    DividendStatus,
)

# Roles


_LOAN_PRODUCTS = [
    {
        "name": "Business Loan",
        "code": "BIZ_LOAN",
        "description": "Designed for entrepreneurs looking to start a new venture or boost working capital for an existing business. Examples include purchasing retail inventory, expanding shop premises, or funding upfront marketing campaigns.",
        "interest_rate_pa": "12.5",
        "min_term_months": 3,
        "max_term_months": 36,
        "min_amount": 500000,
        "max_amount": 15000000,
        "loan_to_savings_ratio": 4.0,
        "loan_to_shares_ratio": 3.0,
        "min_guarantors": 2,
    },
    {
        "name": "Emergency Loan",
        "code": "EMG_LOAN",
        "description": "Provides instant, short-term cash injections for urgent, unexpected personal crises. Examples include dealing with sudden legal fees, urgent family travel, or minor home repairs caused by storms.",
        "interest_rate_pa": "15.0",
        "min_term_months": 1,
        "max_term_months": 6,
        "min_amount": 100000,
        "max_amount": 2000000,
        "loan_to_savings_ratio": 2.0,
        "loan_to_shares_ratio": 2.0,
        "min_guarantors": 1,
    },
    {
        "name": "School Fees Loan",
        "code": "SCH_LOAN",
        "description": "Tailored to help parents and guardians bridge financing gaps for education expenses. Examples include paying termly primary/secondary school tuition, university enrollment fees, and purchasing mandatory text books or uniforms.",
        "interest_rate_pa": "10.0",
        "min_term_months": 1,
        "max_term_months": 4,
        "min_amount": 200000,
        "max_amount": 5000000,
        "loan_to_savings_ratio": 3.0,
        "loan_to_shares_ratio": 2.0,
        "min_guarantors": 1,
    },
    {
        "name": "Housing Loan",
        "code": "HOU_LOAN",
        "description": "A long-term credit facility for property development and home ownership. Examples include purchasing building materials (cement, bricks, roofing), funding major home renovations, or buying a residential plot of land.",
        "interest_rate_pa": "9.5",
        "min_term_months": 6,
        "max_term_months": 60,
        "min_amount": 2000000,
        "max_amount": 50000000,
        "loan_to_savings_ratio": 5.0,
        "loan_to_shares_ratio": 4.0,
        "min_guarantors": 3,
    },
    {
        "name": "Motorcycle Loan",
        "code": "MT_LOAN",
        "description": "An asset-linked loan to help riders acquire brand new or certified pre-owned motorcycles. Examples include buying a motorcycle for personal commuting or setting up a commercial Boda Boda / delivery transport business.",
        "interest_rate_pa": "14.0",
        "min_term_months": 3,
        "max_term_months": 24,
        "min_amount": 1500000,
        "max_amount": 7000000,
        "loan_to_savings_ratio": 3.0,
        "loan_to_shares_ratio": 2.5,
        "min_guarantors": 2,
    },
    {
        "name": "Agriculture Loan",
        "code": "AGR_LOAN",
        "description": "Flexible credit structures tailored to match the seasonal harvest cycles of farming. Examples include buying high-yield seeds, fertilizers, livestock feed, or investing in small-scale drip irrigation equipment.",
        "interest_rate_pa": "8.5",
        "min_term_months": 3,
        "max_term_months": 12,
        "min_amount": 300000,
        "max_amount": 10000000,
        "loan_to_savings_ratio": 3.0,
        "loan_to_shares_ratio": 2.0,
        "min_guarantors": 2,
    },
    {
        "name": "Salary Loan",
        "code": "SA_LOAN",
        "description": "Unsecured personal credit advanced directly to formally employed individuals based on their salary history. Examples include bridging mid-month budget deficits, buying household electronics, or funding holiday travel.",
        "interest_rate_pa": "13.5",
        "min_term_months": 1,
        "max_term_months": 24,
        "min_amount": 500000,
        "max_amount": 12000000,
        "loan_to_savings_ratio": 3.5,
        "loan_to_shares_ratio": 3.0,
        "min_guarantors": 1,
    },
    {
        "name": "Enterprise Loan",
        "code": "ENT_LOAN",
        "description": "High-value commercial financing targeting registered Small and Medium Enterprises (SMEs) requiring heavy structural investments. Examples include purchasing factory machinery, fleet vehicles, or financing large corporate tenders.",
        "interest_rate_pa": "11.0",
        "min_term_months": 6,
        "max_term_months": 48,
        "min_amount": 10000000,
        "max_amount": 100000000,
        "loan_to_savings_ratio": 5.0,
        "loan_to_shares_ratio": 4.0,
        "min_guarantors": 3,
    },
    {
        "name": "Asset Financing Loan",
        "code": "AST_LOAN",
        "description": "Credit focused strictly on buying physical equipment where the asset itself acts as partial collateral. Examples include buying commercial refrigerators, salon equipment, laptops for office work, or power generators.",
        "interest_rate_pa": "12.0",
        "min_term_months": 3,
        "max_term_months": 24,
        "min_amount": 1000000,
        "max_amount": 20000000,
        "loan_to_savings_ratio": 4.0,
        "loan_to_shares_ratio": 3.0,
        "min_guarantors": 2,
    },
    {
        "name": "Medical Emergency Loan",
        "code": "MED_LOAN",
        "description": "A highly discounted emergency product to cover sudden healthcare bills. Examples include funding unexpected surgical procedures, clearing hospital admission deposits, or purchasing expensive prescription chronic medication.",
        "interest_rate_pa": "7.0",
        "min_term_months": 1,
        "max_term_months": 12,
        "min_amount": 200000,
        "max_amount": 5000000,
        "loan_to_savings_ratio": 2.0,
        "loan_to_shares_ratio": 1.5,
        "min_guarantors": 1,
    },
    {
        "name": "Green/Solar Loan",
        "code": "GRN_LOAN",
        "description": "Eco-friendly financing promoting renewable energy adoption. Examples include purchasing solar home systems (panels, inverters, batteries), bio-gas installations, or energy-efficient cooking stoves.",
        "interest_rate_pa": "6.5",
        "min_term_months": 2,
        "max_term_months": 18,
        "min_amount": 300000,
        "max_amount": 4000000,
        "loan_to_savings_ratio": 2.5,
        "loan_to_shares_ratio": 2.0,
        "min_guarantors": 1,
    },
    # --- NEW EXTENSIONS ADDED BELOW ---
    {
        "name": "Land/Plot Purchase Loan",
        "code": "LND_LOAN",
        "description": "Specifically for acquiring raw land, residential plots, or commercial real estate space. Unlike housing loans, this covers raw property acquisition without active building timelines.",
        "interest_rate_pa": "10.5",
        "min_term_months": 6,
        "max_term_months": 48,
        "min_amount": 3000000,
        "max_amount": 40000000,
        "loan_to_savings_ratio": 4.5,
        "loan_to_shares_ratio": 3.5,
        "min_guarantors": 3,
    },
    {
        "name": "Commercial Vehicle Loan",
        "code": "CVH_LOAN",
        "description": "Tailored for business logistics expansion. Examples include buying agricultural tractors, transport delivery trucks, corporate staff vans, or commercial minibuses (matatus).",
        "interest_rate_pa": "11.5",
        "min_term_months": 6,
        "max_term_months": 36,
        "min_amount": 5000000,
        "max_amount": 60000000,
        "loan_to_savings_ratio": 4.0,
        "loan_to_shares_ratio": 3.5,
        "min_guarantors": 3,
    },
    {
        "name": "Group / Chama Loan",
        "code": "GRP_LOAN",
        "description": "Advanced exclusively to registered self-help groups, investment clubs, or Chamas. Examples include joint land purchases, funding collective table-banking capital, or joint market stalls setup.",
        "interest_rate_pa": "9.0",
        "min_term_months": 3,
        "max_term_months": 24,
        "min_amount": 2000000,
        "max_amount": 30000000,
        "loan_to_savings_ratio": 5.0,
        "loan_to_shares_ratio": 4.0,
        "min_guarantors": 0,  # Group funds & cross-guaranteeing acts as security
    },
    {
        "name": "Festival & Holiday Loan",
        "code": "FST_LOAN",
        "description": "Short-term consumer credit to handle cyclical seasonal pressures. Examples include funding family travel during major festive seasons (Christmas, Eid), holiday gifting, or major cultural family obligations.",
        "interest_rate_pa": "14.5",
        "min_term_months": 1,
        "max_term_months": 4,
        "min_amount": 150000,
        "max_amount": 2500000,
        "loan_to_savings_ratio": 2.0,
        "loan_to_shares_ratio": 1.5,
        "min_guarantors": 1,
    },
    {
        "name": "Refinancing Top-Up Loan",
        "code": "TPU_LOAN",
        "description": "Allows active borrowers in good standing to pull extra equity before completing their current cycle. Examples include adding cash to an ongoing project or managing an extension on a business facility.",
        "interest_rate_pa": "13.0",
        "min_term_months": 3,
        "max_term_months": 18,
        "min_amount": 500000,
        "max_amount": 8000000,
        "loan_to_savings_ratio": 3.0,
        "loan_to_shares_ratio": 2.5,
        "min_guarantors": 2,
    },
    {
        "name": "LPO Financing Loan",
        "code": "LPO_LOAN",
        "description": "Bridge financing for contractors holding valid Local Purchase Orders or supply contracts. Examples include fulfilling government supply tenders, buying raw materials to execute corporate manufacturing orders.",
        "interest_rate_pa": "14.0",
        "min_term_months": 1,
        "max_term_months": 6,
        "min_amount": 2000000,
        "max_amount": 30000000,
        "loan_to_savings_ratio": 4.0,
        "loan_to_shares_ratio": 3.0,
        "min_guarantors": 2,
    },
    {
        "name": "Insurance Premium Financing",
        "code": "IPF_LOAN",
        "description": "A niche micro-loan designed to split annual comprehensive insurance costs into predictable installments. Examples include paying annual commercial vehicle covers or medical insurance premiums.",
        "interest_rate_pa": "10.0",
        "min_term_months": 1,
        "max_term_months": 10,
        "min_amount": 300000,
        "max_amount": 5000000,
        "loan_to_savings_ratio": 2.5,
        "loan_to_shares_ratio": 2.0,
        "min_guarantors": 1,
    },
    {
        "name": "Agent Banking Float Loan",
        "code": "FLT_LOAN",
        "description": "Ultra-fast working capital advanced to mobile money agents and fintech kiosks. Examples include boosting instant float availability for heavy deposit/withdrawal days like holidays or weekends.",
        "interest_rate_pa": "16.0",
        "min_term_months": 1,
        "max_term_months": 3,
        "min_amount": 100000,
        "max_amount": 3000000,
        "loan_to_savings_ratio": 2.0,
        "loan_to_shares_ratio": 1.5,
        "min_guarantors": 1,
    },
]

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


# Default Chart of Accounts
# Note: These are templates to be seeded per-organization.
# Set organisation_id when seeding to link to a specific org.
_DEFAULT_CHART_OF_ACCOUNTS = [
    # ========== ASSET ACCOUNTS ==========
    # Cash Accounts
    {
        "name": "1000 - Cash in Vault",
        "account_type": "ASSET",
        "account_category": "CASH",
        "description": "Physical cash held at office/branch.",
        "is_system": True,
    },
    {
        "name": "1100 - Cash at Bank",
        "account_type": "ASSET",
        "account_category": "BANK",
        "description": "Cash deposits in bank accounts.",
        "is_system": True,
    },
    {
        "name": "1200 - Mobile Money Holdings",
        "account_type": "ASSET",
        "account_category": "MOBILE_MONEY",
        "description": "Balance in mobile money merchant accounts.",
        "is_system": True,
    },
    # Receivables
    {
        "name": "1300 - Loans Receivable",
        "account_type": "ASSET",
        "account_category": "LOANS_RECEIVABLE",
        "description": "Outstanding member loans.",
        "is_system": True,
    },
    {
        "name": "1310 - Interest Receivable (Loans)",
        "account_type": "ASSET",
        "account_category": "INTEREST_RECEIVABLE",
        "description": "Accrued interest on member loans.",
        "is_system": True,
    },
    {
        "name": "1400 - Fees Receivable",
        "account_type": "ASSET",
        "account_category": "LOANS_RECEIVABLE",
        "description": "Outstanding fee charges.",
        "is_system": True,
    },
    # Fixed Assets
    {
        "name": "1500 - Equipment",
        "account_type": "ASSET",
        "account_category": None,
        "description": "Office equipment and fixtures.",
        "is_system": True,
    },
    {
        "name": "1510 - Accumulated Depreciation - Equipment",
        "account_type": "ASSET",
        "account_category": None,
        "description": "Accumulated depreciation on equipment.",
        "is_system": True,
    },
    # ========== LIABILITY ACCOUNTS ==========
    # Member Deposits/Savings
    {
        "name": "2100 - Member Savings (Control)",
        "account_type": "LIABILITY",
        "account_category": "MEMBER_SAVINGS",
        "description": "Total member savings liability - control account.",
        "is_system": True,
    },
    {
        "name": "2200 - Member Share Capital",
        "account_type": "LIABILITY",
        "account_category": "MEMBER_SHARES",
        "description": "Member share contributions (equity-like but classified as liability).",
        "is_system": True,
    },
    {
        "name": "2300 - Dividends Payable",
        "account_type": "LIABILITY",
        "account_category": "DIVIDENDS_PAYABLE",
        "description": "Accrued dividends awaiting payment.",
        "is_system": True,
    },
    {
        "name": "2400 - Interest Payable",
        "account_type": "LIABILITY",
        "account_category": None,
        "description": "Interest accrued on member deposits.",
        "is_system": True,
    },
    {
        "name": "2500 - Loans Payable (Borrowed)",
        "account_type": "LIABILITY",
        "account_category": None,
        "description": "Amounts borrowed by SACCO from external sources.",
        "is_system": True,
    },
    {
        "name": "2600 - Payroll Liabilities",
        "account_type": "LIABILITY",
        "account_category": None,
        "description": "Accrued staff salaries and benefits payable.",
        "is_system": True,
    },
    # ========== EQUITY ACCOUNTS ==========
    {
        "name": "3100 - Retained Earnings",
        "account_type": "EQUITY",
        "account_category": "RETAINED_EARNINGS",
        "description": "Cumulative profits retained in the organisation.",
        "is_system": True,
    },
    {
        "name": "3200 - General Reserve",
        "account_type": "EQUITY",
        "account_category": "RESERVE_FUND",
        "description": "Mandatory general reserve for regulatory compliance.",
        "is_system": True,
    },
    {
        "name": "3300 - Loan Loss Provision/Reserve",
        "account_type": "EQUITY",
        "account_category": "RESERVE_FUND",
        "description": "Reserve for potential loan losses.",
        "is_system": True,
    },
    {
        "name": "3400 - Emergency Fund",
        "account_type": "EQUITY",
        "account_category": "RESERVE_FUND",
        "description": "Emergency/liquidity reserve.",
        "is_system": True,
    },
    # ========== INCOME ACCOUNTS ==========
    {
        "name": "4100 - Interest Income (Loans)",
        "account_type": "INCOME",
        "account_category": "INTEREST_INCOME",
        "description": "Interest earned from member loans.",
        "is_system": True,
    },
    {
        "name": "4200 - Fee Income",
        "account_type": "INCOME",
        "account_category": "FEE_INCOME",
        "description": "Fees charged for services (application, account, etc.).",
        "is_system": True,
    },
    {
        "name": "4300 - Penalty Income",
        "account_type": "INCOME",
        "account_category": "PENALTY_INCOME",
        "description": "Late fees, penalty charges on loans/accounts.",
        "is_system": True,
    },
    {
        "name": "4400 - Dividend Income",
        "account_type": "INCOME",
        "account_category": None,
        "description": "Dividends received from investments.",
        "is_system": True,
    },
    {
        "name": "4500 - Other Income",
        "account_type": "INCOME",
        "account_category": None,
        "description": "Miscellaneous income sources.",
        "is_system": True,
    },
    # ========== EXPENSE ACCOUNTS ==========
    {
        "name": "5100 - Staff Salaries & Benefits",
        "account_type": "EXPENSE",
        "account_category": "OPERATING_EXPENSE",
        "description": "Staff compensation and benefits.",
        "is_system": True,
    },
    {
        "name": "5200 - Operating Expenses",
        "account_type": "EXPENSE",
        "account_category": "OPERATING_EXPENSE",
        "description": "General office operations (utilities, rent, supplies).",
        "is_system": True,
    },
    {
        "name": "5300 - Interest Expense (Borrowed Funds)",
        "account_type": "EXPENSE",
        "account_category": "INTEREST_EXPENSE",
        "description": "Interest paid on external borrowings.",
        "is_system": True,
    },
    {
        "name": "5400 - Depreciation Expense",
        "account_type": "EXPENSE",
        "account_category": "OPERATING_EXPENSE",
        "description": "Depreciation on fixed assets.",
        "is_system": True,
    },
    {
        "name": "5500 - Loan Loss Provision Expense",
        "account_type": "EXPENSE",
        "account_category": "LOAN_LOSS_PROVISION",
        "description": "Expense for building loan loss reserves.",
        "is_system": True,
    },
    {
        "name": "5600 - Audit & Compliance Fees",
        "account_type": "EXPENSE",
        "account_category": "OPERATING_EXPENSE",
        "description": "External audit and compliance-related costs.",
        "is_system": True,
    },
    {
        "name": "5700 - Training & Development",
        "account_type": "EXPENSE",
        "account_category": "OPERATING_EXPENSE",
        "description": "Staff training and development programs.",
        "is_system": True,
    },
    {
        "name": "5800 - Miscellaneous Expenses",
        "account_type": "EXPENSE",
        "account_category": "OPERATING_EXPENSE",
        "description": "Other operating expenses.",
        "is_system": True,
    },
]


# Payment Channel Configurations
_PAYMENT_CHANNELS = [
    {
        "channel_code": "CASH",
        "channel_name": "Cash Payment",
        "account_name": "1000 - Cash in Vault",
    },
    {
        "channel_code": "BANK",
        "channel_name": "Bank Transfer",
        "account_name": "1100 - Cash at Bank",
    },
    {
        "channel_code": "MOBILE_MONEY",
        "channel_name": "Mobile Money",
        "account_name": "1200 - Mobile Money Holdings",
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


def seed_loan_products(db: Session) -> None:
    """Insert system loan products if they don't exist."""
    existing = {l.code for l in db.query(LoanProduct).all()}
    for row in _LOAN_PRODUCTS:
        if row["code"] not in existing:
            db.add(LoanProduct(**row))
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


def seed_default_chart_of_accounts(db: Session) -> None:
    """
    Seed default chart of accounts globally for the system.

    This is idempotent - existing accounts won't be duplicated.
    """
    existing_names = {acc.name for acc in db.query(ChartOfAccount.name).all()}

    any_new_items = False

    for row in _DEFAULT_CHART_OF_ACCOUNTS:
        if row["name"] in existing_names:
            continue

        db.add(ChartOfAccount(**row))
        any_new_items = True

    if any_new_items:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise


def seed_payment_channels(db: Session) -> None:
    """
    Seed payment channel configurations globally for the system.

    Maps user-friendly payment channels (CASH, BANK, MOBILE_MONEY)
    to corresponding Chart of Accounts (asset accounts).

    This is idempotent - existing channels won't be duplicated.
    """
    existing_codes = {
        ch.channel_code
        for ch in db.query(PaymentChannelConfiguration.channel_code).all()
    }

    for row in _PAYMENT_CHANNELS:
        if row["channel_code"] in existing_codes:
            continue

        # Look up the corresponding chart of accounts by name
        account = db.query(ChartOfAccount).filter_by(name=row["account_name"]).first()

        if not account:
            # Skip if account not found (shouldn't happen if chart seeded first)
            continue

        # Create the payment channel configuration
        payment_channel = PaymentChannelConfiguration(
            channel_code=row["channel_code"],
            channel_name=row["channel_name"],
            asset_account_id=account.id,
        )
        db.add(payment_channel)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def seed_lookups(db: Session) -> None:
    """
    Convenience function — seeds all system-wide lookup tables in one call.
    This is called on application startup before anything else.

    Usage in main.py:
        @app.on_event("startup")
        def startup():
            db = next(get_db())
            seed_lookups(db)

    This also creates default savings/loan products and chart of accounts.
    """
    seed_roles(db)
    seed_genders(db)
    seed_user_types(db)
    seed_member_statuses(db)
    seed_loan_products(db)
    seed_default_chart_of_accounts(db)
    seed_payment_channels(db)
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
