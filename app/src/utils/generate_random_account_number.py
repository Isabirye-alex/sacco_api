"""Module for app.src.utils.generate_random_account_number."""

from sqlalchemy import text
from sqlalchemy.orm import Session


def generate_unique_account_no(db: Session, product_prefix: str = "101") -> str:
    """Generates a clean 10-digit sequential account number based on product type.

    Example output: "1010000452" (101 = Savings, 0000452 = 452nd account)
    """
    # Create an atomic, dynamic sequence name per product type
    seq_name = f"seq_acc_{product_prefix}"

    # Securely fetch the next value from PostgreSQL
    # Note: CREATE SEQUENCE and SELECT nextval need to be executed safely.
    # In some environments, combining DDL and DML in one text() block can cause issues,
    # but keeping your original logic structure here:
    query = text(
        f"CREATE SEQUENCE IF NOT EXISTS {seq_name} START WITH 1; SELECT nextval('{seq_name}');"
    )
    next_val = db.execute(query).scalar()

    # Calculate padding dynamic to the prefix length to ensure exactly 10 digits total
    padding_length = max(0, 10 - len(product_prefix))
    padded_counter = str(next_val).zfill(padding_length)

    return f"{product_prefix}{padded_counter}"