from datetime import date
from app.src.utils.generate_random_account_number import generate_unique_account_no

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.src.utils.generate_random_member_no import generate_random_member_no
from app.src.models.member import (
    Member,
    Gender,
    MemberStatus,
    MaritalStatus,
    Role,
    NextOfKin,
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


def _resolve_savings_account_status_id(db: Session, code: str = "ACTIVE"):
    status = db.query(SavingsAccountStatus).filter_by(code=code).first()
    if not status:
        status = SavingsAccountStatus(code=code, description=code)
        db.add(status)
        db.flush()
    return status.id


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


def create_member(db: Session, member: MemberCreate) -> Member:
    # 1. Automatically generate the unique 8-character member number
    generated_no = generate_random_member_no(db, member.organisation_id)

    db_member = Member(
        organisation_id=member.organisation_id,
        member_no=generated_no,  # Auto-assigned safely
        first_name=member.first_name,
        middle_name=member.middle_name,
        last_name=member.last_name,
        email=member.email,
        branch_id=member.branch_id,
        gender_id=member.gender_id,
        status_id=member.status_id,
        date_of_birth=member.date_of_birth,
        national_id=member.national_id,
        marital_status_id=member.marital_status_id,  # Matches your model naming
        photo_url=member.photo_url,
        phone_primary=member.phone_primary,
        phone_secondary=member.phone_secondary,
        country=member.country,
        village=member.village,
        district=member.district,
        joined_date=member.joined_date,
        exit_date=member.exit_date,
        exit_reason=member.exit_reason,
    )

    try:
        with db.begin():
            db.add(db_member)
            db.flush()
            _create_member_savings_account(db, db_member)
            db.refresh(db_member)

        return db_member

    except IntegrityError as e:
        db.rollback()  # Cleans up the failed transaction state
        error_msg = str(e.orig)

        # Catch phone duplication
        if "phone_primary" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A member with this primary phone number already exists.",
            )
        # Catch invalid Foreign Keys (e.g. branch_id, gender_id, or status_id doesn't exist)
        elif (
            "foreign key constraint" in error_msg.lower()
            or "violates foreign key" in error_msg.lower()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reference ID provided. Please verify organization, branch, gender, and status IDs.",
            )
        # Fallback for any other unique constraints
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity violation occurred while saving member details.",
        )


def create_gender(db: Session, gender: GenderCreate):
    db_gender = Gender(
        gender=gender.gender,
        description=gender.description,
    )
    db.add(db_gender)
    db.commit()
    db.refresh(db_gender)
    return db_gender


def create_member_status(db: Session, status: MemberStatusCreate):
    db_status = MemberStatus(
        status=status.status,
        description=status.description,
    )
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status


def create_marital_status(db: Session, status: MaritalStatusCreate):
    db_status = MaritalStatus(
        status=status.status,
    )
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status


def create_role(db: Session, role: RoleCreate):
    db_role = Role(
        role=role.role,
        description=role.description,
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
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
    db.commit()
    db.refresh(db_kin)
    return db_kin
