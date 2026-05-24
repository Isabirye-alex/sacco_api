from sqlalchemy import Column, String, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.src.models.base_file import Base, TimestampMixin


class MobileMoneyTransaction(TimestampMixin, Base):
    """Records of mobile money transactions."""

    __tablename__ = "mobile_money_transactions"

    phone_number = Column(String(20), nullable=False)
    amount = Column(Numeric(18, 4), nullable=False)
    transaction_type = Column(
        String(50), nullable=False
    )  # DEPOSIT, WITHDRAWAL, LOAN_PAYMENT
    status = Column(
        String(50), default="PENDING", nullable=False
    )  # PENDING, SUCCESS, FAILED
    reference = Column(String(100), nullable=False)
    transaction_id = Column(
        String(100), nullable=True
    )  # External transaction ID from provider
    provider_response = Column(Text, nullable=True)

    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
