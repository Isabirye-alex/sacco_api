"""
Multi-tenancy layer.

Hierarchy:  Organisation (top-level SACCO body)
                └── Branch  (village / ward office)
"""

import uuid

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.models.base_file import Base, TimestampMixin


class Organisation(TimestampMixin, Base):
    """
    Top-level SACCO entity.  Every other record is scoped to an Organisation.
    One deployment can host multiple independent SACCOs (e.g. different
    village groups sharing the same platform).
    """

    __tablename__ = "organisations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    short_code = Column(String(20), nullable=False, unique=True)  # e.g. "KBSACCO"
    registration_no = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(Text, nullable=True)
    logo_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # settings
    default_currency = Column(String(10), default="UGX", nullable=False)
    min_share_value = Column(Numeric(18, 4), default=1000, nullable=False)
    loan_interest_rate = Column(
        Numeric(5, 2), default=18.00, nullable=False
    )  # annual %
    savings_interest_rate = Column(
        Numeric(5, 2), default=8.00, nullable=False
    )  # annual %

    # relationships
    branches = relationship("Branch", back_populates="organisation", lazy="select")


class Branch(TimestampMixin, Base):
    """
    A physical or logical branch / village group within an Organisation.
    Members, accounts, and loans are ultimately owned by a Branch.
    """

    __tablename__ = "branches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True
    )
    branch_name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=False)  # unique within org
    location = Column(String(255), nullable=True)
    manager_name = Column(String(255), nullable=True)
    branch_phone = Column(String(30), nullable=True)
    branch_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # relationships
    organisation = relationship("Organisation", back_populates="branches")
    members = relationship("Member", back_populates="branch", lazy="dynamic")
