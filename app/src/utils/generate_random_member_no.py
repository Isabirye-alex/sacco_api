from sqlalchemy import func, cast, Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.src.models.member import Member


def get_next_sequential_number(db: Session) -> str:
    """
    Safely finds the highest current member number globally.
    Uses regex to isolate numeric digits before casting to prevent DB errors,
    falling back securely if no records exist.
    """
    # 1. Clean the string to ensure only numeric digits remain
    clean_numeric_string = func.regexp_replace(Member.member_no, r"[^\d]", "", "g")

    # 2. Extract the highest numerical value safely
    max_val = db.query(
        func.max(cast(func.nullif(clean_numeric_string, ""), Integer))
    ).scalar()

    # 3. Increment the sequence counter safely
    if max_val is None:
        next_number = 1
    else:
        next_number = int(max_val) + 1

    return f"{next_number:06d}"


def register_member_safely(db: Session, member_data: dict) -> Member:
    """
    Creates a member tracking a global sequential sequence.
    Handles any tight concurrency race conditions safely via targeted loop retries.
    """
    max_retries = 15
    attempts = 0

    while attempts < max_retries:
        try:
            # Generate the next padded string key
            assigned_no = get_next_sequential_number(db)

            new_member = Member(member_no=assigned_no, **member_data)
            db.add(new_member)
            db.commit()
            return new_member

        except IntegrityError:
            # Race condition caught: another thread saved this number first.
            # Rollback to clear transaction state and retry with an updated sequence lookahead.
            db.rollback()
            attempts += 1

    raise RuntimeError(
        "Failed to allocate a unique member number due to excessive concurrent registration traffic."
    )
