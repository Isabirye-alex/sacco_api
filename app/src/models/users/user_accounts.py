from app.src.config.base_file import Base
from sqlalchemy import Column, String, TEXT, UUID, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

import uuid


class UserAccounts(Base):

    __tablename__ = "user_accounts"
    user_account_id = Column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    user_id = Column(
        UUID, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    account_id = Column(UUID, ForeignKey("accounts.account_id", ondelete="CASCADE"))
    user_account_created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    user_account_updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    user = relationship(
        "UserModel", lazy="joined", uselist=False, back_populates="user_account"
    )
