from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.services.transaction_ledger_service import (
    execute_savings_deposit_with_ledger,
    execute_savings_withdrawal_with_ledger,
    execute_fund_transfer_with_ledger,
)
from app.services.email_notification_service import email_service
from app.services.sms_gateway_service import sms_service_africas_talking
from app.src.config.database import get_db
from app.src.crud.savings.savings_crud import (
    _resolve_savings_tx_type_id,
    create_savings_product,
    create_savings_account,
)
from app.src.crud.savings.transaction_crud import (
    get_savings_transactions,
    get_account_balance,
)
from app.src.models.savings import SavingsProduct, SavingsAccount, SavingsTransaction
from app.src.models import Member
from app.src.schemas.savings import (
    SavingsProductCreate,
    SavingsProductResponse,
    SavingsAccountCreate,
    SavingsAccountResponse,
    SavingsTransactionCreate,
    SavingsTransactionResponse,
)
from app.src.schemas.transaction_schemas import (
    SavingsWithdrawalRequest,
    FundTransferRequest,
    TransactionResponse,
)
from app.src.utils.auth import get_member_id_from_token
from app.src.models import PaymentChannelConfiguration
from pydantic import BaseModel

router = APIRouter()


@router.post(
    "/products",
    response_model=SavingsProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_savings_product_endpoint(
    product: SavingsProductCreate, db: Session = Depends(get_db)
):
    try:
        return create_savings_product(db, product)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/products", response_model=list[SavingsProductResponse])
def list_savings_products(db: Session = Depends(get_db)):
    return db.query(SavingsProduct).all()


@router.get("/accounts", response_model=list[SavingsAccountResponse])
def list_savings_accounts(db: Session = Depends(get_db)):
    return db.query(SavingsAccount).all()


@router.post(
    "/deposit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def deposit_endpoint(
    tx: SavingsTransactionCreate,
    db: Session = Depends(get_db),
    member_id: str = Depends(get_member_id_from_token),
):
    try:
        result = execute_savings_deposit_with_ledger(
            db,
            tx.account_id,
            tx.amount,
            tx.reference,
            tx.processed_by_id,
            tx.payment_channel_code,
        )

        # Send notifications
        account = (
            db.query(SavingsAccount).filter(SavingsAccount.id == tx.account_id).first()
        )
        member = db.query(Member).filter(Member.id == account.member_id).first()

        if member and member.email:
            email_service.send_deposit_confirmation(
                recipient_email=member.email,
                member_name=f"{member.first_name} {member.last_name}",
                account_number=account.account_no,
                amount=tx.amount,
                balance_after=float(result.balance_after),
            )

        if member and member.phone_primary:
            sms_service_africas_talking.send_deposit_notification(
                phone_number=member.phone_primary,
                amount=tx.amount,
                account_number=account.account_no,
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.post(
    "/withdraw",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def withdraw_endpoint(
    withdrawal: SavingsWithdrawalRequest,
    db: Session = Depends(get_db),
    member_id: str = Depends(get_member_id_from_token),
):
    try:
        result = execute_savings_withdrawal_with_ledger(
            db,
            withdrawal.account_id,
            withdrawal.amount,
            withdrawal.reference,
            member_id,
            withdrawal.payment_channel_code,
        )

        # Send notifications
        account = (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == withdrawal.account_id)
            .first()
        )
        member = db.query(Member).filter(Member.id == account.member_id).first()

        if member and member.email:
            email_service.send_withdrawal_confirmation(
                recipient_email=member.email,
                member_name=f"{member.first_name} {member.last_name}",
                account_number=account.account_no,
                amount=withdrawal.amount,
                balance_after=float(result.balance_after),
            )

        if member and member.phone_primary:
            sms_service_africas_talking.send_withdrawal_notification(
                phone_number=member.phone_primary,
                amount=withdrawal.amount,
                account_number=account.account_no,
                balance=float(result.balance_after),
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Withdrawal failed: {e}",
        )


@router.post(
    "/transfer",
    status_code=status.HTTP_201_CREATED,
)
def transfer_funds_endpoint(
    transfer: FundTransferRequest,
    db: Session = Depends(get_db),
    member_id: str = Depends(get_member_id_from_token),
):
    try:
        result = execute_fund_transfer_with_ledger(
            db,
            transfer.from_account_id,
            transfer.to_account_id,
            transfer.amount,
            transfer.reference,
            member_id,
        )

        # Send notifications
        from_account = (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == transfer.from_account_id)
            .first()
        )
        to_account = (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == transfer.to_account_id)
            .first()
        )

        from_member = (
            db.query(Member).filter(Member.id == from_account.member_id).first()
        )
        to_member = db.query(Member).filter(Member.id == to_account.member_id).first()

        # Notify sender
        if from_member and from_member.email:
            email_service.send_transfer_notification(
                sender_email=from_member.email,
                sender_name=f"{from_member.first_name} {from_member.last_name}",
                recipient_name=f"{to_member.first_name} {to_member.last_name}",
                amount=transfer.amount,
                from_account=from_account.account_no,
                to_account=to_account.account_no,
            )

        if from_member and from_member.phone_primary:
            sms_service_africas_talking.send_transfer_notification(
                phone_number=from_member.phone_primary,
                amount=transfer.amount,
                recipient=f"{to_member.first_name} {to_member.last_name}",
            )

        return {
            "status": "success",
            "from_account": from_account.account_no,
            "to_account": to_account.account_no,
            "amount": transfer.amount,
            "reference": transfer.reference,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer failed: {e}",
        )


@router.get("/transactions/{account_id}")
def get_transactions_endpoint(
    account_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get transaction history for a savings account."""
    try:
        transactions = get_savings_transactions(db, account_id, skip=skip, limit=limit)
        return transactions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transactions: {e}",
        )


@router.get("/balance/{account_id}")
def get_balance_endpoint(
    account_id: str,
    db: Session = Depends(get_db),
):
    """Get current balance of a savings account."""
    try:
        balance = get_account_balance(db, account_id)
        if not balance:
            raise HTTPException(status_code=404, detail="Account not found")
        return balance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve balance: {e}",
        )


@router.get("/transactions", response_model=list[SavingsTransactionResponse])
def list_savings_transactions(db: Session = Depends(get_db)):
    return db.query(SavingsTransaction).all()


# A simple response schema so the frontend knows what to look for
class PaymentChannelResponse(BaseModel):
    channel_code: str
    channel_name: str

    class Config:
        from_attributes = True


@router.get("/payment-channels", response_model=list[PaymentChannelResponse])
def list_payment_channels(db: Session = Depends(get_db)):
    """Fetch all active payment channels to populate the frontend dropdown."""
    return db.query(PaymentChannelConfiguration).all()
