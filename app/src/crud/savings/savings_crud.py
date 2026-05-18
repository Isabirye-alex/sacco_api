from sqlalchemy.orm import Session

from app.src.models.savings import SavingsProduct, SavingsAccount, SavingsTransaction
from app.src.schemas.savings import (
    SavingsProductCreate,
    SavingsAccountCreate,
    SavingsTransactionCreate,
)


def create_savings_product(db: Session, product: SavingsProductCreate):
    db_product = SavingsProduct(
        organisation_id=product.organisation_id,
        name=product.name,
        code=product.code,
        product_type=product.product_type,
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
    db_account = SavingsAccount(
        organisation_id=account.organisation_id,
        branch_id=account.branch_id,
        member_id=account.member_id,
        product_id=account.product_id,
        account_no=account.account_no,
        balance=account.balance,
        status=account.status,
        opened_date=account.opened_date,
        closed_date=account.closed_date,
        maturity_date=account.maturity_date,
        notes=account.notes,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def create_savings_transaction(db: Session, tx: SavingsTransactionCreate):
    db_tx = SavingsTransaction(
        organisation_id=tx.organisation_id,
        account_id=tx.account_id,
        ledger_entry_id=tx.ledger_entry_id,
        tx_type=tx.tx_type,
        amount=tx.amount,
        balance_after=tx.balance_after,
        reference=tx.reference,
        description=tx.description,
        transaction_date=tx.transaction_date,
        processed_by_id=tx.processed_by_id,
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx
