from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.src.models.member import Member

def get_next_sequential_number(db: Session, organisation_id: str) -> str:
    """
    Looks up the highest current member number for the organization 
    and increments it by 1. Returns a zero-padded string.
    """
    # Query the maximum member number for this specific organization
    max_member_no = db.query(func.max(Member.member_no)).filter(
        Member.organisation_id == organisation_id
    ).scalar()
    
    # Handle the base case for the very first member
    if not max_member_no or not max_member_no.isdigit():
        next_number = 1
    else:
        next_number = int(max_member_no) + 1
        
    # Returns a 6-digit zero-padded string (e.g., "000001", "000142")
    return f"{next_number:06d}"


def register_member_safely(db: Session, organisation_id: str, member_data: dict) -> Member:
    """
    Safely creates a member. If a race condition happens (another process 
    takes the sequential number first), it rolls back and retries smoothly.
    """
    # Set a safety limit so an infinite loop doesn't hang the server if something else breaks
    max_retries = 10  
    attempts = 0

    while attempts < max_retries:
        try:
            # 1. Calculate the next expected sequential number
            assigned_no = get_next_sequential_number(db, organisation_id)
            
            # 2. Instantiate the model
            new_member = Member(
                organisation_id=organisation_id,
                member_no=assigned_no,
                **member_data
            )
            db.add(new_member)
            
            # 3. Attempt to flush/commit to the database
            db.commit()
            return new_member

        except IntegrityError:
            # RACE CONDITION DETECTED! 
            # Another user committed the exact same member_no between lines 25 and 33.
            db.rollback()  # Clear the failed transaction state
            attempts += 1  # Increment attempt counter and try again instantly
            
    raise RuntimeError(
        f"Failed to assign a unique member number after {max_retries} concurrent collision attempts."
    )