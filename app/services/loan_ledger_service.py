from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.src.models import (
    Loan,
    LoanApplication,
    LoanRepayment,
    LoanPenalty,
    SavingsAccount,
    LedgerEntry,
    LedgerLine,
    User,
)
from app.src.models.ledger import DR_CR_CREDIT, DR_CR_DEBIT
from app.src.models.loans import LoanStatus, LoanApplicationStatus


def calculate_loan_repayment_schedule(
    loan_amount: float,
    annual_rate: float,
    monthly_payment: float,
    start_date: date,
    frequency_code: str,
):
    """Calculate amortization schedule for a loan."""
    schedule = []
    balance = loan_amount
    current_date = start_date
    interest_rate = annual_rate / 100 / 12  # monthly rate

    period_num = 1
    while balance > 0.01:  # tolerance for floating point
        interest_charge = balance * interest_rate
        principal_payment = monthly_payment - interest_charge

        if principal_payment >= balance:
            principal_payment = balance
            interest_charge = balance * interest_rate
            payment_amount = principal_payment + interest_charge
        else:
            payment_amount = monthly_payment

        balance -= principal_payment

        schedule.append(
            {
                "period": period_num,
                "due_date": current_date,
                "opening_balance": balance + principal_payment,
                "payment_amount": payment_amount,
                "principal": principal_payment,
                "interest": interest_charge,
                "closing_balance": max(0, balance),
            }
        )

        current_date += timedelta(days=30)  # approximate monthly
        period_num += 1

    return schedule


def approve_loan_application_with_ledger(
    db: Session,
    application_id: UUID,
    approved_amount: float,
    user_id: UUID,
    branch_id: UUID,
):
    """
    Admin approves a loan application and creates the Loan record.
    This also creates ledger entries if disbursement is immediate.
    """
    try:
        # Resolve User ID
        user = (
            db.query(User)
            .filter((User.id == user_id) | (User.member_id == user_id))
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        actual_user_id = user.id

        # 1. FETCH & LOCK THE APPLICATION
        application = (
            db.query(LoanApplication)
            .filter(LoanApplication.id == application_id)
            .with_for_update(of=LoanApplication)
            .first()
        )
        if not application:
            raise HTTPException(status_code=404, detail="Loan application not found")

        # 2. CHECK APPLICATION STATUS
        if application.status != "PENDING":
            raise HTTPException(
                status_code=400,
                detail=f"Application status is {application.status}, cannot approve",
            )

        # 3. VALIDATE AMOUNT
        if approved_amount > float(application.requested_amount):
            raise HTTPException(
                status_code=400,
                detail="Approved amount cannot exceed requested amount",
            )

        # 4. UPDATE APPLICATION STATUS
        application.status = "APPROVED"
        application.approved_amount = Decimal(str(approved_amount))
        application.approved_date = datetime.now()
        application.approved_by_id = actual_user_id
        db.add(application)
        db.flush()

        # 5. CREATE LOAN RECORD
        from app.src.models import LoanRepaymentSchedule

        loan = Loan(
            branch_id=branch_id,
            member_id=application.member_id,
            product_id=application.product_id,
            application_id=application_id,
            status="ACTIVE",
            principal_amount=approved_amount,
            outstanding_balance=approved_amount,
            interest_rate=application.product.interest_rate_pa,
            interest_method=application.product.interest_method,
            repayment_frequency=application.product.repayment_frequency,
            term_months=application.proposed_term_months,
            disbursal_date=date.today(),
            maturity_date=date.today()
            + timedelta(days=application.proposed_term_months * 30),
            approved_by_id=actual_user_id,
            created_by_id=actual_user_id,
        )
        db.add(loan)
        db.flush()

        # 6. GENERATE REPAYMENT SCHEDULE
        monthly_rate = float(application.product.interest_rate_pa) / 100 / 12
        num_periods = application.proposed_term_months
        monthly_payment = (
            approved_amount
            * (monthly_rate * (1 + monthly_rate) ** num_periods)
            / ((1 + monthly_rate) ** num_periods - 1)
        )

        schedule_dates = []
        current = date.today()
        for i in range(1, num_periods + 1):
            current += timedelta(days=30)
            schedule_dates.append(current)

        # Store schedule in JSON or as separate records (depending on your schema)
        loan.repayment_schedule = schedule_dates
        db.add(loan)
        db.commit()

        return {"loan": loan, "application": application}

    except Exception as e:
        db.rollback()
        raise e


def process_loan_repayment_with_ledger(
    db: Session,
    loan_id: UUID,
    amount: float,
    reference: str,
    user_id: UUID,
    payment_channel_code: str,
):
    """
    Process loan repayment with ledger posting.
    Allocates payment to interest first, then principal.
    """
    try:
        from app.src.models import PaymentChannelConfiguration

        # Resolve User ID
        user = (
            db.query(User)
            .filter((User.id == user_id) | (User.member_id == user_id))
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        actual_user_id = user.id

        # 1. LOCK & FETCH LOAN
        loan = (
            db.query(Loan).filter(Loan.id == loan_id).with_for_update(of=Loan).first()
        )
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")

        if loan.status != "ACTIVE":
            raise HTTPException(
                status_code=400,
                detail=f"Loan status is {loan.status}, cannot receive payment",
            )

        # 2. CALCULATE INTEREST DUE
        days_outstanding = (date.today() - loan.disbursal_date).days
        annual_rate = float(loan.interest_rate) / 100
        interest_accrued = (
            float(loan.outstanding_balance) * annual_rate * (days_outstanding / 365)
        )

        # 3. ALLOCATE PAYMENT
        interest_payment = min(amount, interest_accrued)
        principal_payment = amount - interest_payment

        # 4. GET PAYMENT CHANNEL & PRODUCT INFO
        channel_config = (
            db.query(PaymentChannelConfiguration)
            .filter(PaymentChannelConfiguration.channel_code == payment_channel_code)
            .first()
        )
        if not channel_config:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported payment channel: {payment_channel_code}",
            )

        product = loan.product

        # 5. CREATE LEDGER ENTRY
        ledger_entry = LedgerEntry(
            branch_id=loan.branch_id,
            entry_no=f"JV-{reference}-{date.today().strftime('%Y%m%d')}",
            entry_type="LOAN_REPAYMENT",
            entry_date=date.today(),
            description=f"Loan Repayment - Loan {loan.id}",
            reference=reference,
            total_debit=amount,
            total_credit=amount,
            status="POSTED",
            created_by_id=actual_user_id,
        )
        db.add(ledger_entry)
        db.flush()

        # 6. CREATE LEDGER LINES
        # Line A: DEBIT Cash/Asset (increases asset)
        cash_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=channel_config.asset_account_id,
            dr_cr=DR_CR_DEBIT,
            amount=amount,
            description=f"Loan payment via {payment_channel_code}",
            member_id=loan.member_id,
        )

        # Line B: CREDIT Loan Receivable (decreases asset) - partial principal
        if principal_payment > 0:
            principal_line = LedgerLine(
                entry_id=ledger_entry.id,
                account_id=product.loan_receivable_account_id,
                dr_cr=DR_CR_CREDIT,
                amount=principal_payment,
                description=f"Principal repayment on loan {loan.id}",
                member_id=loan.member_id,
            )
            db.add(principal_line)

        # Line C: CREDIT Interest Income (increases income) - if any interest
        if interest_payment > 0:
            interest_line = LedgerLine(
                entry_id=ledger_entry.id,
                account_id=product.interest_income_account_id,
                dr_cr=DR_CR_CREDIT,
                amount=interest_payment,
                description=f"Interest earned on loan {loan.id}",
                member_id=loan.member_id,
            )
            db.add(interest_line)

        db.add(cash_line)

        # 7. RECORD REPAYMENT
        repayment = LoanRepayment(
            loan_id=loan_id,
            amount=amount,
            principal_amount=principal_payment,
            interest_amount=interest_payment,
            payment_date=date.today(),
            reference=reference,
            payment_channel_code=payment_channel_code,
            processed_by_id=actual_user_id,
            ledger_entry_id=ledger_entry.id,
        )
        db.add(repayment)

        # 8. UPDATE LOAN BALANCE
        loan.outstanding_balance = float(loan.outstanding_balance) - principal_payment
        if loan.outstanding_balance <= 0:
            loan.status = "COMPLETED"
            loan.completion_date = date.today()

        db.add(loan)
        db.commit()

        return repayment

    except Exception as e:
        db.rollback()
        raise e


