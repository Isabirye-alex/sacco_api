from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import requests
from datetime import date

from app.src.config.database import get_db
from app.src.config.settings import settings
from app.src.models import MobileMoneyTransaction
from app.src.schemas.transaction_schemas import (
    MobileMoneyPaymentRequest,
    MobileMoneyPaymentResponse,
)
from app.src.utils.auth import get_member_id_from_token
from app.services.transaction_ledger_service import (
    execute_savings_deposit_with_ledger,
    execute_savings_withdrawal_with_ledger,
)
from app.services.loan_ledger_service import process_loan_repayment_with_ledger

router = APIRouter()


class MobileMoneyProcessor:
    """Handle mobile money transactions."""

    def __init__(self):
        self.provider = settings.MOBILE_MONEY_PROVIDER
        self.api_key = settings.MOBILE_MONEY_API_KEY
        self.api_secret = settings.MOBILE_MONEY_API_SECRET

    def initiate_payment(
        self,
        phone_number: str,
        amount: float,
        reference: str,
        transaction_type: str,
    ) -> dict:
        """
        Initiate a mobile money payment request.
        Supports M-Pesa, Airtel Money, etc.
        """
        try:
            if self.provider.lower() == "mpesa":
                return self._mpesa_payment(phone_number, amount, reference)
            elif self.provider.lower() == "airtel_money":
                return self._airtel_payment(phone_number, amount, reference)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _mpesa_payment(self, phone_number: str, amount: float, reference: str) -> dict:
        """Handle M-Pesa payment."""
        try:
            url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

            headers = {
                "Authorization": f"Bearer {self._get_mpesa_token()}",
                "Content-Type": "application/json",
            }

            payload = {
                "BusinessShortCode": settings.MPESA_BUSINESS_CODE,
                "Password": settings.MPESA_PASSWORD,
                "Timestamp": date.today().strftime("%Y%m%d%H%M%S"),
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": settings.MPESA_BUSINESS_CODE,
                "PhoneNumber": phone_number,
                "CallBackURL": f"{settings.API_BASE_URL}/mobile-money/callback",
                "AccountReference": reference,
                "TransactionDesc": "SACCO Payment",
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get("ResponseCode") == "0":
                    return {
                        "success": True,
                        "transaction_id": data.get("CheckoutRequestID"),
                        "request_id": data.get("MerchantRequestID"),
                    }

            return {"success": False, "error": response.text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _airtel_payment(self, phone_number: str, amount: float, reference: str) -> dict:
        """Handle Airtel Money payment."""
        try:
            url = "https://api.airtel.in/payments/v1/charge"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "reference": reference,
                "subscriber": {
                    "phone": phone_number,
                },
                "transaction": {
                    "amount": amount,
                    "currency": "KES",
                },
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "transaction_id": data.get("data", {}).get("transaction_id"),
                }

            return {"success": False, "error": response.text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_mpesa_token(self) -> str:
        """Get M-Pesa access token."""
        try:
            url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
            auth = (settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
            response = requests.get(url, auth=auth, timeout=10)
            if response.status_code == 200:
                return response.json().get("access_token")
        except Exception as e:
            print(f"Failed to get M-Pesa token: {e}")
        return None


@router.post(
    "/pay",
    response_model=MobileMoneyPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def process_mobile_money_payment_endpoint(
    payment: MobileMoneyPaymentRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_member_id_from_token),
):
    """
    Process a mobile money payment.
    Supports deposit, withdrawal, and loan payment transactions.
    """
    try:
        processor = MobileMoneyProcessor()

        # Initiate mobile money payment
        payment_result = processor.initiate_payment(
            phone_number=payment.phone_number,
            amount=payment.amount,
            reference=payment.reference,
            transaction_type=payment.transaction_type,
        )

        if not payment_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Mobile money payment failed: {payment_result.get('error')}",
            )

        # Create transaction record
        transaction = MobileMoneyTransaction(
            phone_number=payment.phone_number,
            amount=payment.amount,
            transaction_type=payment.transaction_type,
            status="PENDING",
            reference=payment.reference,
            transaction_id=payment_result.get("transaction_id"),
            created_by_id=user_id,
        )
        db.add(transaction)
        db.flush()

        # Process based on transaction type
        if payment.transaction_type == "DEPOSIT":
            if not payment.account_id:
                raise HTTPException(
                    status_code=400,
                    detail="account_id required for deposit transactions",
                )

            # Execute deposit once payment is confirmed
            # (In production, use callback from M-Pesa/Airtel)
            execute_savings_deposit_with_ledger(
                db,
                payment.account_id,
                payment.amount,
                payment.reference,
                user_id,
                "MOBILE_MONEY",
            )
            transaction.status = "SUCCESS"

        elif payment.transaction_type == "WITHDRAWAL":
            if not payment.account_id:
                raise HTTPException(
                    status_code=400,
                    detail="account_id required for withdrawal transactions",
                )

            execute_savings_withdrawal_with_ledger(
                db,
                payment.account_id,
                payment.amount,
                payment.reference,
                user_id,
                "MOBILE_MONEY",
            )
            transaction.status = "SUCCESS"

        elif payment.transaction_type == "LOAN_PAYMENT":
            if not payment.loan_id:
                raise HTTPException(
                    status_code=400,
                    detail="loan_id required for loan payment transactions",
                )

            process_loan_repayment_with_ledger(
                db,
                payment.loan_id,
                payment.amount,
                payment.reference,
                user_id,
                "MOBILE_MONEY",
            )
            transaction.status = "SUCCESS"

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported transaction type: {payment.transaction_type}",
            )

        db.add(transaction)
        db.commit()

        return transaction

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process mobile money payment: {e}",
        )


@router.post("/callback")
def mobile_money_callback(
    db: Session = Depends(get_db),
):
    """
    Webhook endpoint for mobile money provider callbacks.
    Called by M-Pesa, Airtel Money, etc., when payment is confirmed.
    """
    try:
        # Extract callback data from request
        # Process and update transaction status
        # This is provider-specific

        return {"status": "received"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process callback: {e}",
        )


@router.get("/transaction/{transaction_id}")
def get_mobile_money_transaction_endpoint(
    transaction_id: UUID,
    db: Session = Depends(get_db),
):
    """Get details of a mobile money transaction."""
    try:
        transaction = (
            db.query(MobileMoneyTransaction)
            .filter(MobileMoneyTransaction.id == transaction_id)
            .first()
        )
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transaction: {e}",
        )
