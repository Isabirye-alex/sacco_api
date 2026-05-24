from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from decimal import Decimal
from app.src.models import (
    ShareAccount,
    ShareTransaction,
    Dividend,
    DividendPayment,
    LedgerEntry,
    LedgerLine,
)
from app.src.models.ledger import DR_CR_CREDIT, DR_CR_DEBIT


def purchase_shares_with_ledger(
    db: Session,
    member_id: UUID,
    product_id: UUID,
    num_shares: int,
    price_per_share: float,
    reference: str,
    user_id: UUID,
    payment_channel_code: str,
    branch_id: UUID,
):
    """
    Process member purchasing shares with double-entry ledger posting.
    """
    try:
        from app.src.models import ShareProduct, PaymentChannelConfiguration

        # 1. FETCH SHARE PRODUCT
        product = db.query(ShareProduct).filter(ShareProduct.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Share product not found")

        # 2. VALIDATE QUANTITY
        if num_shares < product.min_shares:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum shares required: {product.min_shares}",
            )

        if product.max_shares and num_shares > product.max_shares:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum shares allowed: {product.max_shares}",
            )

        # 3. CALCULATE TOTAL AMOUNT
        total_amount = num_shares * price_per_share

        # 4. GET PAYMENT CHANNEL
        channel_config = (
            db.query(PaymentChannelConfiguration)
            .filter(PaymentChannelConfiguration.channel_code == payment_channel_code)
            .first()
        )
        if not channel_config:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported payment channel: {payment_channel_code}",
            )

        # 5. GET OR CREATE SHARE ACCOUNT
        share_account = (
            db.query(ShareAccount)
            .filter(
                ShareAccount.member_id == member_id,
                ShareAccount.product_id == product_id,
            )
            .first()
        )

        if not share_account:
            share_account = ShareAccount(
                organisation_id=product.organisation_id,
                branch_id=branch_id,
                member_id=member_id,
                product_id=product_id,
                account_no=f"SHA-{member_id}-{product_id}",
                shares_held=0,
                total_value=0,
                is_active=True,
            )
            db.add(share_account)
            db.flush()

        # 6. CREATE LEDGER ENTRY
        ledger_entry = LedgerEntry(
            branch_id=branch_id,
            entry_no=f"JV-{reference}-{date.today().strftime('%Y%m%d')}",
            entry_type="SHARE_PURCHASE",
            entry_date=date.today(),
            description=f"Share Purchase - {num_shares} shares of {product.code}",
            reference=reference,
            total_debit=total_amount,
            total_credit=total_amount,
            status="POSTED",
            created_by_id=user_id,
        )
        db.add(ledger_entry)
        db.flush()

        # 7. CREATE LEDGER LINES
        # Line A: DEBIT Cash/Asset (increases asset)
        cash_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=channel_config.asset_account_id,
            dr_cr=DR_CR_DEBIT,
            amount=total_amount,
            description=f"Share purchase payment via {payment_channel_code}",
            member_id=member_id,
        )

        # Line B: CREDIT Share Capital (increases equity)
        share_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=product.share_capital_account_id,
            dr_cr=DR_CR_CREDIT,
            amount=total_amount,
            description=f"Share capital contribution for {product.code}",
            member_id=member_id,
        )

        db.add_all([cash_line, share_line])

        # 8. RECORD SHARE TRANSACTION
        shares_after = float(share_account.shares_held) + num_shares
        share_transaction = ShareTransaction(
            organisation_id=product.organisation_id,
            account_id=share_account.id,
            tx_type="PURCHASE",
            shares=num_shares,
            price_per_share=price_per_share,
            total_amount=total_amount,
            shares_after=shares_after,
            reference=reference,
            description=f"Purchase of {num_shares} shares",
            transaction_date=date.today(),
            processed_by_id=user_id,
            ledger_entry_id=ledger_entry.id,
        )
        db.add(share_transaction)

        # 9. UPDATE SHARE ACCOUNT
        share_account.shares_held = shares_after
        share_account.total_value = float(share_account.total_value) + total_amount
        db.add(share_account)
        db.commit()

        return {"transaction": share_transaction, "account": share_account}

    except Exception as e:
        db.rollback()
        raise e


