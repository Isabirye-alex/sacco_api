from app.src.config.base_file import Base
from sqlalchemy import Column, String, TEXT, UUID, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

import uuid
class TransactionModel(Base):

    __tablename__ = 'transactions'
    txn_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    transaction_id = Column(String(100), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user = relationship('UserModel', lazy='joined', uselist=False, back_populates='transaction')
