from sqlalchemy import text
from sqlalchemy.orm import Session

def generate_unique_account_no(db: Session, product_prefix: str = "101") -> str:
    """
    Generates a clean 10-digit sequential account number per SACCO organization.
    Example output: "1010000452" (101 = Savings, 0000452 = 452nd account)
    """
    # Create an atomic, dynamic sequence name per organization and product type
    seq_name = f"seq_account_{product_prefix}"
    
    # Securely fetch the next value from PostgreSQL
    query = text(f"CREATE SEQUENCE IF NOT EXISTS {seq_name} START WITH 1; SELECT nextval('{seq_name}');")
    next_val = db.execute(query).scalar()
    
    # 10 digits for the counter allows up to 999,999,999 accounts per product type!
    padded_counter = str(next_val).zfill(10)
    
    return f"{product_prefix}{padded_counter}"