"""Module for app.src.api.endpoints.loans_extended."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from app.services.loan_ledger_service import (
    approve_loan_application_with_ledger,
    process_loan_repayment_with_ledger,
    apply_late_payment_penalty,
)
from app.services.email_notification_service import email_service
from app.services.sms_gateway_service import sms_service_africas_talking
from app.src.config.database import get_db
from app.src.crud.loans.loan_crud_operations import (
    get_loan_applications,
    get_loan_application_by_id,
    get_member_loans,
    get_loan_by_id,
    get_loan_repayment_history,
    get_pending_loan_applications,
)
from app.src.models import LoanApplication, Loan, Member
from app.src.schemas.transaction_schemas import (
    LoanApplicationRequest,
    LoanApprovalRequest,
    LoanRepaymentRequest,
    LoanRepaymentResponse,
    LoanApplicationResponse,
    LoanResponse,
)
from app.src.utils.auth import get_member_id_from_token

router = APIRouter()


@router.post(
    "/applications",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_application_endpoint(
    application: LoanApplicationRequest,
    db: Session = Depends(get_db),
    member_id: UUID = Depends(get_member_id_from_token),
):
    """Create a new loan application."""
    try:
        from app.src.models import LoanProduct, Branch

        product = (
            db.query(LoanProduct)
            .filter(LoanProduct.id == application.product_id)
            .first()
        )
        if not product:
            raise HTTPException(status_code=404, detail="Loan product not found")

        member = db.query(Member).filter(Member.id == member_id).first()
        branch = db.query(Branch).filter(Branch.id == member.branch_id).first()

        # Validate loan amount
        if application.requested_amount < float(product.min_amount) or (
            product.max_amount
            and application.requested_amount > float(product.max_amount)
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Loan amount must be between {product.min_amount} and {product.max_amount or 'unlimited'}",
            )

        # Validate term
        if (
            application.proposed_term_months < product.min_term_months
            or application.proposed_term_months > product.max_term_months
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Loan term must be between {product.min_term_months} and {product.max_term_months} months",
            )

        loan_app = LoanApplication(
            branch_id=branch.id,
            member_id=member_id,
            product_id=application.product_id,
            applied_amount=application.requested_amount,
            term_months=application.proposed_term_months,
            purpose=application.purpose,
            status="PENDING",
            applied_date=date.today(),
            created_by_id=member_id,
        )
        db.add(loan_app)
        db.commit()

        return loan_app

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create loan application: {e}",
        )

@router.get("/applications/pending")
def get_pending_applications_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get all pending loan applications (admin only)."""
    try:
        applications = get_pending_loan_applications(db, skip=skip, limit=limit)
        return applications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pending applications: {e}",
        )


@router.get("/applications/{application_id}")
def get_loan_application_endpoint(
    application_id: UUID,
    db: Session = Depends(get_db),
):
    """Get details of a specific loan application."""
    try:
        application = get_loan_application_by_id(db, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        return application
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve application: {e}",
        )


@router.post(
    "/applications/{application_id}/approve",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
)
def approve_loan_application_endpoint(
    application_id: UUID,
    approval: LoanApprovalRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_member_id_from_token),
):
    """Approve a loan application (admin only)."""
    try:
        application = get_loan_application_by_id(db, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        result = approve_loan_application_with_ledger(
            db,
            application_id,
            approval.approved_amount,
            user_id,
            application.branch_id,
        )

        loan = result["loan"]
        member = db.query(Member).filter(Member.id == application.member_id).first()

        # Send notifications
        if member and member.email:
            email_service.send_loan_approval_notification(
                recipient_email=member.email,
                member_name=f"{member.first_name} {member.last_name}",
                loan_amount=approval.approved_amount,
                interest_rate=float(application.product.interest_rate_pa),
                maturity_date=str(loan.maturity_date),
            )

        if member and member.phone_primary:
            sms_service_africas_talking.send_loan_approval_notification(
                phone_number=member.phone_primary,
                loan_amount=approval.approved_amount,
                loan_term=application.proposed_term_months,
            )

        return loan

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve loan: {e}",
        )


@router.get("/member/{member_id}")
def get_member_loans_endpoint(
    member_id: UUID,
    status: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get all loans for a specific member."""
    try:
        loans = get_member_loans(db, member_id, status=status, skip=skip, limit=limit)
        return loans
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve loans: {e}",
        )


@router.get("/{loan_id}")
def get_loan_endpoint(
    loan_id: UUID,
    db: Session = Depends(get_db),
):
    """Get details of a specific loan."""
    try:
        loan = get_loan_by_id(db, loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        return loan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve loan: {e}",
        )


@router.post(
    "/{loan_id}/repay",
    response_model=LoanRepaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def process_loan_repayment_endpoint(
    loan_id: UUID,
    repayment: LoanRepaymentRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_member_id_from_token),
):
    """Process a loan repayment."""
    try:
        if repayment.loan_id != loan_id:
            raise HTTPException(status_code=400, detail="Loan ID mismatch")

        repayment_record = process_loan_repayment_with_ledger(
            db,
            loan_id,
            repayment.amount,
            repayment.reference,
            user_id,
            repayment.payment_channel_code,
        )

        loan = get_loan_by_id(db, loan_id)
        member = db.query(Member).filter(Member.id == loan.member_id).first()

        # Send notification
        if member and member.email:
            from app.services.email_notification_service import email_service

            email_service.send_email(
                recipient_email=member.email,
                subject="Loan Payment Received - SACCO",
                body=f"""
                <html>
                    <body>
                        <h2>Loan Payment Confirmation</h2>
                        <p>Dear {member.first_name},</p>
                        <p>Your loan payment has been received:</p>
                        <ul>
                            <li><strong>Amount Paid:</strong> {repayment.amount:,.2f}</li>
                            <li><strong>Principal:</strong> {repayment_record.principal_amount:,.2f}</li>
                            <li><strong>Interest:</strong> {repayment_record.interest_amount:,.2f}</li>
                            <li><strong>Outstanding Balance:</strong> {loan.outstanding_balance:,.2f}</li>
                        </ul>
                        <p>Best Regards,<br/>SACCO Management</p>
                    </body>
                </html>
                """,
                is_html=True,
            )

        return repayment_record

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process repayment: {e}",
        )


@router.get("/{loan_id}/repayment-history")
def get_loan_repayment_history_endpoint(
    loan_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get repayment history for a loan."""
    try:
        history = get_loan_repayment_history(db, loan_id, skip=skip, limit=limit)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve repayment history: {e}",
        )
