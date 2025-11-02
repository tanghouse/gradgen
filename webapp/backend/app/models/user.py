from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth-only users
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    credits = Column(Integer, default=0)  # Deprecated - keeping for backward compatibility

    # New business model fields
    has_used_free_tier = Column(Boolean, default=False)  # True after generating 5 free photos
    has_purchased_premium = Column(Boolean, default=False)  # True after buying £19.99/£39.99
    referral_discount_eligible = Column(Boolean, default=False)  # True after 3 successful referrals
    referral_code = Column(String, unique=True, index=True, nullable=True)  # User's personal referral code

    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)

    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'google', 'microsoft', etc.
    oauth_id = Column(String, nullable=True)  # Provider's user ID

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    credit_transactions = relationship("CreditTransaction", back_populates="user")
    generation_jobs = relationship("GenerationJob", back_populates="user")
    payments = relationship("Payment", back_populates="user")
