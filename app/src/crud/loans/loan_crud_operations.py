"""Module for app.src.crud.loans.loan_crud_operations."""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from app.src.models import LoanApplication, Loan, LoanRepayment


def get_loan_applications(
    db: Session,
    member_id: UUID = None,
    status: str = None,
    skip: int = 0,
    limit: int = 50,
):
    """Get loan applications with optional filtering."""
    query = db.query(LoanApplication)

    if member_id:
        query = query.filter(LoanApplication.member_id == member_id)

    if status:
        query = query.filter(LoanApplication.status == status)

    return (
        query.order_by(LoanApplication.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_loan_application_by_id(db: Session, application_id: UUID):
    """Get a specific loan application."""
    return (
        db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    )


def get_member_loans(
    db: Session,
    member_id: UUID,
    status: str = None,
    skip: int = 0,
    limit: int = 50,
):
    """Get all loans for a member."""
    query = db.query(Loan).filter(Loan.member_id == member_id)

    if status:
        query = query.filter(Loan.status == status)

    return query.order_by(Loan.created_at.desc()).offset(skip).limit(limit).all()


def get_loan_by_id(db: Session, loan_id: UUID):
    """Get a specific loan."""
    return db.query(Loan).filter(Loan.id == loan_id).first()


def get_loan_repayment_history(
    db: Session,
    loan_id: UUID,
    skip: int = 0,
    limit: int = 50,
):
    """Get repayment history for a loan."""
    return (
        db.query(LoanRepayment)
        .filter(LoanRepayment.loan_id == loan_id)
        .order_by(LoanRepayment.payment_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_pending_loan_applications(
    db: Session,
    branch_id: UUID = None,
    skip: int = 0,
    limit: int = 50,
):
    """Get all pending loan applications."""
    query = db.query(LoanApplication).filter(LoanApplication.status == "PENDING")

    if branch_id:
        query = query.filter(LoanApplication.branch_id == branch_id)

    return (
        query.order_by(LoanApplication.created_at.asc()).offset(skip).limit(limit).all()
    )
