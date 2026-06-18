"""Module for app.src.api.endpoints.shares_extended."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.services.shares_ledger_service import (
    purchase_shares_with_ledger,
    calculate_and_distribute_dividends,
    declare_dividend,
)
from app.services.email_notification_service import email_service
from app.services.sms_gateway_service import sms_service_africas_talking
from app.src.config.database import get_db
from app.src.crud.shares.share_crud_operations import (
    get_member_share_accounts,
    get_share_account_by_id,
    get_share_transactions,
    get_product_dividends,
    get_dividend_by_id,
    get_member_shareholdings,
)
from app.src.models import Member, ShareProduct
from app.src.schemas.transaction_schemas import (
    SharePurchaseRequest,
    SharePurchaseResponse,
    DividendDeclarationRequest,
    DividendResponse,
    ShareAccountResponse,
)
from app.src.utils.auth import get_member_id_from_token

router = APIRouter()


@router.post(
    "/purchase",
    status_code=status.HTTP_201_CREATED,
)
def purchase_shares_endpoint(
    purchase: SharePurchaseRequest,
    db: Session = Depends(get_db),
    member_id: UUID = Depends(get_member_id_from_token),
):
    """Purchase shares of a product."""
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        result = purchase_shares_with_ledger(
            db,
            member_id,
            purchase.product_id,
            purchase.num_shares,
            purchase.price_per_share,
            purchase.reference,
            member_id,
            purchase.payment_channel_code,
            member.branch_id,
        )

        product = (
            db.query(ShareProduct)
            .filter(ShareProduct.id == purchase.product_id)
            .first()
        )

        # Send notifications
        total_amount = purchase.num_shares * purchase.price_per_share

        if member.email:
            email_service.send_email(
                recipient_email=member.email,
                subject="Share Purchase Confirmation - SACCO",
                body=f"""
                <html>
                    <body>
                        <h2>Share Purchase Confirmation</h2>
                        <p>Dear {member.first_name},</p>
                        <p>Your share purchase has been successfully processed:</p>
                        <ul>
                            <li><strong>Product:</strong> {product.name}</li>
                            <li><strong>Shares Purchased:</strong> {purchase.num_shares}</li>
                            <li><strong>Price per Share:</strong> {purchase.price_per_share:,.2f}</li>
                            <li><strong>Total Amount:</strong> {total_amount:,.2f}</li>
                        </ul>
                        <p>Thank you for investing in SACCO.</p>
                        <p>Best Regards,<br/>SACCO Management</p>
                    </body>
                </html>
                """,
                is_html=True,
            )

        if member.phone_primary:
            sms_service_africas_talking.send_sms(
                phone_number=member.phone_primary,
                message=f"You have purchased {purchase.num_shares} shares of {product.code} for {total_amount:,.2f}. Thank you!",
            )

        return {
            "status": "success",
            "account": result["account"],
            "transaction": result["transaction"],
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purchase shares: {e}",
        )


@router.get("/accounts/{member_id}", response_model=list[ShareAccountResponse])
def get_member_share_accounts_endpoint(
    member_id: UUID,
    db: Session = Depends(get_db),
):
    """Get all share accounts for a member."""
    try:
        accounts = get_member_share_accounts(db, member_id)
        return accounts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve share accounts: {e}",
        )


@router.get("/holdings/{member_id}")
def get_member_shareholdings_endpoint(
    member_id: UUID,
    db: Session = Depends(get_db),
):
    """Get summary of all share holdings for a member."""
    try:
        holdings = get_member_shareholdings(db, member_id)
        return {
            "member_id": member_id,
            "holdings": holdings,
            "total_value": sum(h["total_value"] for h in holdings),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve shareholdings: {e}",
        )


@router.get("/transactions/{account_id}")
def get_share_transactions_endpoint(
    account_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get transaction history for a share account."""
    try:
        transactions = get_share_transactions(db, account_id, skip=skip, limit=limit)
        return transactions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transactions: {e}",
        )


@router.post(
    "/dividends/declare",
    response_model=DividendResponse,
    status_code=status.HTTP_201_CREATED,
)
def declare_dividend_endpoint(
    declaration: DividendDeclarationRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_member_id_from_token),
):
    """Declare a new dividend for a share product (admin only)."""
    try:
        dividend = declare_dividend(
            db,
            declaration.product_id,
            declaration.period_label,
            declaration.period_start,
            declaration.period_end,
            declaration.rate_percent,
            user_id,
        )
        return dividend
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to declare dividend: {e}",
        )


@router.post(
    "/dividends/{dividend_id}/distribute",
    response_model=DividendResponse,
    status_code=status.HTTP_200_OK,
)
def distribute_dividends_endpoint(
    dividend_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_member_id_from_token),
):
    """Calculate and distribute dividends to shareholders (admin only)."""
    try:
        result = calculate_and_distribute_dividends(
            db,
            dividend_id,
            user_id,
        )

        dividend = result["dividend"]
        payments = result["payments"]

        # Send notifications to all recipients
        from app.src.models import ShareAccount

        for payment in payments:
            account = (
                db.query(ShareAccount)
                .filter(ShareAccount.id == payment.share_account_id)
                .first()
            )
            member = db.query(Member).filter(Member.id == account.member_id).first()

            if member and member.email:
                email_service.send_dividend_notification(
                    recipient_email=member.email,
                    member_name=f"{member.first_name} {member.last_name}",
                    dividend_amount=float(payment.amount),
                    product_name=dividend.product.name,
                )

            if member and member.phone_primary:
                sms_service_africas_talking.send_dividend_notification(
                    phone_number=member.phone_primary,
                    dividend_amount=float(payment.amount),
                )

        return dividend

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to distribute dividends: {e}",
        )


@router.get("/dividends/product/{product_id}")
def get_product_dividends_endpoint(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    """Get all dividends declared for a product."""
    try:
        dividends = get_product_dividends(db, product_id)
        return dividends
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dividends: {e}",
        )


@router.get("/dividends/{dividend_id}", response_model=DividendResponse)
def get_dividend_endpoint(
    dividend_id: UUID,
    db: Session = Depends(get_db),
):
    """Get details of a specific dividend."""
    try:
        dividend = get_dividend_by_id(db, dividend_id)
        if not dividend:
            raise HTTPException(status_code=404, detail="Dividend not found")
        return dividend
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dividend: {e}",
        )
