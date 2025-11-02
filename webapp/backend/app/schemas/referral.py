from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class ReferralStats(BaseModel):
    """Referral statistics for a user"""
    referral_code: Optional[str]
    total_referrals: int
    completed_referrals: int
    pending_referrals: int
    discount_eligible: bool
    referrals_needed: int
    referrals_remaining: int


class ReferralLinkResponse(BaseModel):
    """Referral link response"""
    referral_code: str
    referral_link: str
    stats: ReferralStats


class ReferralCreate(BaseModel):
    """Track a new referral"""
    referral_code: str
    referred_email: Optional[EmailStr] = None


class ReferralInfo(BaseModel):
    """Information about a single referral"""
    email: Optional[str]
    status: str
    created_at: Optional[datetime]
    completed_at: Optional[datetime]


class ReferralListResponse(BaseModel):
    """List of referrals"""
    referrals: List[ReferralInfo]
    total_count: int
