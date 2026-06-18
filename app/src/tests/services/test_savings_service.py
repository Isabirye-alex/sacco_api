import datetime
from decimal import Decimal
from uuid import uuid4

from app.src.repositories.savings_repository import SavingsRepository
from app.src.schemas.savings import SavingsDepositDTO
from app.src.services.savings_service import SavingsService


class DummyAccount:
  def __init__(self, id, organisation_id, balance):
    self.id = id
    self.organisation_id = organisation_id
    self.balance = Decimal(balance)


class DummyRepo(SavingsRepository):
  def __init__(self):
    self.account = DummyAccount(uuid4(), uuid4(), "100.00")

  def get_account(self, db, account_id):
    return self.account if account_id == self.account.id else None

  def update_account_balance(self, db, account, new_balance):
    account.balance = Decimal(new_balance)

  def create_transaction(self, db, tx):
    tx.id = uuid4()
    return tx


def test_deposit_increases_balance():
  repo = DummyRepo()
  svc = SavingsService(repo)
  dto = SavingsDepositDTO(
    account_id=repo.account.id,
    amount=Decimal("50.00"),
    transaction_date=datetime.date.today(),
    reference="ref-1",
    description="test",
  )

  tx = svc.deposit(None, dto)
  assert tx.id is not None
  assert repo.account.balance == Decimal("150.00")
