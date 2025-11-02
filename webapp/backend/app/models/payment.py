from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_payment_intent_id = Column(String, unique=True, index=True)
    amount = Column(Float, nullable=False)  # in GBP (£19.99 or £39.99)
    credits = Column(Integer, nullable=False)  # Deprecated - keeping for backward compatibility
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    currency = Column(String, default="gbp")  # Changed from usd to gbp

    # New business model fields
    original_price = Column(Float, nullable=True)  # £39.99 (before discount)
    discount_applied = Column(Float, default=0.0)  # £20.00 if discounted
    discount_source = Column(String, nullable=True)  # "referral" or "promo_code"
    promo_code_used = Column(String, nullable=True)  # Code that was applied
    generation_job_id = Column(Integer, ForeignKey("generation_jobs.id"), nullable=True)  # Linked job

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="payments")
