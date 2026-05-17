import uuid
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Boolean,
    Date,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.config.base_file import Base, TimestampMixin


import uuid
from sqlalchemy import Column, String, Text, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.src.config.base_file import Base, TimestampMixin


class Gender(TimestampMixin, Base):
    """Dynamic lookup table for genders managed by Admins."""

    __tablename__ = "genders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gender = Column(String(50), nullable=False, unique=True)  # e.g., "MALE", "FEMALE"
    description = Column(Text, nullable=True)

    members = relationship("Member", back_populates="gender")


class MemberStatus(TimestampMixin, Base):
    """Dynamic lookup table for member account states."""

    __tablename__ = "member_statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(
        String(50), nullable=False, unique=True
    )  # e.g., "ACTIVE", "DORMANT"
    description = Column(Text, nullable=True)

    members = relationship("Member", back_populates="status")


class UserType(TimestampMixin, Base):
    """Dynamic lookup table for system roles and permissions."""

    __tablename__ = "user_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_type = Column(
        String(50), nullable=False, unique=True
    )  # e.g., "LOAN_OFFICER", "ADMIN"
    description = Column(Text, nullable=True)

    users = relationship("User", back_populates="u_type", lazy="joined")


class MaritalStatus(TimestampMixin, Base):
    __tablename__ = "marital_status"
    id = Column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    status = Column(String(20), nullable=False, default="single")

    member = relationship("Member", uselist=False, back_populates="marriage_status")


class Roles(TimestampMixin, Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String(100), nullable=False, unique=True)
    description = Column(String(250), nullable=True)

    # user = relationship("User", back_populates="role", uselist=False, lazy="joined")


class UserBase:
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True, unique=True)


class Member(UserBase, TimestampMixin, Base):
    """A registered SACCO member linking to dynamic lookups."""

    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    branch_id = Column(
        UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True
    )

    gender_id = Column(UUID(as_uuid=True), ForeignKey("genders.id"), nullable=False)
    status_id = Column(
        UUID(as_uuid=True), ForeignKey("member_statuses.id"), nullable=False
    )

    # Identity & Contact
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    member_no = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    national_id = Column(String(50), nullable=True)
    marital_status = Column(UUID, ForeignKey("marital_status.id", ondelete="CASCADE"))
    photo_url = Column(String(512), nullable=True)
    phone_primary = Column(String(30), nullable=True, unique=True)
    phone_secondary = Column(String(30), nullable=True, unique=True)
    email = Column(String(255), nullable=True)
    country = Column(Text, nullable=True)
    village = Column(String(255), nullable=True)
    district = Column(String(255), nullable=True)
    joined_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    exit_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
    exit_reason = Column(Text, nullable=True)

    # Lookup Relationships
    gender = relationship("Gender", back_populates="members")
    status = relationship("MemberStatus", back_populates="members")
    marriage_status = relationship(
        "MaritalStatus", uselist=False, back_populates="member", lazy="joined"
    )

    # Core Relationships
    user = relationship("User", lazy="joined", back_populates="member", uselist=False)
    next_of_kin = relationship(
        "NextOfKin", back_populates="member", lazy="joined", uselist=False
    )
    branch = relationship(
        "Branch", back_populates="members", lazy="joined", uselist=False
    )
    loans = relationship("Loan", back_populates="member")

    __table_args__ = (UniqueConstraint("member_no", name="uq_member_no_per_org"),)


class User(UserBase, TimestampMixin, Base):
    """Login account linking to a dynamic Role table."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    user_type = Column(UUID(as_uuid=True), ForeignKey("user_types.id"), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(String(50), nullable=True)

    # Lookup Relationship
    u_type = relationship("UserType", back_populates="users", lazy="joined")
    # role = relationship("Roles", back_populates="user", uselist=True, lazy="joined")

    # Core Relationship
    member = relationship("Member", back_populates="user", lazy="raise")

    __table_args__ = (UniqueConstraint("email", name="uq_user_email_per_org"),)


class NextOfKin(UserBase, TimestampMixin, Base):
    """Emergency contacts and/or loan guarantors / beneficiaries."""

    __tablename__ = "next_of_kin"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )

    member_relationship = Column(String(100), nullable=True)  # e.g. "Spouse", "Child"
    national_id = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)  # primary beneficiary
    marital_status = Column(
        UUID, ForeignKey("marital_status.id", ondelete="CASCADE"), nullable=False
    )

    member = relationship("Member", back_populates="next_of_kin", uselist=False)
