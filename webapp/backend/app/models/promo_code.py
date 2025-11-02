from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.db.database import Base


class PromoCode(Base):
    """Promo codes for discounts (e.g., marketing campaigns)"""
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)  # e.g., "LAUNCH2025"
    discount_amount = Column(Float, nullable=False)  # e.g., 20.00 for £20 off
    discount_type = Column(String, default="fixed")  # "fixed" or "percentage"

    # Usage limits
    max_uses = Column(Integer, nullable=True)  # None = unlimited
    current_uses = Column(Integer, default=0)

    # Validity period
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)  # None = no expiry

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    description = Column(String, nullable=True)  # Internal note
    created_by = Column(String, nullable=True)  # Admin who created it
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def is_valid(self) -> bool:
        """Check if promo code is currently valid"""
        from datetime import datetime, timezone as tz

        if not self.is_active:
            return False

        # Check usage limit
        if self.max_uses is not None and self.current_uses >= self.max_uses:
            return False

        # Check validity period
        now = datetime.now(tz.utc)
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False

        return True

    def calculate_discount(self, original_price: float) -> float:
        """Calculate discount amount based on type"""
        if self.discount_type == "percentage":
            return original_price * (self.discount_amount / 100)
        else:  # fixed
            return self.discount_amount
