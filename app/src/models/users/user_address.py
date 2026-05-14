import uuid
from sqlalchemy.orm import relationship
from app.src.config.base_file import Base
from sqlalchemy import Column, DateTime, String, UUID, TEXT, ForeignKey, func


class UserAddress(Base):

    __tablename__ = "address"
    address_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    nationality = Column(String(30), nullable=False, default="Ugandan")
    district = Column(String(40), nullable=False)
    sub_county = Column(String(50), nullable=False)
    parish = Column(String(50), nullable=False)
    village = Column(String(50), nullable=False)
    postal_code = Column(String(50), nullable=True)
    address_created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    address_updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("UserModel", lazy="joined", back_populates="address")
