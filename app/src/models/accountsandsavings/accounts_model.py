from app.src.config.base_file import Base
from sqlalchemy import Column, String, TEXT, UUID, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

import uuid


class AccountsModel(Base):

    __tablename__ = "accounts"
    account_id = Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    account_name = Column(UUID(as_uuid=True), unique=True, nullable=False)
    account_status = Column(String(50), nullable=True, default="Coming soon")
    account_created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    account_updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