def calculate_and_distribute_dividends(
    db: Session,
    dividend_id: UUID,
    user_id: UUID,
):
    """
    Calculate and distribute dividends to all share holders for a declared dividend.
    """
    try:
        # 1. FETCH DIVIDEND
        dividend = db.query(Dividend).filter(Dividend.id == dividend_id).first()
        if not dividend:
            raise HTTPException(status_code=404, detail="Dividend not found")

        if dividend.status != "DECLARED":
            raise HTTPException(
                status_code=400,
                detail=f"Dividend status is {dividend.status}, cannot distribute",
            )

        # 2. GET ALL SHARE ACCOUNTS FOR THIS PRODUCT
        accounts = (
            db.query(ShareAccount)
            .filter(ShareAccount.product_id == dividend.product_id)
            .all()
        )

        product = dividend.product
        total_distributed = 0
        dividend_payments = []

        # 3. CALCULATE PAYMENT FOR EACH ACCOUNT
        for account in accounts:
            if float(account.shares_held) == 0:
                continue

            # Dividend = shares_held * nominal_value * dividend_rate%
            payment_amount = (
                float(account.shares_held)
                * float(product.nominal_value)
                * (float(dividend.rate_percent) / 100)
            )

            if payment_amount == 0:
                continue

            # 4. CREATE LEDGER ENTRY FOR THIS PAYMENT
            ledger_entry = LedgerEntry(
                branch_id=account.branch_id,
                entry_no=f"DIV-{dividend.id}-{account.id}",
                entry_type="DIVIDEND_PAYMENT",
                entry_date=date.today(),
                description=f"Dividend Payment - {product.code}",
                reference=f"DIVIDEND-{dividend.id}",
                total_debit=payment_amount,
                total_credit=payment_amount,
                status="POSTED",
                created_by_id=user_id,
            )
            db.add(ledger_entry)
            db.flush()

            # 5. CREATE LEDGER LINES
            # Line A: DEBIT Dividend Expense
            expense_line = LedgerLine(
                entry_id=ledger_entry.id,
                account_id=product.dividend_expense_account_id,
                dr_cr=DR_CR_DEBIT,
                amount=payment_amount,
                description=f"Dividend expense for {product.code}",
                member_id=account.member_id,
            )

            # Line B: CREDIT Dividends Payable (if you use this account)
            # or CREDIT Cash/Member Account
            payable_line = LedgerLine(
                entry_id=ledger_entry.id,
                account_id=product.dividend_payable_account_id,
                dr_cr=DR_CR_CREDIT,
                amount=payment_amount,
                description=f"Dividend payable to member",
                member_id=account.member_id,
            )

            db.add_all([expense_line, payable_line])

            # 6. RECORD DIVIDEND PAYMENT
            payment = DividendPayment(
                dividend_id=dividend_id,
                share_account_id=account.id,
                amount=payment_amount,
                payment_date=date.today(),
                ledger_entry_id=ledger_entry.id,
            )
            db.add(payment)
            dividend_payments.append(payment)
            total_distributed += payment_amount

        # 7. UPDATE DIVIDEND STATUS
        dividend.status = "DISTRIBUTED"
        dividend.total_amount = Decimal(str(total_distributed))
        db.add(dividend)

        db.commit()

        return {
            "dividend": dividend,
            "payments": dividend_payments,
            "total_distributed": total_distributed,
        }

    except Exception as e:
        db.rollback()
        raise e


def declare_dividend(
    db: Session,
    product_id: UUID,
    period_label: str,
    period_start: date,
    period_end: date,
    rate_percent: float,
    user_id: UUID,
):
    """
    Declare a new dividend for a share product.
    Status starts as DRAFT and can be moved to DECLARED for distribution.
    """
    try:
        from app.src.models import Organisation

        # Get product to get organisation_id
        product = db.query(ShareProduct).filter(ShareProduct.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Share product not found")

        # Calculate total based on all shareholders
        share_accounts = (
            db.query(ShareAccount).filter(ShareAccount.product_id == product_id).all()
        )

        total_amount = 0
        for account in share_accounts:
            total_amount += (
                float(account.shares_held)
                * float(product.nominal_value)
                * (rate_percent / 100)
            )

        dividend = Dividend(
            organisation_id=product.organisation_id,
            product_id=product_id,
            period_label=period_label,
            period_start=period_start,
            period_end=period_end,
            rate_percent=rate_percent,
            total_amount=Decimal(str(total_amount)),
            status="DRAFT",
            created_by_id=user_id,
        )
        db.add(dividend)
        db.commit()

        return dividend

    except Exception as e:
        db.rollback()
        raise e
