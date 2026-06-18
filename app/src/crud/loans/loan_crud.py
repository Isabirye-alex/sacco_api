"""Module for app.src.crud.loans.loan_crud."""

from datetime import date

from sqlalchemy.orm import Session
from app.src.utils.generate_unique_application_no import generate_unique_application_number
from app.src.models.loans import (
    LoanProduct,
    LoanApplication,
    Loan,
    LoanGuarantor,
    LoanCollateral,
    LoanRepaymentSchedule,
    LoanRepayment,
    LoanPenalty,
)
from app.src.schemas.loans.loan_schema import (
    LoanProductCreate,
    LoanApplicationCreate,
    LoanCreate,
    LoanGuarantorCreate,
    LoanCollateralCreate,
    LoanRepaymentScheduleCreate,
    LoanRepaymentCreate,
    LoanPenaltyCreate,
)


def create_loan_product(db: Session, product: LoanProductCreate):
    db_product = LoanProduct(
        name=product.name,
        code=product.code,
        description=product.description,
        interest_rate_pa=product.interest_rate_pa,
        interest_method=product.interest_method,
        repayment_frequency=product.repayment_frequency,
        min_term_months=product.min_term_months,
        max_term_months=product.max_term_months,
        min_amount=product.min_amount,
        max_amount=product.max_amount,
        loan_to_savings_ratio=product.loan_to_savings_ratio,
        loan_to_shares_ratio=product.loan_to_shares_ratio,
        requires_guarantor=product.requires_guarantor,
        min_guarantors=product.min_guarantors,
        requires_collateral=product.requires_collateral,
        penalty_rate_per_day=product.penalty_rate_per_day,
        processing_fee_pct=product.processing_fee_pct,
        is_active=product.is_active,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def create_loan_application(db: Session, application: LoanApplicationCreate, member_id: str):
    application_no = generate_unique_application_number()
    db_application = LoanApplication(
        branch_id=application.branch_id,
        member_id=application.member_id,
        product_id=application.product_id,
        application_no=application_no,
        applied_amount=application.applied_amount,
        approved_amount=application.approved_amount,
        term_months=application.term_months,
        purpose=application.purpose,
        status=application.status,
        applied_date=application.applied_date or date.today(),
        reviewed_date=application.reviewed_date,
        decision_date=application.decision_date,
        reviewed_by_id=application.reviewed_by_id,
        decision_by_id=application.decision_by_id,
        rejection_reason=application.rejection_reason,
        notes=application.notes,
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def create_loan(db: Session, loan: LoanCreate):
    db_loan = Loan(
        branch_id=loan.branch_id,
        member_id=loan.member_id,
        product_id=loan.product_id,
        application_id=loan.application_id,
        loan_no=loan.loan_no,
        principal=loan.principal,
        interest_rate_pa=loan.interest_rate_pa,
        term_months=loan.term_months,
        interest_method=loan.interest_method,
        repayment_frequency=loan.repayment_frequency,
        processing_fee=loan.processing_fee,
        total_interest=loan.total_interest,
        total_payable=loan.total_payable,
        outstanding_principal=loan.outstanding_principal,
        outstanding_interest=loan.outstanding_interest,
        outstanding_penalty=loan.outstanding_penalty,
        total_paid=loan.total_paid,
        disbursement_date=loan.disbursement_date,
        first_payment_date=loan.first_payment_date,
        maturity_date=loan.maturity_date,
        closed_date=loan.closed_date,
        status=loan.status,
        disbursed_by_id=loan.disbursed_by_id,
        ledger_entry_id=loan.ledger_entry_id,
        notes=loan.notes,
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


def create_loan_guarantor(db: Session, guarantor: LoanGuarantorCreate):
    db_guarantor = LoanGuarantor(
        application_id=guarantor.application_id,
        guarantor_id=guarantor.guarantor_id,
        guaranteed_amount=guarantor.guaranteed_amount,
        has_consented=guarantor.has_consented,
        consent_date=guarantor.consent_date,
        notes=guarantor.notes,
    )
    db.add(db_guarantor)
    db.commit()
    db.refresh(db_guarantor)
    return db_guarantor


def create_loan_collateral(db: Session, collateral: LoanCollateralCreate):
    db_collateral = LoanCollateral(
        application_id=collateral.application_id,
        collateral_type=collateral.collateral_type,
        description=collateral.description,
        estimated_value=collateral.estimated_value,
        document_ref=collateral.document_ref,
        notes=collateral.notes,
    )
    db.add(db_collateral)
    db.commit()
    db.refresh(db_collateral)
    return db_collateral


def create_loan_repayment_schedule(db: Session, schedule: LoanRepaymentScheduleCreate):
    db_schedule = LoanRepaymentSchedule(
        loan_id=schedule.loan_id,
        instalment_no=schedule.instalment_no,
        due_date=schedule.due_date,
        principal_due=schedule.principal_due,
        interest_due=schedule.interest_due,
        total_due=schedule.total_due,
        principal_paid=schedule.principal_paid,
        interest_paid=schedule.interest_paid,
        penalty_paid=schedule.penalty_paid,
        is_paid=schedule.is_paid,
        paid_date=schedule.paid_date,
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def create_loan_repayment(db: Session, repayment: LoanRepaymentCreate):
    db_repayment = LoanRepayment(
        loan_id=repayment.loan_id,
        ledger_entry_id=repayment.ledger_entry_id,
        amount=repayment.amount,
        principal_portion=repayment.principal_portion,
        interest_portion=repayment.interest_portion,
        penalty_portion=repayment.penalty_portion,
        payment_date=repayment.payment_date,
        payment_method=repayment.payment_method,
        reference=repayment.reference,
        notes=repayment.notes,
        received_by_id=repayment.received_by_id,
    )
    db.add(db_repayment)
    db.commit()
    db.refresh(db_repayment)
    return db_repayment


def create_loan_penalty(db: Session, penalty: LoanPenaltyCreate):
    db_penalty = LoanPenalty(
        loan_id=penalty.loan_id,
        penalty_type=penalty.penalty_type,
        days_overdue=penalty.days_overdue,
        amount=penalty.amount,
        amount_paid=penalty.amount_paid,
        is_waived=penalty.is_waived,
        waived_by_id=penalty.waived_by_id,
        raised_date=penalty.raised_date,
        notes=penalty.notes,
    )
    db.add(db_penalty)
    db.commit()
    db.refresh(db_penalty)
    return db_penalty
