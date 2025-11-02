from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.referral import (
    ReferralStats,
    ReferralLinkResponse,
    ReferralListResponse
)
from app.services.referral_service import ReferralService
from app.core.config import settings

router = APIRouter()


@router.get("/stats", response_model=ReferralStats)
def get_referral_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's referral statistics

    Returns:
    - referral_code: User's unique referral code
    - total_referrals: Total number of referrals
    - completed_referrals: Number of verified referrals
    - pending_referrals: Number of pending referrals
    - discount_eligible: Whether user has earned the discount
    - referrals_needed: Total needed for discount (3)
    - referrals_remaining: How many more needed
    """
    stats = ReferralService.get_referral_stats(db, current_user.id)
    return stats


@router.get("/link", response_model=ReferralLinkResponse)
def get_referral_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's referral link and stats

    Returns:
    - referral_code: User's code
    - referral_link: Full shareable link
    - stats: Referral statistics
    """
    # Get or create referral code
    code = ReferralService.get_or_create_user_referral_code(db, current_user)

    # Get full link
    link = ReferralService.get_referral_link(db, current_user, settings.FRONTEND_URL)

    # Get stats
    stats = ReferralService.get_referral_stats(db, current_user.id)

    return {
        "referral_code": code,
        "referral_link": link,
        "stats": stats
    }


@router.get("/list", response_model=ReferralListResponse)
def list_my_referrals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of people referred by current user

    Returns list of referrals with status and dates
    """
    referrals = ReferralService.get_referred_users(db, current_user.id)

    return {
        "referrals": referrals,
        "total_count": len(referrals)
    }


@router.post("/track")
def track_referral(
    referral_code: str,
    referred_email: str = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Track a referral when someone clicks a referral link
    Called during registration process

    Args:
    - referral_code: The code from the URL
    - referred_email: Email of person signing up (optional)
    """
    # Get IP and user agent for fraud detection
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None

    referral = ReferralService.track_referral(
        db=db,
        referral_code=referral_code,
        referred_email=referred_email,
        ip_address=ip_address,
        user_agent=user_agent
    )

    if not referral:
        raise HTTPException(
            status_code=404,
            detail="Referral code not found"
        )

    return {
        "message": "Referral tracked successfully",
        "referral_code": referral_code
    }


@router.get("/check-eligibility")
def check_discount_eligibility(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user is eligible for referral discount

    Returns:
    - eligible: Boolean
    - completed_referrals: Number of completed referrals
    - required: Number required (3)
    """
    stats = ReferralService.get_referral_stats(db, current_user.id)

    return {
        "eligible": stats["discount_eligible"],
        "completed_referrals": stats["completed_referrals"],
        "required": stats["referrals_needed"],
        "remaining": stats["referrals_remaining"]
    }
