from sqlalchemy.orm import Session
from uuid import UUID
from app.src.models import SavingsTransaction, SavingsAccount


def get_savings_transactions(
    db: Session,
    account_id: UUID,
    skip: int = 0,
    limit: int = 50,
):
    """Get transaction history for a savings account."""
    return (
        db.query(SavingsTransaction)
        .filter(SavingsTransaction.account_id == account_id)
        .order_by(SavingsTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_account_balance(db: Session, account_id: UUID):
    """Get current balance of a savings account."""
    account = db.query(SavingsAccount).filter(SavingsAccount.id == account_id).first()
    if not account:
        return None

    return {
        "account_id": account.id,
        "account_no": account.account_no,
        "balance": float(account.balance),
        "member_id": account.member_id,
        "product_id": account.product_id,
    }
