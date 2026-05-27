from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import requests
import json
import logging
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
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
logger.propagate = True


class MobileMoneyProcessor:
    """Handle mobile money transactions using MarzPay only."""

    def __init__(self):
        self.provider = settings.MOBILE_MONEY_PROVIDER
        self.auth_header = (
            settings.MARZPAY_AUTH_HEADER.strip()
            if settings.MARZPAY_AUTH_HEADER
            else None
        )

    def initiate_payment(
        self,
        phone_number: str,
        amount: float,
        reference: str,
        transaction_type: str,
    ) -> dict:
        """
        Initiate a MarzPay payment request.
        """
        try:
            if self.provider.lower() != "marzpay":
                raise ValueError(f"Unsupported provider: {self.provider}")
            return self._marzpay_payment(phone_number, amount, reference)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _marzpay_payment(
        self, phone_number: str, amount: float, reference: str
    ) -> dict:
        """Handle MarzPay payment."""
        try:
            url = (
                settings.MARZPAY_API_URL
                or "https://wallet.wearemarz.com/api/v1/collect-money"
            )
            callback_url = settings.MARZPAY_CALLBACK_URL or (
                f"{settings.API_BASE_URL}/mobile-money/callback"
                if settings.API_BASE_URL
                else None
            )

            if not self.auth_header:
                raise ValueError("MarzPay auth header is not configured.")

            auth_header_value = (
                self.auth_header
                if self.auth_header.lower().startswith("basic ")
                else f"Basic {self.auth_header}"
            )
            headers = {
                "Authorization": auth_header_value,
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # Debug logging
            logger.info(f"MarzPay Request URL: {url}")
            logger.info(
                f"MarzPay Auth Header: {headers.get('Authorization', 'NOT SET')[:40]}"
            )
            print("MarzPay Debug: Request URL=", url)
            print(
                "MarzPay Debug: Auth Header=",
                headers.get("Authorization", "NOT SET")[:40],
            )

            payload = {
                "phone_number": phone_number,
                "amount": (
                    str(int(amount)) if float(amount).is_integer() else str(amount)
                ),
                "country": settings.MARZPAY_COUNTRY,
                "reference": reference,
                "description": f"SACCO payment: {reference}",
            }

            logger.info(f"MarzPay Request Payload: {payload}")
            print("MarzPay Debug: Request Payload=", payload)

            if callback_url:
                payload["callback_url"] = callback_url

            response = requests.post(url, data=payload, headers=headers, timeout=30)
            data = response.json()

            logger.info(f"MarzPay Response Status: {response.status_code}")
            logger.info(f"MarzPay Response: {data}")

            if response.status_code in (200, 201) and data.get("status") == "success":
                transaction_id = (
                    data.get("data", {}).get("transaction", {}).get("uuid")
                    or data.get("data", {}).get("transaction", {}).get("reference")
                    or data.get("data", {})
                    .get("transaction", {})
                    .get("provider_reference")
                )
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "provider_response": data,
                }

            return {
                "success": False,
                "error": data.get("message") or response.text,
                "provider_response": data,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


@router.post(
    "/payments",
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
        print("started")
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
            provider_response=json.dumps(
                payment_result.get("provider_response", payment_result), default=str
            ),
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
            # (In production, use callback from MarzPay)
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
    Called by MarzPay when payment is confirmed.
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
