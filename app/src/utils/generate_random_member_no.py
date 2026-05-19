import secrets
from sqlalchemy.orm import Session

from app.src.models.member import Member

def generate_random_member_no(db: Session, organisation_id: str) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    
    while True:
        # Generate all 8 characters in one single line
        code = "".join(secrets.choice(alphabet) for _ in range(10))
        
        # Check for collisions within this specific SACCO
        exists = db.query(Member.id).filter(
            Member.organisation_id == organisation_id,
            Member.member_no == code
        ).first()
        
        if not exists:
            return code