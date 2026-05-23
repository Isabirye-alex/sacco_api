from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from app.src.crud.savings.savings_crud import _resolve_savings_tx_type_id
from app.src.models import SavingsAccount, SavingsTransaction, LedgerEntry, LedgerLine
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
            created_by_id=user_id,
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

        # 6. LOG LOCAL TRANSACTIONS HISTORIES
        savings_tx = SavingsTransaction(
            account_id=account.id,
            ledger_entry_id=ledger_entry.id,
            tx_type_id=_resolve_savings_tx_type_id(db, "DEPOSIT"),
            amount=amount,
            balance_after=balance_after,
            reference=reference,
            description=f"Deposit via Ledger Entry {ledger_entry.entry_no}",
            transaction_date=date.today(),
            processed_by_id=user_id,
        )
        db.add(savings_tx)

        # Apply structural mutations safely within block bounds
        account.balance = balance_after

        # 7. COMMIT ATOMIC CHANGES
        db.commit()
        db.refresh(savings_tx)
        return savings_tx

    except Exception as e:
        print(e)
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction runtime aborted: {str(e)}",
        )
