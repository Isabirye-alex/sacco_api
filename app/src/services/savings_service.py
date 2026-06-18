from dataclasses import dataclass
from decimal import Decimal
from types import SimpleNamespace


@dataclass
class SavingsTransactionResult:
    id: str | None
    account_id: str
    amount: Decimal
    transaction_type: str


class SavingsService:
    """Business logic for savings flows following a clean service layer pattern."""

    def __init__(self, repository):
        self.repository = repository

    def deposit(self, db, dto):
        account = self.repository.get_account(db, dto.account_id)
        if account is None:
            raise ValueError(f"Account {dto.account_id} not found")

        new_balance = Decimal(str(account.balance)) + Decimal(str(dto.amount))
        self.repository.update_account_balance(db, account, new_balance)

        transaction = SimpleNamespace(
            id=None,
            account_id=dto.account_id,
            amount=Decimal(str(dto.amount)),
            transaction_type="deposit",
            reference=dto.reference,
            description=dto.description,
            transaction_date=dto.transaction_date,
            processed_by_id=dto.processed_by_id,
        )
        transaction = self.repository.create_transaction(db, transaction)
        return transaction
