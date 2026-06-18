from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.src.models.savings import SavingsAccount, SavingsTransaction


class SavingsRepository:
  """SQLAlchemy repository for savings accounts and transactions."""

  def get_account(self, db: Session, account_id: UUID) -> Optional[SavingsAccount]:
    return (
      db.query(SavingsAccount)
      .filter(SavingsAccount.id == account_id)
      .one_or_none()
    )

  def update_account_balance(
    self, db: Session, account: SavingsAccount, new_balance: Decimal
  ) -> None:
    account.balance = new_balance
    db.add(account)
    db.flush()

  def create_transaction(
    self, db: Session, tx: SavingsTransaction
  ) -> SavingsTransaction:
    db.add(tx)
    db.flush()
    db.commit()
    db.refresh(tx)
    return tx
