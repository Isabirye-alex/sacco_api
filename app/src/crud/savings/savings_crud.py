from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.src.models.savings import (
    SavingsProduct,
    SavingsAccount,
    SavingsTransaction,
    SavingsProductType,
    SavingsAccountStatus,
    SavingsTxType,
)
from app.src.dependencies.lookups import (
    _SAVINGS_PRODUCT_TYPES,
    _SAVINGS_ACCOUNT_STATUSES,
    _SAVINGS_TX_TYPES,
)
from app.src.schemas.savings import (
    SavingsProductCreate,
    SavingsAccountCreate,
    SavingsTransactionCreate,
)
from app.src.utils.generate_random_account_number import generate_unique_account_no

def _resolve_savings_product_type_id(db: Session, code: str):
    valid_codes = {item["code"] for item in _SAVINGS_PRODUCT_TYPES}
    if code not in valid_codes:
        raise ValueError(f"Invalid savings product type: {code}")

    product_type = db.query(SavingsProductType).filter_by(code=code).first()
    if not product_type:
        product_type = SavingsProductType(code=code, description=code)
        db.add(product_type)
        db.flush()
    return product_type.id


def _resolve_savings_account_status_id(db: Session, code: str):
    valid_codes = {item["code"] for item in _SAVINGS_ACCOUNT_STATUSES}
    if code not in valid_codes:
        raise ValueError(f"Invalid savings account status: {code}")

    status = db.query(SavingsAccountStatus).filter_by(code=code).first()
    if not status:
        status = SavingsAccountStatus(code=code, description=code)
        db.add(status)
        db.flush()
    return status.id


def _resolve_savings_tx_type_id(db: Session, code: str):
    valid_codes = {item["code"] for item in _SAVINGS_TX_TYPES}
    if code not in valid_codes:
        raise ValueError(f"Invalid savings transaction type: {code}")

    tx_type = db.query(SavingsTxType).filter_by(code=code).first()
    if not tx_type:
        tx_type = SavingsTxType(code=code, description=code)
        db.add(tx_type)
        db.flush()
    return tx_type.id


def create_savings_product(db: Session, product: SavingsProductCreate):
    product_type_id = _resolve_savings_product_type_id(
        db, product.product_type or _SAVINGS_PRODUCT_TYPES[0]["code"]
    )
    db_product = SavingsProduct(
        organisation_id=product.organisation_id,
        name=product.name,
        code=product.code,
        product_type=product.product_type,
        product_type_id=product_type_id,
        description=product.description,
        interest_rate_pa=product.interest_rate_pa,
        min_opening_balance=product.min_opening_balance,
        min_balance=product.min_balance,
        max_balance=product.max_balance,
        withdrawal_allowed=product.withdrawal_allowed,
        lock_period_days=product.lock_period_days,
        is_active=product.is_active,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def create_savings_account(db: Session, account: SavingsAccountCreate):
    
    account_number = generate_unique_account_no(db)

    db_account = SavingsAccount(
        branch_id=account.branch_id,
        member_id=account.member_id,
        product_id=account.product_id,
        account_no=account_number,
        balance=account.balance,
        status_id=account.status_id,
        opened_date=account.opened_date,
        closed_date=account.closed_date,
        maturity_date=account.maturity_date,
        notes=account.notes,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def deposit(db: Session, tx: SavingsTransactionCreate):
    # 1. Fetch and Lock the user's savings account to ensure mathematical absolute accuracy
    # 'with_for_update' forces other simultaneous API threads to wait their turn
    account = (
        db.query(SavingsAccount)
        .filter(SavingsAccount.id == tx.account_id)
        .with_for_update()
        .first()
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target savings account not found."
        )

    # 2. Automatically compute the balance variables right here on the server
    current_balance = account.balance
    calculated_balance_after = current_balance + tx.amount

    # 3. Resolve your configuration properties
    tx_type_code = "DEPOSIT"
    tx_type_id = _resolve_savings_tx_type_id(db, tx_type_code)

    # 4. Create the historic audit entry
    db_tx = SavingsTransaction(
        organisation_id=tx.organisation_id,
        account_id=tx.account_id,
        ledger_entry_id=tx.ledger_entry_id,
        tx_type_id=tx_type_id,
        amount=tx.amount,
        
        #INJECT CALCULATED VALUE HERE
        balance_after=calculated_balance_after, 
        
        reference=tx.reference,
        description=tx.description or f"Deposit of UGX {tx.amount}",
        transaction_date=tx.transaction_date,
        processed_by_id=tx.processed_by_id,
    )
    db.add(db_tx)

    # 5. CRITICAL STEP: Update the actual running balance on the Savings Account row itself!
    account.balance = calculated_balance_after

    # 6. Commit both updates safely inside a single database transaction block
    db.commit()
    db.refresh(db_tx)
    
    return db_tx