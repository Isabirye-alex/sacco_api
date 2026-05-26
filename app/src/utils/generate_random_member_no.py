from sqlalchemy import text
from sqlalchemy.orm import Session
from app.src.models.member import Member


def register_member_safely(db: Session, member_data: dict) -> Member:
    """
    Creates a member tracking a global sequential sequence.
    Uses PostgreSQL sequences for atomic, high-performance ID allocation.
    """
    # 1. Define the sequence name (could be scoped per-org if multi-tenant)
    seq_name = "member_no_seq"

    # 2. Get the next value atomically
    # Note: In production, move 'CREATE SEQUENCE' to an Alembic migration
    query = text(
        f"CREATE SEQUENCE IF NOT EXISTS {seq_name} START WITH 1; SELECT nextval('{seq_name}');"
    )
    next_val = db.execute(query).scalar()
    assigned_no = f"{next_val:06d}"

    new_member = Member(member_no=assigned_no, **member_data)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member
