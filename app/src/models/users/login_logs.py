from app.src.config.base_file import Base
from sqlalchemy import Column, TEXT, DateTime, String, UUID, ForeignKey, func
from sqlalchemy.orm import relationship
import uuid

class LoginLogs(Base):
    __tablename__ = 'login_logs'

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    login_at =  Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(30), nullable=True)
    user_agent = Column(String(50), nullable=True)
    status = Column(String(20), default='success')
    failure_reason = Column(String(30), default='Invalid password')
    session_id = Column(String(30), nullable=True)
    location_country = Column(String(50), nullable=True)
    location_city = Column(String(50), nullable=True)
    

    user = relationship('UserModel', lazy='select')

