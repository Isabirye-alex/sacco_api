"""Module for app.src.utils.generate_unique_application_no."""

import secrets
import uuid
from sqlalchemy.orm import Session

def generate_unique_application_number() -> str:
    raw_uuid = str(uuid.uuid7()).upper() 
    parts = raw_uuid.split("-")
    
    return f"LA-{parts[0]}-{parts[4][-4:]}"
    # Example output: L-019550AF-9E2B