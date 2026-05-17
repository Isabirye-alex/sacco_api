from typing import Protocol, Optional
from sqlalchemy.orm import Session

from app.src.models.savings import SavingsAccount, SavingsTransaction


class SavingsRepositoryProtocol(Protocol):
    def get_account(self, db: Session, account_id: str) -> Optional[SavingsAccount]: ...

    def update_account_balance(
        self, db: Session, account: SavingsAccount, new_balance
    ) -> None: ...

    def create_transaction(
        self, db: Session, tx: SavingsTransaction
    ) -> SavingsTransaction: ...


class SavingsRepository:
    """Concrete repository encapsulating SQLAlchemy operations for savings."""

    def get_account(self, db: Session, account_id: str) -> Optional[SavingsAccount]:
        return (
            db.query(SavingsAccount)
            .filter(SavingsAccount.id == account_id)
            .one_or_none()
        )

    def update_account_balance(
        self, db: Session, account: SavingsAccount, new_balance
    ) -> None:
        account.balance = new_balance
        db.add(account)
        db.flush()

    def create_transaction(
        self, db: Session, tx: SavingsTransaction
    ) -> SavingsTransaction:
        db.add(tx)
        db.flush()
        return tx
