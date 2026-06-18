from decimal import Decimal

from sqlalchemy.orm import Session

from app.src.models.savings import SavingsAccount, SavingsTransaction, SavingsTxTypeEnum
from app.src.repositories.savings_repository import SavingsRepository
from app.src.schemas.savings import SavingsDepositDTO, SavingsWithdrawDTO


class SavingsService:
  """Domain service for savings operations."""

  def __init__(self, repository: SavingsRepository):
    self.repo = repository

  def deposit(self, db: Session, dto: SavingsDepositDTO) -> SavingsTransaction:
    account: SavingsAccount | None = self.repo.get_account(db, dto.account_id)
    if account is None:
      raise ValueError("Account not found")

    if dto.amount <= 0:
      raise ValueError("Deposit amount must be positive")

    new_balance = Decimal(account.balance) + Decimal(dto.amount)
    self.repo.update_account_balance(db, account, new_balance)

    tx = SavingsTransaction(
      organisation_id=account.organisation_id,
      account_id=account.id,
      tx_type=SavingsTxTypeEnum.DEPOSIT,
      amount=dto.amount,
      balance_after=new_balance,
      transaction_date=dto.transaction_date,
      reference=dto.reference,
      description=dto.description,
      processed_by_id=dto.processed_by_id,
    )

    return self.repo.create_transaction(db, tx)

  def withdraw(self, db: Session, dto: SavingsWithdrawDTO) -> SavingsTransaction:
    account: SavingsAccount | None = self.repo.get_account(db, dto.account_id)
    if account is None:
      raise ValueError("Account not found")

    if dto.amount <= 0:
      raise ValueError("Withdrawal amount must be positive")

    if Decimal(account.balance) < Decimal(dto.amount):
      raise ValueError("Insufficient funds")

    new_balance = Decimal(account.balance) - Decimal(dto.amount)
    self.repo.update_account_balance(db, account, new_balance)

    tx = SavingsTransaction(
      organisation_id=account.organisation_id,
      account_id=account.id,
      tx_type=SavingsTxTypeEnum.WITHDRAWAL,
      amount=dto.amount,
      balance_after=new_balance,
      transaction_date=dto.transaction_date,
      reference=dto.reference,
      description=dto.description,
      processed_by_id=dto.processed_by_id,
    )

    return self.repo.create_transaction(db, tx)
