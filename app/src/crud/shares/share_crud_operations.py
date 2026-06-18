"""Module for app.src.crud.shares.share_crud_operations."""

from sqlalchemy.orm import Session
from uuid import UUID
from app.src.models import ShareAccount, ShareTransaction, Dividend


def get_member_share_accounts(
    db: Session,
    member_id: UUID,
):
    """Get all share accounts for a member."""
    return db.query(ShareAccount).filter(ShareAccount.member_id == member_id).all()


def get_share_account_by_id(db: Session, account_id: UUID):
    """Get a specific share account."""
    return db.query(ShareAccount).filter(ShareAccount.id == account_id).first()


def get_share_transactions(
    db: Session,
    account_id: UUID,
    skip: int = 0,
    limit: int = 50,
):
    """Get transaction history for a share account."""
    return (
        db.query(ShareTransaction)
        .filter(ShareTransaction.account_id == account_id)
        .order_by(ShareTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_product_dividends(
    db: Session,
    product_id: UUID,
):
    """Get all dividends declared for a product."""
    return (
        db.query(Dividend)
        .filter(Dividend.product_id == product_id)
        .order_by(Dividend.created_at.desc())
        .all()
    )


def get_dividend_by_id(db: Session, dividend_id: UUID):
    """Get a specific dividend."""
    return db.query(Dividend).filter(Dividend.id == dividend_id).first()


def get_member_shareholdings(
    db: Session,
    member_id: UUID,
):
    """Get summary of all share holdings for a member."""
    accounts = get_member_share_accounts(db, member_id)
    holdings = []

    for account in accounts:
        holdings.append(
            {
                "product_id": account.product_id,
                "product_name": account.product.name,
                "shares_held": float(account.shares_held),
                "total_value": float(account.total_value),
                "account_no": account.account_no,
            }
        )

    return holdings
