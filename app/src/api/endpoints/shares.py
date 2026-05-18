from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.crud.shares.share_crud import (
    create_share_product,
    create_share_account,
    create_share_transaction,
    create_dividend,
    create_dividend_payment,
)
from app.src.models.shares import (
    ShareProduct,
    ShareAccount,
    ShareTransaction,
    Dividend,
    DividendPayment,
)
from app.src.schemas.shares.share_schema import (
    ShareProductCreate,
    ShareProductResponse,
    ShareAccountCreate,
    ShareAccountResponse,
    ShareTransactionCreate,
    ShareTransactionResponse,
    DividendCreate,
    DividendResponse,
    DividendPaymentCreate,
    DividendPaymentResponse,
)

router = APIRouter()


@router.post(
    "/products",
    response_model=ShareProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_share_product_endpoint(
    product: ShareProductCreate, db: Session = Depends(get_db)
):
    try:
        return create_share_product(db, product)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/products", response_model=list[ShareProductResponse])
def list_share_products(db: Session = Depends(get_db)):
    return db.query(ShareProduct).all()


@router.post(
    "/accounts",
    response_model=ShareAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_share_account_endpoint(
    account: ShareAccountCreate, db: Session = Depends(get_db)
):
    try:
        return create_share_account(db, account)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/accounts", response_model=list[ShareAccountResponse])
def list_share_accounts(db: Session = Depends(get_db)):
    return db.query(ShareAccount).all()


@router.post(
    "/transactions",
    response_model=ShareTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_share_transaction_endpoint(
    tx: ShareTransactionCreate, db: Session = Depends(get_db)
):
    try:
        return create_share_transaction(db, tx)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/transactions", response_model=list[ShareTransactionResponse])
def list_share_transactions(db: Session = Depends(get_db)):
    return db.query(ShareTransaction).all()


@router.post(
    "/dividends",
    response_model=DividendResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dividend_endpoint(dividend: DividendCreate, db: Session = Depends(get_db)):
    try:
        return create_dividend(db, dividend)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/dividends", response_model=list[DividendResponse])
def list_dividends(db: Session = Depends(get_db)):
    return db.query(Dividend).all()


@router.post(
    "/dividend-payments",
    response_model=DividendPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dividend_payment_endpoint(
    payment: DividendPaymentCreate, db: Session = Depends(get_db)
):
    try:
        return create_dividend_payment(db, payment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/dividend-payments", response_model=list[DividendPaymentResponse])
def list_dividend_payments(db: Session = Depends(get_db)):
    return db.query(DividendPayment).all()
