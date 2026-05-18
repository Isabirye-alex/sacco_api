from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.crud.savings.savings_crud import (
    create_savings_product,
    create_savings_account,
    create_savings_transaction,
)
from app.src.models.savings import SavingsProduct, SavingsAccount, SavingsTransaction
from app.src.schemas.savings import (
    SavingsProductCreate,
    SavingsProductResponse,
    SavingsAccountCreate,
    SavingsAccountResponse,
    SavingsTransactionCreate,
    SavingsTransactionResponse,
)

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


@router.post(
    "/accounts",
    response_model=SavingsAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_savings_account_endpoint(
    account: SavingsAccountCreate, db: Session = Depends(get_db)
):
    try:
        return create_savings_account(db, account)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/accounts", response_model=list[SavingsAccountResponse])
def list_savings_accounts(db: Session = Depends(get_db)):
    return db.query(SavingsAccount).all()


@router.post(
    "/transactions",
    response_model=SavingsTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_savings_transaction_endpoint(
    tx: SavingsTransactionCreate, db: Session = Depends(get_db)
):
    try:
        return create_savings_transaction(db, tx)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/transactions", response_model=list[SavingsTransactionResponse])
def list_savings_transactions(db: Session = Depends(get_db)):
    return db.query(SavingsTransaction).all()
