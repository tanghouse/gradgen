from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ReferralStatus(str, enum.Enum):
    PENDING = "pending"  # Referred user registered but not verified
    COMPLETED = "completed"  # Referred user completed verification
    REWARDED = "rewarded"  # Referrer received discount


class Referral(Base):
    """Track referrals for 'refer 3 friends' discount"""
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)

    # Referrer (the user who sent the referral)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Referred user (the friend who signed up)
    referred_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null until signup

    # Referral tracking
    referral_code = Column(String, unique=True, index=True, nullable=False)  # e.g., "ABC123XYZ"
    status = Column(Enum(ReferralStatus), default=ReferralStatus.PENDING)

    # Metadata
    referred_email = Column(String, nullable=True)  # Email used during invite
    ip_address = Column(String, nullable=True)  # For fraud detection
    user_agent = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)  # When referred user verified
    rewarded_at = Column(DateTime(timezone=True), nullable=True)  # When discount applied

    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id], backref="referrals_sent")
    referred_user = relationship("User", foreign_keys=[referred_user_id], backref="referred_by")
