from sqlalchemy.orm import Session

from app.src.models.member import (
    Member,
    Gender,
    MemberStatus,
    MaritalStatus,
    Role,
    NextOfKin,
)
from app.src.schemas.member.member_schema import (
    MemberCreate,
    GenderCreate,
    MemberStatusCreate,
    MaritalStatusCreate,
    RoleCreate,
    NextOfKinCreate,
)


def create_member(db: Session, member: MemberCreate):
    db_member = Member(
        first_name=member.first_name,
        middle_name=member.middle_name,
        last_name=member.last_name,
        email=member.email,
        phone=member.phone,
        branch_id=member.branch_id,
        gender_id=member.gender_id,
        status_id=member.status_id,
        user_id=member.user_id,
        member_no=member.member_no,
        date_of_birth=member.date_of_birth,
        national_id=member.national_id,
        marital_status=member.marital_status,
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
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


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
    db_role = Roles(
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
        middle_name=kin.middle_name,
        last_name=kin.last_name,
        email=kin.email,
        phone=kin.phone,
        address=kin.address,
        member_relationship=kin.member_relationship,
        national_id=kin.national_id,
        is_primary=kin.is_primary,
        marital_status=kin.marital_status,
    )
    db.add(db_kin)
    db.commit()
    db.refresh(db_kin)
    return db_kin
