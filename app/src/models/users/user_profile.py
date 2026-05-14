from app.src.config.base_file import Base
from sqlalchemy import Column, ForeignKey, String, TEXT, DateTime, UUID, func
import uuid
from sqlalchemy.orm import relationship


class UserProfile(Base):

    __tablename__ = "profile"

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE') ,nullable=False, unique=True)
    member_id = Column(String(50), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False, unique=True)
    date_of_birth = Column(String(15), nullable=False)
    id_number = Column(String(20), nullable=True, unique=True)
    occupation = Column(String(50), nullable=False)
    monthly_income = Column(String(50), nullable=False)
    marital_status = Column(String(50), nullable=False, default="single")
    employer_name = Column(String(50), nullable=True)
    primary_language = Column(String(50), nullable=False, default="English")
    user_avatar = Column(TEXT, nullable=True)
    profile_created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    profile_updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    user = relationship('UserModel', lazy='joined', back_populates='profile')
