from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.repositories.savings_repository import SavingsRepository
from app.src.schemas.savings import (
  SavingsAccountResponse,
  SavingsDepositDTO,
  SavingsTransactionResponse,
  SavingsWithdrawDTO,
)
from app.src.services.savings_service import SavingsService

router = APIRouter()
_savings_service = SavingsService(SavingsRepository())


@router.get("/accounts/{account_id}", response_model=SavingsAccountResponse)
def get_savings_account(account_id: UUID, db: Session = Depends(get_db)):
  account = _savings_service.repo.get_account(db, account_id)
  if not account:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail="Savings account not found"
    )
  return account


@router.post(
  "/deposit",
  response_model=SavingsTransactionResponse,
  status_code=status.HTTP_201_CREATED,
)
def deposit_savings(dto: SavingsDepositDTO, db: Session = Depends(get_db)):
  try:
    return _savings_service.deposit(db, dto)
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
  "/withdraw",
  response_model=SavingsTransactionResponse,
  status_code=status.HTTP_201_CREATED,
)
def withdraw_savings(dto: SavingsWithdrawDTO, db: Session = Depends(get_db)):
  try:
    return _savings_service.withdraw(db, dto)
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
