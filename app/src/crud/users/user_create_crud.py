from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.src.models.member import User
from app.src.schemas.users.user_schema import UserCreate
from app.src.utils.auth import hash_password
from sqlalchemy.exc import SQLAlchemyError


def create_new_user(db: Session, user: UserCreate):
    # 1. Insert into users table
    try:
        # Hash the password if provided, otherwise leave as None so model default applies
        pwd = hash_password(user.password) if user.password else None

        db_user = User(
            role_id=user.role_id,
            hashed_password=pwd,
        )

        db.add(db_user)
        db.flush()  # Get the user_id

        # 2. Create user profile
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:

        # If any of the above fails, undo everything
        db.rollback()
        # Log the actual error for the developer
        print(f"Unexpected Error: {str(e)}")
        # Raise an exception that FastApi can return to the user
        raise HTTPException(
            status_code=400,
            detail="Could not create user. Please check if your id or email is already registered",
        )

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error")
