from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.src.models import SavingsTransaction, SavingsTxType # Adjust paths to your models

def _resolve_savings_tx_type_id(db: Session, tx_type_code: str) -> UUID:
    """
    Looks up the underlying UUID for a given transaction string code.
    Fails safely with a 400 error if the system receives an invalid type code.
    """
    # Force uppercase to avoid case-sensitivity bugs (e.g., 'deposit' vs 'DEPOSIT')
    normalized_code = tx_type_code.strip().upper() 
    
    result = db.query(SavingsTxType.id).filter(SavingsTxType.code == normalized_code).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transaction type code '{tx_type_code}'. Must be DEPOSIT, WITHDRAWAL, etc."
        )
        
    return result.id