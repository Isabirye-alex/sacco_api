import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Date,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.config.base_file import Base, TimestampMixin


class Gender(TimestampMixin, Base):
    """Dynamic lookup table for genders managed by Admins."""

    __tablename__ = "genders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    members = relationship("Member", back_populates="gender")


class MemberStatus(TimestampMixin, Base):
    """Dynamic lookup table for member account states."""

    __tablename__ = "member_statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    members = relationship("Member", back_populates="status")


class Role(TimestampMixin, Base):
    """Dynamic lookup table for system roles and permissions."""

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", back_populates="role")


class Member(TimestampMixin, Base):
    """A registered SACCO member linking to dynamic lookups."""

    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    branch_id = Column(
        UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True
    )
    gender_id = Column(UUID(as_uuid=True), ForeignKey("genders.id"), nullable=False)
    status_id = Column(
        UUID(as_uuid=True), ForeignKey("member_statuses.id"), nullable=False
    )

    member_no = Column(String(50), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    national_id = Column(String(50), nullable=True)
    photo_url = Column(String(512), nullable=True)
    phone_primary = Column(String(30), nullable=True)
    phone_secondary = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    country = Column(Text, nullable=True)
    village = Column(String(255), nullable=True)
    district = Column(String(255), nullable=True)
    joined_date = Column(Date, nullable=True)
    exit_date = Column(Date, nullable=True)
    exit_reason = Column(Text, nullable=True)

    gender = relationship("Gender", back_populates="members")
    status = relationship("MemberStatus", back_populates="members")
    organisation = relationship("Organisation", back_populates="members")
    branch = relationship("Branch", back_populates="members")
    user = relationship("User", lazy="joined", back_populates="member", uselist=False)
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


class User(TimestampMixin, Base):
    """Login account linking to a dynamic Role table."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    member_id = Column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=True, unique=True
    )
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)

    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(String(50), nullable=True)

    role = relationship("Role", back_populates="users")
    member = relationship("Member", back_populates="user", lazy="joined")

    __table_args__ = (
        UniqueConstraint("organisation_id", "email", name="uq_user_email_per_org"),
    )


class NextOfKin(TimestampMixin, Base):
    """Emergency contacts and/or loan guarantors / beneficiaries."""

    __tablename__ = "next_of_kin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    full_name = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    national_id = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    member = relationship("Member", back_populates="next_of_kin")
