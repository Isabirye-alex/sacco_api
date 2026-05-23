from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.models.base_file import Base, TimestampMixin

USER_TYPE_MEMBER = "MEMBER"
USER_TYPE_STAFF = "STAFF"


class UserType(TimestampMixin, Base):
    __tablename__ = "user_types"

    code = Column(String(50), primary_key=True, unique=True)
    description = Column(Text, nullable=True)

    users = relationship(
        "User",
        back_populates="user_type_obj",
        lazy="select",
        foreign_keys="User.user_type",
    )


class Gender(TimestampMixin, Base):
    """
    Admin-managed gender lookup.
    Seeded with: Male, Female, Other, Prefer not to say.
    Admins can add entries without a code change.
    """

    __tablename__ = "genders"

    gender = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    members = relationship("Member", back_populates="gender", lazy="select")


class MemberStatus(TimestampMixin, Base):
    """
    Admin-managed member account state lookup.
    Seeded with: Pending, Active, Dormant, Suspended, Exited.
    """

    __tablename__ = "member_statuses"

    status = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    members = relationship("Member", back_populates="status", lazy="select")


class MaritalStatus(TimestampMixin, Base):
    """
    Admin-managed marital status lookup.
    Seeded with: Single, Married, Widowed, Divorced, Separated.
    """

    __tablename__ = "marital_statuses"

    status = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    members = relationship("Member", back_populates="marital_status", lazy="select")
    next_of_kin = relationship(
        "NextOfKin", back_populates="marital_status", lazy="select"
    )


class Role(TimestampMixin, Base):
    """
    Seeded role lookup. Admins can add custom roles; system roles are
    protected (is_system=True) and cannot be deleted or renamed.

    System roles
    ------------
    MEMBER           regular member portal access
    LOAN_OFFICER     can review and process loan applications
    TREASURER        full access to savings, shares, ledger
    BRANCH_MANAGER   manages one branch; all operations within it
    ADMIN            organisation-wide admin
    SUPER_ADMIN      platform-level; can manage multiple organisations
    """

    __tablename__ = "roles"

    role = Column(String(100), nullable=False, unique=True)
    description = Column(String(250), nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)  # protected seed rows

    # one Role → many Users
    users = relationship("User", back_populates="role", lazy="select")


class User(TimestampMixin, Base):
    """
    Login account for both members and staff.

    Differentiation
    ---------------
    user_type = MEMBER → linked to a Member record via member_id (1-to-1)
    user_type = STAFF  → member_id is NULL; role drives permissions

    Always check user_type before role:
        if user.user_type == USER_TYPE_STAFF and user.role.role == "TREASURER":
            ...
    """

    __tablename__ = "users"

    role_name = Column(
        String(15), ForeignKey("roles.role", ondelete="RESTRICT"), nullable=True, default='MEMBER', unique=True
    )

    user_type = Column(
        String(50),
        ForeignKey("user_types.code"),
        nullable=False,
        default=USER_TYPE_MEMBER,
    )
    user_type_obj = relationship(
        "UserType",
        back_populates="users",
        uselist=False,
        lazy="joined",
        foreign_keys=[user_type],
    )

    # NULL for STAFF users; populated and unique for MEMBER users
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    )

    # credentials & contact
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # relationships
    # one User → one Role  (uselist=False — FK is on User side, each user has one role)
    role = relationship("Role", back_populates="users", uselist=False, lazy="joined")
    # one User → one Member at most  (NULL for staff)
    member = relationship("Member", back_populates="user", uselist=False, lazy="select")

    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email_per_org"),
    )

    # convenience helpers (used in FastAPI dependencies)
    @property
    def is_member_user(self) -> bool:
        """True when this account belongs to a regular SACCO member."""
        return self.user_type == USER_TYPE_MEMBER

    @property
    def is_staff_user(self) -> bool:
        """True when this account belongs to SACCO staff."""
        return self.user_type == USER_TYPE_STAFF

    def has_role(self, *roles: str) -> bool:
        """
        Check whether this user holds any of the given role names.

        Usage:
            user.has_role("TREASURER")
            user.has_role("ADMIN", "SUPER_ADMIN")
        """
        return self.role is not None and self.role.role in roles

    def is_admin_or_above(self) -> bool:
        return self.has_role("ADMIN", "SUPER_ADMIN")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Member(TimestampMixin, Base):
    """
    A registered SACCO member.

    Every Member has exactly one User account (the portal login).
    Creation order: create User (user_type=MEMBER) → create Member →
    set User.member_id = member.id.

    Lookup FK pattern
    -----------------
    gender_id, status_id, marital_status_id all point to admin-managed
    lookup tables instead of hardcoded enums, so admins can extend them
    without migrations.
    """

    __tablename__ = "members"

    
    branch_id = Column(
        UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True
    )

    # lookup FKs — admin-managed, not hardcoded enums
    gender_id = Column(UUID(as_uuid=True), ForeignKey("genders.id"), nullable=False)
    status_id = Column(
        UUID(as_uuid=True), ForeignKey("member_statuses.id"), nullable=True
    )
    marital_status_id = Column(
        UUID(as_uuid=True), ForeignKey("marital_statuses.id"), nullable=True
    )

    # identity
    member_no = Column(String(50), nullable=False, index=True, unique=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    national_id = Column(String(50), nullable=False)
    photo_url = Column(String(512), nullable=True)

    # contact
    email = Column(String(255), nullable=True)
    phone_primary = Column(String(30), nullable=True, unique=True)
    phone_secondary = Column(String(30), nullable=True)
    country = Column(String(100), nullable=True)
    village = Column(String(255), nullable=True)
    district = Column(String(255), nullable=True)
    physical_address = Column(Text, nullable=True)

    # membership lifecycle
    joined_date = Column(Date, nullable=True)
    exit_date = Column(Date, nullable=True)
    exit_reason = Column(Text, nullable=True)

    # relationships
    branch = relationship(
        "Branch", back_populates="members", lazy="joined", uselist=False
    )
    gender = relationship(
        "Gender", back_populates="members", lazy="joined", uselist=False
    )
    status = relationship(
        "MemberStatus", back_populates="members", lazy="joined", uselist=False
    )
    marital_status = relationship(
        "MaritalStatus", back_populates="members", lazy="joined", uselist=False
    )
    user = relationship("User", back_populates="member", lazy="select", uselist=False)
    next_of_kin = relationship("NextOfKin", back_populates="member", lazy="select")

    savings_accounts = relationship(
        "SavingsAccount", back_populates="member", lazy="select"
    )
    share_accounts = relationship(
        "ShareAccount", back_populates="member", lazy="select"
    )
    loans = relationship("Loan", back_populates="member", lazy="select")

    __table_args__ = (
        UniqueConstraint( "member_no", name="uq_member_no_per_org"),
    )


class NextOfKin(TimestampMixin, Base):
    """Emergency contacts and / or beneficiaries attached to a Member."""

    __tablename__ = "next_of_kin"

    member_id = Column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    marital_status_id = Column(
        UUID(as_uuid=True), ForeignKey("marital_statuses.id"), nullable=True
    )

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)
    national_id = Column(String(50), nullable=True)
    relationship_to_member = Column(
        String(100), nullable=True
    )  # e.g. "Spouse", "Child"
    address = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    member = relationship("Member", back_populates="next_of_kin", uselist=False)
    marital_status = relationship(
        "MaritalStatus", back_populates="next_of_kin", uselist=False, lazy="joined"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
