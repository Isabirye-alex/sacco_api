"""Module for app.src.tests.services.test_savings_service."""

import datetime
from decimal import Decimal

import pytest

from app.src.services.savings_service import SavingsService
from app.src.repositories.savings_repository import SavingsRepository


class DummyAccount:
    def __init__(self, id, organisation_id, balance):
        self.id = id
        self.organisation_id = organisation_id
        self.balance = Decimal(balance)


class DummyDB:
    def __init__(self):
        self._flushed = []


class DummyRepo(SavingsRepository):
    def __init__(self):
        self.account = DummyAccount("acc-1", "org-1", "100.00")

    def get_account(self, db, account_id):
        return self.account if account_id == self.account.id else None

    def update_account_balance(self, db, account, new_balance):
        account.balance = Decimal(new_balance)

    def create_transaction(self, db, tx):
        tx.id = "tx-1"
        return tx


def test_deposit_increases_balance():
    repo = DummyRepo()
    svc = SavingsService(repo)
    dto = type(
        "D",
        (),
        {
            "account_id": "acc-1",
            "amount": 50.0,
            "transaction_date": datetime.date.today(),
            "reference": "ref-1",
            "description": "test",
            "processed_by_id": None,
        },
    )

    tx = svc.deposit(None, dto)
    assert tx.id == "tx-1"
    assert repo.account.balance == Decimal("150.00")
