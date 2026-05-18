from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.crud.loans.loan_crud import (
    create_loan_product,
    create_loan_application,
    create_loan,
    create_loan_guarantor,
    create_loan_collateral,
    create_loan_repayment_schedule,
    create_loan_repayment,
    create_loan_penalty,
)
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
    LoanProductResponse,
    LoanApplicationCreate,
    LoanApplicationResponse,
    LoanCreate,
    LoanResponse,
    LoanGuarantorCreate,
    LoanGuarantorResponse,
    LoanCollateralCreate,
    LoanCollateralResponse,
    LoanRepaymentScheduleCreate,
    LoanRepaymentScheduleResponse,
    LoanRepaymentCreate,
    LoanRepaymentResponse,
    LoanPenaltyCreate,
    LoanPenaltyResponse,
)

router = APIRouter()


@router.post(
    "/products", response_model=LoanProductResponse, status_code=status.HTTP_201_CREATED
)
def create_loan_product_endpoint(
    product: LoanProductCreate, db: Session = Depends(get_db)
):
    try:
        return create_loan_product(db, product)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/products", response_model=list[LoanProductResponse])
def list_loan_products(db: Session = Depends(get_db)):
    return db.query(LoanProduct).all()


@router.post(
    "/applications",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_application_endpoint(
    application: LoanApplicationCreate, db: Session = Depends(get_db)
):
    try:
        return create_loan_application(db, application)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/applications", response_model=list[LoanApplicationResponse])
def list_loan_applications(db: Session = Depends(get_db)):
    return db.query(LoanApplication).all()


@router.post(
    "/loans",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_endpoint(loan: LoanCreate, db: Session = Depends(get_db)):
    try:
        return create_loan(db, loan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/loans", response_model=list[LoanResponse])
def list_loans(db: Session = Depends(get_db)):
    return db.query(Loan).all()


@router.post(
    "/guarantors",
    response_model=LoanGuarantorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_guarantor_endpoint(
    guarantor: LoanGuarantorCreate, db: Session = Depends(get_db)
):
    try:
        return create_loan_guarantor(db, guarantor)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/guarantors", response_model=list[LoanGuarantorResponse])
def list_loan_guarantors(db: Session = Depends(get_db)):
    return db.query(LoanGuarantor).all()


@router.post(
    "/collaterals",
    response_model=LoanCollateralResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_collateral_endpoint(
    collateral: LoanCollateralCreate, db: Session = Depends(get_db)
):
    try:
        return create_loan_collateral(db, collateral)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/collaterals", response_model=list[LoanCollateralResponse])
def list_loan_collaterals(db: Session = Depends(get_db)):
    return db.query(LoanCollateral).all()


@router.post(
    "/repayment-schedules",
    response_model=LoanRepaymentScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_repayment_schedule_endpoint(
    schedule: LoanRepaymentScheduleCreate, db: Session = Depends(get_db)
):
    try:
        return create_loan_repayment_schedule(db, schedule)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/repayment-schedules", response_model=list[LoanRepaymentScheduleResponse])
def list_loan_repayment_schedules(db: Session = Depends(get_db)):
    return db.query(LoanRepaymentSchedule).all()


@router.post(
    "/repayments",
    response_model=LoanRepaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_repayment_endpoint(
    repayment: LoanRepaymentCreate, db: Session = Depends(get_db)
):
    try:
        return create_loan_repayment(db, repayment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/repayments", response_model=list[LoanRepaymentResponse])
def list_loan_repayments(db: Session = Depends(get_db)):
    return db.query(LoanRepayment).all()


@router.post(
    "/penalties",
    response_model=LoanPenaltyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan_penalty_endpoint(
    penalty: LoanPenaltyCreate, db: Session = Depends(get_db)
):
    try:
        return create_loan_penalty(db, penalty)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/penalties", response_model=list[LoanPenaltyResponse])
def list_loan_penalties(db: Session = Depends(get_db)):
    return db.query(LoanPenalty).all()
