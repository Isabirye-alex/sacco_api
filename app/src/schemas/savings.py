from datetime import date
from pydantic import BaseModel
from typing import Optional


class SavingsDepositDTO(BaseModel):
    account_id: str
    amount: float
    transaction_date: date
    reference: Optional[str] = None
    description: Optional[str] = None
    processed_by_id: Optional[str] = None


class SavingsWithdrawDTO(BaseModel):
    account_id: str
    amount: float
    transaction_date: date
    reference: Optional[str] = None
    description: Optional[str] = None
    processed_by_id: Optional[str] = None


class SavingsAccountDTO(BaseModel):
    id: str
    account_no: str
    balance: float


class SavingsTransactionDTO(BaseModel):
    id: str
    account_id: str
    tx_type: str
    amount: float
    balance_after: float
    transaction_date: date
    reference: Optional[str]
