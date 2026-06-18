"""Module for app.src.crud.shares.share_crud."""

from sqlalchemy.orm import Session

from app.src.models.shares import (
    ShareProduct,
    ShareAccount,
    ShareTransaction,
    Dividend,
    DividendPayment,
)
from app.src.schemas.shares.share_schema import (
    ShareProductCreate,
    ShareAccountCreate,
    ShareTransactionCreate,
    DividendCreate,
    DividendPaymentCreate,
)


def create_share_product(db: Session, product: ShareProductCreate):
    db_product = ShareProduct(
        organisation_id=product.organisation_id,
        name=product.name,
        code=product.code,
        product_type=product.product_type,
        description=product.description,
        nominal_value=product.nominal_value,
        min_shares=product.min_shares,
        max_shares=product.max_shares,
        is_transferable=product.is_transferable,
        is_redeemable=product.is_redeemable,
        is_active=product.is_active,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def create_share_account(db: Session, account: ShareAccountCreate):
    db_account = ShareAccount(
        organisation_id=account.organisation_id,
        branch_id=account.branch_id,
        member_id=account.member_id,
        product_id=account.product_id,
        account_no=account.account_no,
        shares_held=account.shares_held,
        total_value=account.total_value,
        is_active=account.is_active,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def create_share_transaction(db: Session, tx: ShareTransactionCreate):
    db_tx = ShareTransaction(
        organisation_id=tx.organisation_id,
        account_id=tx.account_id,
        ledger_entry_id=tx.ledger_entry_id,
        tx_type=tx.tx_type,
        shares=tx.shares,
        price_per_share=tx.price_per_share,
        total_amount=tx.total_amount,
        shares_after=tx.shares_after,
        reference=tx.reference,
        description=tx.description,
        transaction_date=tx.transaction_date,
        processed_by_id=tx.processed_by_id,
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx


def create_dividend(db: Session, dividend: DividendCreate):
    db_dividend = Dividend(
        organisation_id=dividend.organisation_id,
        product_id=dividend.product_id,
        period_label=dividend.period_label,
        period_start=dividend.period_start,
        period_end=dividend.period_end,
        rate_percent=dividend.rate_percent,
        total_amount=dividend.total_amount,
        status=dividend.status,
        approved_by_id=dividend.approved_by_id,
        approved_date=dividend.approved_date,
        notes=dividend.notes,
    )
    db.add(db_dividend)
    db.commit()
    db.refresh(db_dividend)
    return db_dividend


def create_dividend_payment(db: Session, payment: DividendPaymentCreate):
    db_payment = DividendPayment(
        organisation_id=payment.organisation_id,
        dividend_id=payment.dividend_id,
        share_account_id=payment.share_account_id,
        member_id=payment.member_id,
        shares_at_record=payment.shares_at_record,
        amount=payment.amount,
        paid_date=payment.paid_date,
        payment_method=payment.payment_method,
        reference=payment.reference,
        ledger_entry_id=payment.ledger_entry_id,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment
