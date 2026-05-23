from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from app.src.crud.savings.savings_crud import _resolve_savings_tx_type_id
from app.src.models import SavingsAccount, SavingsTransaction, LedgerEntry, LedgerLine

def execute_savings_deposit_with_ledger(
    db: Session,
    account_id: UUID,
    amount: float,
    reference: str,
    member_id: UUID,
    cash_gl_account_id: UUID,  # e.g., Cash in Vault GL UUID
    savings_gl_account_id: UUID,  # e.g., Member Savings Control GL UUID
):
    try:
        # 1. LOCK & UPDATE SAVINGS ACCOUNT
        account = (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == account_id)
            .with_for_update(of=SavingsAccount)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="Savings account not found")

        balance_after = float(account.balance) + amount

        # 2. CREATE THE LEDGER ENTRY HEADER
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
            created_by_id=member_id,
        )
        db.add(ledger_entry)
        db.flush()

        # 3. CREATE LEDGER LINE 1: DEBIT CASH (Asset up)
        cash_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=cash_gl_account_id,  
            dr_cr="DR",  # 🚀 FIXED: Changed from "CREDIT" to "DR" to reflect an asset increase
            amount=amount,
            description=f"Cash received for deposit on {account.account_no}",
            member_id=account.member_id,
        )

        # 4. CREATE LEDGER LINE 2: CREDIT SAVINGS CONTROL (Liability up)
        savings_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=savings_gl_account_id,  
            dr_cr="CR",  # 🚀 Note: Ensure your DB uses "DR"/"CR" pairs globally, not "DEBIT"/"CREDIT"
            amount=amount,
            description=f"Savings provision for member account {account.account_no}",
            member_id=account.member_id,
        )
        db.add_all([cash_line, savings_line])

        # 5. CREATE SAVINGS TRANSACTION LINKED TO THE LEDGER
        savings_tx = SavingsTransaction(
            account_id=account.id,
            ledger_entry_id=ledger_entry.id,
            tx_type_id=_resolve_savings_tx_type_id(db, "DEPOSIT"),
            amount=amount,
            balance_after=balance_after,
            reference=reference,
            description=f"Cash Deposit via Ledger Entry {ledger_entry.entry_no}",
            transaction_date=date.today(),
            processed_by_id=member_id,
        )
        db.add(savings_tx)

        account.balance = balance_after

        # 6. ATOMIC TRANSACTION COMMIT
        db.commit()
        db.refresh(savings_tx)
        return savings_tx

    except Exception as e:
        db.rollback() 
        print(f"Database Exception Logged: {str(e)}") # Useful for console debugging
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction processing aborted: {str(e)}",
        )