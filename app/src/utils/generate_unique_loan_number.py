"""Module for app.src.utils.generate_unique_loan_number."""

import uuid

def generate_uuid_loan_number() -> str:
    raw_uuid = str(uuid.uuid7()).upper() 
    parts = raw_uuid.split("-")
    
    # parts[0] = Timestamp prefix
    # parts[4] = Randomized ending sequence
    # This takes the time prefix and the last 4 characters of randomness
    return f"LD-{parts[0]}-{parts[4][-4:]}"
    # Example output: L-019550AF-9E2B