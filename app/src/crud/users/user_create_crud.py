from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.src.models.member import Member, User
from app.src.schemas.users.user_schema import UserCreate, UserResponse
from app.src.utils.auth import hash_password


def _to_user_response(user: User) -> UserResponse:
  member = user.member
  return UserResponse(
    id=user.id,
    organisation_id=user.organisation_id,
    member_id=user.member_id,
    email=user.email,
    phone=user.phone,
    is_active=user.is_active,
    is_verified=user.is_verified,
    first_name=member.first_name if member else None,
    last_name=member.last_name if member else None,
    member_no=member.member_no if member else None,
  )


def create_new_user(db: Session, user: UserCreate) -> UserResponse:
  try:
    member = Member(
      organisation_id=user.organisation_id,
      branch_id=user.branch_id,
      gender_id=user.gender_id,
      status_id=user.status_id,
      member_no=user.member_no,
      first_name=user.first_name,
      middle_name=user.middle_name,
      last_name=user.last_name,
      date_of_birth=user.date_of_birth,
      national_id=user.national_id,
      phone_primary=user.phone_primary,
      phone_secondary=user.phone_secondary,
      email=user.email,
      country=user.country,
      village=user.village,
      district=user.district,
      joined_date=user.joined_date,
    )
    db.add(member)
    db.flush()

    db_user = User(
      organisation_id=user.organisation_id,
      member_id=member.id,
      role_id=user.role_id,
      email=user.email,
      phone=user.phone_primary,
      hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return _to_user_response(db_user)
  except SQLAlchemyError as e:
    db.rollback()
    print(f"Database error creating user: {e}")
    raise HTTPException(
      status_code=400,
      detail="Could not create user. Check that email or member number is not already registered.",
    )
  except Exception as e:
    db.rollback()
    print(f"Unexpected error creating user: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