def apply_late_payment_penalty(
    db: Session,
    loan_id: UUID,
    reference: str,
    user_id: UUID,
):
    """Apply penalty for late loan payment."""
    try:
        # Resolve User ID
        user = (
            db.query(User)
            .filter((User.id == user_id) | (User.member_id == user_id))
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        actual_user_id = user.id

        loan = (
            db.query(Loan).filter(Loan.id == loan_id).with_for_update(of=Loan).first()
        )
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")

        product = loan.product

        # Calculate penalty (e.g., 0.1% of outstanding balance per day)
        penalty_rate = float(product.penalty_rate_per_day)
        penalty_amount = float(loan.outstanding_balance) * penalty_rate

        # Create ledger entry
        ledger_entry = LedgerEntry(
            branch_id=loan.branch_id,
            entry_no=f"JV-{reference}-{date.today().strftime('%Y%m%d')}",
            entry_type="LOAN_PENALTY",
            entry_date=date.today(),
            description=f"Late Payment Penalty - Loan {loan.id}",
            reference=reference,
            total_debit=penalty_amount,
            total_credit=penalty_amount,
            status="POSTED",
            created_by_id=actual_user_id,
        )
        db.add(ledger_entry)
        db.flush()

        # Create ledger lines
        penalty_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=product.penalty_income_account_id,
            dr_cr=DR_CR_DEBIT,
            amount=penalty_amount,
            description=f"Late payment penalty for loan {loan.id}",
            member_id=loan.member_id,
        )

        liability_line = LedgerLine(
            entry_id=ledger_entry.id,
            account_id=product.loan_receivable_account_id,
            dr_cr=DR_CR_CREDIT,
            amount=penalty_amount,
            description=f"Penalty accrual on loan {loan.id}",
            member_id=loan.member_id,
        )

        db.add_all([penalty_line, liability_line])

        # Record penalty
        penalty = LoanPenalty(
            loan_id=loan_id,
            amount=penalty_amount,
            penalty_type="LATE_PAYMENT",
            applied_date=date.today(),
            reference=reference,
            ledger_entry_id=ledger_entry.id,
        )
        db.add(penalty)
        db.commit()

        return penalty

    except Exception as e:
        db.rollback()
        raise e
