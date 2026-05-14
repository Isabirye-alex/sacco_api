from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.src.models.users.user_model import UserModel
from app.src.models.users.user_profile import UserProfile
from app.src.models.users.user_address import UserAddress
from app.src.schemas.users.user_schema import UserCreate
from sqlalchemy.exc import SQLAlchemyError


def create_new_user(db: Session, user: UserCreate):
    # 1. Insert into users table
    try:
        db_user = UserModel(
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            password=user.password,
        )

        db.add(db_user)
        db.flush()  # Get the user_id

        # 2. Create user profile
        db_profile = UserProfile(
            user_id=db_user.user_id,
            member_id=user.member_id,
            phone_number=user.phone_number,
            id_number=user.id_number,
            date_of_birth=user.date_of_birth,
            occupation=user.occupation,
            monthly_income=user.monthly_income,
            marital_status=user.marital_status,
            primary_language=user.primary_language,
            employer_name=user.employer_name,
        )

        db.add(db_profile)

        # 3. Create address
        db_address = UserAddress(
            user_id=db_user.user_id,
            district=user.district,
            nationality=user.nationality,
            sub_county=user.sub_county,
            village=user.village,
            parish=user.parish,
            postal_code=user.postal_code,
        )

        db.add(db_address)
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
        raise HTTPException(
            status_code=500, detail=f"Internal server error"
        )
