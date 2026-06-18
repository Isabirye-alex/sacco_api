from abc import ABC, abstractmethod


class SavingsRepository(ABC):
    """Repository contract for savings-related persistence operations."""

    @abstractmethod
    def get_account(self, db, account_id):
        """Return a savings account by id or None if it does not exist."""

    @abstractmethod
    def update_account_balance(self, db, account, new_balance):
        """Persist the new account balance."""

    @abstractmethod
    def create_transaction(self, db, tx):
        """Create and return a transaction record."""
