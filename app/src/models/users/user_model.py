import uuid
from sqlalchemy import TEXT, UUID, Boolean, Column, DateTime, String, func
from sqlalchemy.orm import relationship
from app.src.config.base_file import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    is_verified = Column(Boolean, default=False)
    password = Column(TEXT, nullable=True, default="!google_sign_in")
    is_active = Column(Boolean, default=True)
    user_type = Column(String(50), default="Client")
    user_created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    user_updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    profile = relationship(
        "UserProfile", lazy="joined", back_populates="user", uselist=False
    )
    address = relationship(
        "UserAddress", lazy="joined", back_populates="user", uselist=False
    )
