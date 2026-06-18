import uuid

from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.config.base_file import Base


class LoginLogs(Base):
    """Login audit trail. member_id references users.member_id (members.id)."""

    __tablename__ = "login_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True, nullable=False)
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.member_id", ondelete="CASCADE"),
        nullable=True,
    )
    login_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    ip_address = Column(String(30), nullable=True)
    user_agent = Column(String(250), nullable=True)
    status = Column(String(20), nullable=True, default="success")
    failure_reason = Column(String(30), nullable=True)
    attempts = Column(Integer, nullable=False, default=1, server_default="1")
    session_id = Column(String(30), nullable=True)
    location_country = Column(String(50), nullable=True)
    location_city = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted = Column(Boolean, nullable=False, default=False, server_default="false")

    user = relationship(
        "User",
        foreign_keys=[member_id],
        primaryjoin="LoginLogs.member_id == User.member_id",
        lazy="select",
    )
