from app.src.models.base_file import Base, TimestampMixin
from sqlalchemy import Column, Integer, TEXT, DateTime, String, UUID, ForeignKey, func
from sqlalchemy.orm import relationship
import uuid


class LoginLogs(TimestampMixin,Base):
    __tablename__ = "login_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
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

    user = relationship("User", lazy="select")
