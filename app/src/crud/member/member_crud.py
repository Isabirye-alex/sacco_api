from datetime import date
from app.src.schemas.users.user_schema import UserCreate
from app.src.utils.generate_random_account_number import generate_unique_account_no
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.src.models.member import (
    Member,
    Gender,
    MemberStatus,
    MaritalStatus,
    Role,
    NextOfKin,
    User,
)
from app.src.models.savings import (
    SavingsAccount,
    SavingsAccountStatus,
    SavingsProduct,
)
from app.src.schemas.member.member_schema import (
    MemberCreate,
    GenderCreate,
    MemberStatusCreate,
    MaritalStatusCreate,
    RoleCreate,
    NextOfKinCreate,
)
from app.src.utils.generate_random_member_no import register_member_safely


def _resolve_savings_account_status_id(db: Session, code: str = "ACTIVE"):
    status_obj = db.query(SavingsAccountStatus).filter_by(code=code).first()
    if not status_obj:
        status_obj = SavingsAccountStatus(code=code, description=code)
        db.add(status_obj)
        db.flush()
    return status_obj.id


def _find_default_savings_product(db: Session) -> SavingsProduct:
    product = (
        db.query(SavingsProduct).filter_by(code="ORDINARY", is_active=True).first()
    )
    if not product:
        product = db.query(SavingsProduct).filter_by(is_active=True).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No active savings product is configured. Please configure a savings product before creating members.",
        )

    return product


def _create_member_savings_account(db: Session, member: Member):
    product = _find_default_savings_product(db)
    status_id = _resolve_savings_account_status_id(db, "ACTIVE")

    account_number = generate_unique_account_no(db)

    savings_account = SavingsAccount(
        branch_id=member.branch_id,
        member_id=member.id,
        product_id=product.id,
        account_no=account_number,
        balance=0,
        status_id=status_id,
        opened_date=member.joined_date or date.today(),
    )
    db.add(savings_account)
    db.flush()
    return savings_account


def create_member(db: Session, member: MemberCreate, user: UserCreate) -> Member:
    from app.src.utils.auth import hash_password

    max_retries = 10
    attempts = 0

    while attempts < max_retries:
        generated_no = register_member_safely(db, member.dict())

        db_member = Member(
            member_no=generated_no,
            first_name=member.first_name,
            middle_name=member.middle_name,
            last_name=member.last_name,
            email=member.email,
            branch_id=member.branch_id,
            gender_id=member.gender_id,
            date_of_birth=member.date_of_birth,
            national_id=member.national_id,
            marital_status_id=member.marital_status_id,
            phone_primary=member.phone_primary,
            phone_secondary=member.phone_secondary,
            country=member.country,
            village=member.village,
            district=member.district,
            joined_date=member.joined_date or date.today(),
            exit_date=member.exit_date,
            exit_reason=member.exit_reason,
        )

        try:
            # Wrap execution inside a nested savepoint transaction block
            with db.begin_nested():
                db.add(db_member)
                db.flush()  # Populates db_member.id so savings account FK works
                _create_member_savings_account(db, db_member)

                # Create User record linked to the new member
                db_user = User(
                    member_id=db_member.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone=user.phone,
                    hashed_password=hash_password(user.password),
                )
                db.add(db_user)
                db.flush()
            # If everything inside the savepoint succeeded, commit it globally
            db.commit()
            db.refresh(db_member)
            return db_member

        except IntegrityError as e:
            # The savepoint block automatically rolled back the failed insert state
            error_msg = str(e.orig).lower()
            print(error_msg)

            # CASE A: Check if the collision was specifically due to the member number
            # Update 'uq_organisation_member_no' to match your actual database constraint name
            if "uq_organisation_member_no" in error_msg or "member_no" in error_msg:
                attempts += 1
                continue  # Loop back, get a fresh number, and try again seamlessly!

            # CASE B: It's an integrity violation unrelated to member_no (no point in retrying)
            if "phone_primary" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A member with this primary phone number already exists.",
                )
            elif (
                "foreign key constraint" in error_msg
                or "violates foreign key" in error_msg
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reference ID provided. Please verify organization, branch, gender, and status IDs.",
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity violation occurred while saving member details.",
            )

    # Safety valve trigger
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to allocate a unique member number due to excessive concurrent registration traffic.",
    )


def create_gender(db: Session, gender: GenderCreate):
    db_gender = Gender(
        gender=gender.gender,
        description=gender.description,
    )
    db.add(db_gender)
    db.flush()
    db.refresh(db_gender)
    db.commit()
    return db_gender


def create_member_status(db: Session, status: MemberStatusCreate):
    db_status = MemberStatus(
        status=status.status,
        description=status.description,
    )
    db.add(db_status)
    db.flush()
    db.refresh(db_status)
    return db_status


def create_marital_status(db: Session, status: MaritalStatusCreate):
    db_status = MaritalStatus(
        status=status.status,
    )
    db.add(db_status)
    db.flush()
    db.refresh(db_status)
    db.commit()
    return db_status


def create_role(db: Session, role: RoleCreate):
    db_role = Role(
        role=role.role,
        description=role.description,
    )
    db.add(db_role)
    db.flush()
    db.refresh(db_role)
    db.commit()
    return db_role


def create_next_of_kin(db: Session, kin: NextOfKinCreate):
    db_kin = NextOfKin(
        member_id=kin.member_id,
        first_name=kin.first_name,
        last_name=kin.last_name,
        email=kin.email,
        phone=kin.phone,
        address=kin.address,
        relationship_to_member=kin.relationship_to_member,
        national_id=kin.national_id,
        is_primary=kin.is_primary,
        marital_status_id=kin.marital_status_id,
    )
    db.add(db_kin)
    db.flush()
    db.refresh(db_kin)
    db.commit()
    return db_kin


def get_current_member(db: Session, member_id: str):
    current_user = (
        db.query(Member)
        .filter(Member.id == member_id)
        .options(
            selectinload(Member.savings_accounts),
            selectinload(Member.share_accounts),
            selectinload(Member.loans),
            selectinload(Member.next_of_kin),
            selectinload(Member.marital_status),
            selectinload(Member.gender),
            selectinload(Member.marital_status),
            selectinload(Member.branch),
            selectinload(Member.user),
        )
        .first()
    )
    return current_user
