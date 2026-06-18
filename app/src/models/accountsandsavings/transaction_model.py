import uuid

from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.src.config.base_file import Base


class TransactionModel(Base):
  __tablename__ = "transactions"

  txn_id = Column(
    UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
  )
  member_id = Column(
    UUID(as_uuid=True),
    ForeignKey("users.member_id", ondelete="CASCADE"),
    nullable=False,
  )
  transaction_id = Column(String(100), nullable=False)
  transaction_date = Column(
    DateTime(timezone=True), nullable=False, server_default=func.now()
  )

  user = relationship(
    "User",
    foreign_keys=[member_id],
    primaryjoin="TransactionModel.member_id == User.member_id",
    lazy="joined",
    uselist=False,
  )
