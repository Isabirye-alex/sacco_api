"""Module for app.services.transaction_ledger_service."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from app.src.crud.savings.savings_crud import _resolve_savings_tx_type_id
from app.src.models import SavingsAccount, SavingsTransaction, LedgerEntry, LedgerLine, User
from app.src.models.ledger import DR_CR_CREDIT, DR_CR_DEBIT
from app.src.models.savings import PaymentChannelConfiguration, SavingsProduct


def execute_savings_deposit_with_ledger(
    db: Session,
    account_id: UUID,
    amount: float,
    reference: str,
    user_id: UUID,
    payment_channel_code: str,
):
    try:
        # Resolve actual User ID (the input user_id from token is likely a member_id)
        user = db.query(User).filter((User.id == user_id) | (User.member_id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        actual_user_id = user.id

        # 1. LOCK & LOCATE THE SAVINGS ACCOUNT
        account = (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == account_id)
            .with_for_update(of=SavingsAccount)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="Savings account not found")

        # 2. AUTOMATICALLY RESOLVE CREDIT SIDE: Fetch the associated Product Config
        product = (
            db.query(SavingsProduct)
            .filter(SavingsProduct.id == account.product_id)
            .first()
        )
        if not product:
            raise HTTPException(
                status_code=404, detail="Associated savings product definition missing"
            )

        savings_gl_account_id = product.savings_control_account_id
        if not savings_gl_account_id:
            raise HTTPException(
                status_code=500,
                detail="Product misconfiguration: No control ledger linked to this product type.",
            )

        # 3. AUTOMATICALLY RESOLVE DEBIT SIDE: Fetch the asset account using the channel code
        channel_config = (
            db.query(PaymentChannelConfiguration)
            .filter(PaymentChannelConfiguration.channel_code == payment_channel_code)
            .first()
        )
        if not channel_config:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported or inactive payment option: {payment_channel_code}",
            )
        cash_gl_account_id = channel_config.asset_account_id

        balance_after = float(account.balance) + amount

        # 4. INITIALIZE BALANCE SHEET HEADER
        ledger_entry = LedgerEntry(
            branch_id=account.branch_id,
            entry_no=f"JV-{reference}-{date.today().strftime('%Y%m%d')}",
            entry_type="SAVINGS_DEPOSIT",
            entry_date=date.today(),
            description=f"Savings Deposit - Account {account.account_no}",
            reference=reference,
            total_debit=amount,
            total_credit=amount,
            status="POSTED",
            created_by_id=actual_user_id,
        )
        db.add(ledger_entry)
        db.flush()

        # 5. GENERATE DOUBLE-ENTRY LEDGER LINES
        # Line A: DEBIT Cash/Asset Account (Increases Asset)
        cash_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=cash_gl_account_id,
            dr_cr=DR_CR_DEBIT,  # Uses your global "DEBIT" model constant string
            amount=amount,
            description=f"Deposit via channel [{payment_channel_code}] into account {account.account_no}",
            member_id=account.member_id,
        )

        # Line B: CREDIT Member Savings Liability Account (Increases Liability)
        savings_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=savings_gl_account_id,
            dr_cr=DR_CR_CREDIT,  # Uses your global "CREDIT" model constant string
            amount=amount,
            description=f"Savings allocation for member account {account.account_no}",
            member_id=account.member_id,
        )
        db.add_all([cash_line, savings_line])

        # 6. UPDATE ACCOUNT BALANCE
        account.balance = balance_after
        db.add(account)

        # 7. CREATE SAVINGS TRANSACTION RECORD
        tx_type_id = _resolve_savings_tx_type_id(db, "DEPOSIT")
        savings_tx = SavingsTransaction(
            account_id=account_id,
            tx_type_id=tx_type_id,
            amount=amount,
            balance_after=balance_after,
            reference=reference,
            description=f"Deposit via {payment_channel_code}",
            transaction_date=date.today(),
            processed_by_id=user_id,
            ledger_entry_id=ledger_entry.id,
        )
        db.add(savings_tx)
        db.commit()

        return savings_tx

    except Exception as e:
        db.rollback()
        raise e


def execute_savings_withdrawal_with_ledger(
    db: Session,
    account_id: UUID,
    amount: float,
    reference: str,
    user_id: UUID,
    payment_channel_code: str,
):
    """Withdrawal from savings account with double-entry ledger posting."""
    try:
        # Resolve actual User ID
        user = db.query(User).filter((User.id == user_id) | (User.member_id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        actual_user_id = user.id

        # 1. LOCK & LOCATE THE SAVINGS ACCOUNT
        account = (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == account_id)
            .with_for_update(of=SavingsAccount)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="Savings account not found")

        # 2. CHECK SUFFICIENT BALANCE
        if float(account.balance) < amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available: {account.balance}, Requested: {amount}",
            )

        # 3. AUTOMATICALLY RESOLVE CREDIT SIDE: Fetch the associated Product Config
        product = (
            db.query(SavingsProduct)
            .filter(SavingsProduct.id == account.product_id)
            .first()
        )
        if not product:
            raise HTTPException(
                status_code=404, detail="Associated savings product definition missing"
            )

        savings_gl_account_id = product.savings_control_account_id
        if not savings_gl_account_id:
            raise HTTPException(
                status_code=500,
                detail="Product misconfiguration: No control ledger linked to this product type.",
            )

        # 4. AUTOMATICALLY RESOLVE DEBIT SIDE: Fetch the asset account using the channel code
        channel_config = (
            db.query(PaymentChannelConfiguration)
            .filter(PaymentChannelConfiguration.channel_code == payment_channel_code)
            .first()
        )
        if not channel_config:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported or inactive payment option: {payment_channel_code}",
            )
        cash_gl_account_id = channel_config.asset_account_id

        balance_after = float(account.balance) - amount

        # 5. INITIALIZE BALANCE SHEET HEADER
        ledger_entry = LedgerEntry(
            branch_id=account.branch_id,
            entry_no=f"JV-{reference}-{date.today().strftime('%Y%m%d')}",
            entry_type="SAVINGS_WITHDRAWAL",
            entry_date=date.today(),
            description=f"Savings Withdrawal - Account {account.account_no}",
            reference=reference,
            total_debit=amount,
            total_credit=amount,
            status="POSTED",
            created_by_id=actual_user_id,
        )
        db.add(ledger_entry)
        db.flush()

        # 6. GENERATE DOUBLE-ENTRY LEDGER LINES
        # Line A: CREDIT Cash/Asset Account (Decreases Asset)
        cash_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=cash_gl_account_id,
            dr_cr=DR_CR_CREDIT,  # Credit to reduce asset
            amount=amount,
            description=f"Withdrawal via channel [{payment_channel_code}] from account {account.account_no}",
            member_id=account.member_id,
        )

        # Line B: DEBIT Member Savings Liability Account (Decreases Liability)
        savings_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=savings_gl_account_id,
            dr_cr=DR_CR_DEBIT,  # Debit to reduce liability
            amount=amount,
            description=f"Savings withdrawal from member account {account.account_no}",
            member_id=account.member_id,
        )
        db.add_all([cash_line, savings_line])

        # 7. UPDATE ACCOUNT BALANCE
        account.balance = balance_after
        db.add(account)

        # 8. CREATE SAVINGS TRANSACTION RECORD
        tx_type_id = _resolve_savings_tx_type_id(db, "WITHDRAWAL")
        savings_tx = SavingsTransaction(
            account_id=account_id,
            tx_type_id=tx_type_id,
            amount=amount,
            balance_after=balance_after,
            reference=reference,
            description=f"Withdrawal via {payment_channel_code}",
            transaction_date=date.today(),
            processed_by_id=user_id,
            ledger_entry_id=ledger_entry.id,
        )
        db.add(savings_tx)
        db.commit()

        return savings_tx

    except Exception as e:
        db.rollback()
        print(e)
        raise e


def execute_fund_transfer_with_ledger(
    db: Session,
    from_account_id: UUID,
    to_account_id: UUID,
    amount: float,
    reference: str,
    user_id: UUID,
):
    """Transfer funds from one savings account to another with ledger posting."""
    try:
        # Resolve actual User ID
        user = db.query(User).filter((User.id == user_id) | (User.member_id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        actual_user_id = user.id

        # 1. LOCK & LOCATE BOTH ACCOUNTS
        from_account = (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == from_account_id)
            .with_for_update(of=SavingsAccount)
            .first()
        )
        if not from_account:
            raise HTTPException(status_code=404, detail="Source account not found")

        to_account = (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == to_account_id)
            .with_for_update(of=SavingsAccount)
            .first()
        )
        if not to_account:
            raise HTTPException(status_code=404, detail="Destination account not found")

        # 2. CHECK SUFFICIENT BALANCE
        if float(from_account.balance) < amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available: {from_account.balance}, Requested: {amount}",
            )

        from_product = (
            db.query(SavingsProduct)
            .filter(SavingsProduct.id == from_account.product_id)
            .first()
        )
        to_product = (
            db.query(SavingsProduct)
            .filter(SavingsProduct.id == to_account.product_id)
            .first()
        )

        # 3. INITIALIZE BALANCE SHEET HEADER
        ledger_entry = LedgerEntry(
            branch_id=from_account.branch_id,
            entry_no=f"JV-{reference}-{date.today().strftime('%Y%m%d')}",
            entry_type="FUND_TRANSFER",
            entry_date=date.today(),
            description=f"Fund Transfer from {from_account.account_no} to {to_account.account_no}",
            reference=reference,
            total_debit=amount,
            total_credit=amount,
            status="POSTED",
            created_by_id=actual_user_id,
        )
        db.add(ledger_entry)
        db.flush()

        # 4. GENERATE DOUBLE-ENTRY LEDGER LINES
        # Line A: DEBIT Receiver's Account (Increases Liability)
        receiver_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=to_product.savings_control_account_id,
            dr_cr=DR_CR_DEBIT,
            amount=amount,
            description=f"Fund received from {from_account.account_no}",
            member_id=to_account.member_id,
        )

        # Line B: CREDIT Sender's Account (Decreases Liability)
        sender_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=from_product.savings_control_account_id,
            dr_cr=DR_CR_CREDIT,
            amount=amount,
            description=f"Fund transferred to {to_account.account_no}",
            member_id=from_account.member_id,
        )
        db.add_all([receiver_line, sender_line])

        # 5. UPDATE BOTH ACCOUNT BALANCES
        from_account.balance = float(from_account.balance) - amount
        to_account.balance = float(to_account.balance) + amount
        db.add_all([from_account, to_account])

        # 6. CREATE TRANSACTION RECORDS FOR BOTH ACCOUNTS
        tx_type_id = _resolve_savings_tx_type_id(db, "TRANSFER")

        from_tx = SavingsTransaction(
            account_id=from_account_id,
            tx_type_id=tx_type_id,
            amount=amount,
            balance_after=from_account.balance,
            reference=reference,
            description=f"Transfer to account {to_account.account_no}",
            transaction_date=date.today(),
            processed_by_id=user_id,
            ledger_entry_id=ledger_entry.id,
        )

        to_tx = SavingsTransaction(
            account_id=to_account_id,
            tx_type_id=tx_type_id,
            amount=amount,
            balance_after=to_account.balance,
            reference=reference,
            description=f"Transfer from account {from_account.account_no}",
            transaction_date=date.today(),
            processed_by_id=user_id,
            ledger_entry_id=ledger_entry.id,
        )
        db.add_all([from_tx, to_tx])
        db.commit()

        return {"from_transaction": from_tx, "to_transaction": to_tx}

    except Exception as e:
        db.rollback()
        raise e
