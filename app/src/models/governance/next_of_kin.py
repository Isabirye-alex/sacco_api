from sqlalchemy.orm import relationship
from sqlalchemy import Column, TEXT, String, DateTime, func, UUID, ForeignKey
from app.src.config.base_file import Base
import uuid

class NextOfKin(Base):

    __tablename__ = 'next_of_kin'

    nxt_id = Column(UUID(as_uuid=True), primary_key=True ,nullable=False, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    