"""
Pydantic schemas for payment API
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreatePremiumCheckoutRequest(BaseModel):
    """Request to create a premium tier checkout session"""
    promo_code: Optional[str] = Field(None, description="Optional promo code for discount")


class CheckoutSessionResponse(BaseModel):
    """Response containing Stripe checkout session details"""
    session_id: str
    session_url: str
    amount: float  # Final amount in GBP
    original_price: float  # £39.99
    discount_applied: float  # £0 or £20
    discount_source: Optional[str]  # "referral", "promo_code", or None


class PricingInfoResponse(BaseModel):
    """Response with pricing information for the user"""
    base_price: float = 39.99
    discounted_price: Optional[float] = None
    discount_available: bool
    discount_source: Optional[str]  # "referral" or "promo_code"
    referral_discount_eligible: bool
    referrals_completed: int
    referrals_needed: int


class PaymentStatusResponse(BaseModel):
    """Response with payment status"""
    payment_id: int
    status: str
    amount: float
    currency: str
    created_at: datetime
    generation_job_id: Optional[int]


class PromoCodeValidationRequest(BaseModel):
    """Request to validate a promo code"""
    promo_code: str = Field(..., min_length=1, max_length=50)


class PromoCodeValidationResponse(BaseModel):
    """Response with promo code validation result"""
    valid: bool
    discount_amount: Optional[float] = None
    discount_type: Optional[str] = None
    message: str
