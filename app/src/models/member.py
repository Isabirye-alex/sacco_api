"""
Members & Auth
==============
Member      – the person who belongs to a SACCO branch
User        – login credentials / roles (1-to-1 with Member for regular members;
              staff accounts may exist without a Member record)
Role        – e.g. MEMBER, BRANCH_MANAGER, TREASURER, ADMIN, SUPER_ADMIN
NextOfKin   – emergency contacts / beneficiaries
"""

import enum
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Date,
    Enum as SAEnum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.config.base_file import Base, TimestampMixin

# ─── Enumerations ────────────────────────────────────────────────────────────


class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNSPECIFIED = "UNSPECIFIED"


class MemberStatusEnum(str, enum.Enum):
    PENDING = "PENDING"  # application submitted, not yet approved
    ACTIVE = "ACTIVE"
    DORMANT = "DORMANT"  # no activity for > 6 months
    SUSPENDED = "SUSPENDED"
    EXITED = "EXITED"  # withdrew from SACCO


class RoleEnum(str, enum.Enum):
    MEMBER = "MEMBER"
    LOAN_OFFICER = "LOAN_OFFICER"
    TREASURER = "TREASURER"
    BRANCH_MANAGER = "BRANCH_MANAGER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


# ─── Models ──────────────────────────────────────────────────────────────────


class Member(TimestampMixin, Base):
    """
    A registered SACCO member. Belongs to exactly one Branch (and therefore
    one Organisation).  A member may also have a User account for portal access.
    """

    __tablename__ = "members"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    branch_id = Column(
        UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True
    )

    # identity
    member_no = Column(String(50), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    gender = Column(SAEnum(GenderEnum), default=GenderEnum.UNSPECIFIED, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    national_id = Column(String(50), nullable=True)  # NIN / passport
    photo_url = Column(String(512), nullable=True)

    # contact
    phone_primary = Column(String(30), nullable=True)
    phone_secondary = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    country = Column(Text, nullable=True)
    village = Column(String(255), nullable=True)
    district = Column(String(255), nullable=True)

    # membership
    status = Column(
        SAEnum(MemberStatusEnum), default=MemberStatusEnum.PENDING, nullable=False
    )
    joined_date = Column(Date, nullable=True)
    exit_date = Column(Date, nullable=True)
    exit_reason = Column(Text, nullable=True)

    # relationships
    organisation = relationship("Organisation", back_populates="members")
    branch = relationship("Branch", back_populates="members")
    user = relationship("User", back_populates="member", uselist=False)
    next_of_kin = relationship("NextOfKin", back_populates="member", lazy="dynamic")
    savings_accounts = relationship(
        "SavingsAccount", back_populates="member", lazy="dynamic"
    )
    share_accounts = relationship(
        "ShareAccount", back_populates="member", lazy="dynamic"
    )
    loans = relationship("Loan", back_populates="member", lazy="dynamic")

    __table_args__ = (
        UniqueConstraint("organisation_id", "member_no", name="uq_member_no_per_org"),
    )

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)


class User(TimestampMixin, Base):
    """
    Login account.  Can be linked to a Member (member portal login) or
    exist independently (staff / admin accounts).
    """

    __tablename__ = "users"

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    member_id = Column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=True, unique=True
    )

    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(RoleEnum), default=RoleEnum.MEMBER, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(String(50), nullable=True)  # ISO timestamp string

    # relationships
    member = relationship("Member", back_populates="user")

    __table_args__ = (
        UniqueConstraint("organisation_id", "email", name="uq_user_email_per_org"),
    )


class NextOfKin(TimestampMixin, Base):
    """Emergency contacts and/or loan guarantors / beneficiaries."""

    __tablename__ = "next_of_kin"

    member_id = Column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    full_name = Column(String(255), nullable=False)
    # relationship = Column(String(100), nullable=True)   # e.g. "Spouse", "Child"
    phone = Column(String(30), nullable=True)
    national_id = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)  # primary beneficiary

    member = relationship("Member", back_populates="next_of_kin")
