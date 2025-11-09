"""
Admin endpoints for testing and account management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.generation import GenerationJob
from app.api.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


class ResetAccountResponse(BaseModel):
    message: str
    email: str
    previous_state: dict
    new_state: dict
    generation_history: dict


@router.post("/reset-account", response_model=ResetAccountResponse)
def reset_account_for_testing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset current user's tier flags for testing purposes.
    Preserves generation history but resets:
    - has_used_free_tier to FALSE
    - has_purchased_premium to FALSE
    - premium_generations_used to 0
    - referral_discount_eligible to FALSE
    """

    # Capture previous state
    previous_state = {
        "has_used_free_tier": current_user.has_used_free_tier,
        "has_purchased_premium": current_user.has_purchased_premium,
        "premium_generations_used": current_user.premium_generations_used,
        "referral_discount_eligible": current_user.referral_discount_eligible,
    }

    # Reset tier flags
    current_user.has_used_free_tier = False
    current_user.has_purchased_premium = False
    current_user.premium_generations_used = 0
    current_user.referral_discount_eligible = False

    db.commit()
    db.refresh(current_user)

    # Get new state
    new_state = {
        "has_used_free_tier": current_user.has_used_free_tier,
        "has_purchased_premium": current_user.has_purchased_premium,
        "premium_generations_used": current_user.premium_generations_used,
        "referral_discount_eligible": current_user.referral_discount_eligible,
    }

    # Get generation history
    free_jobs = db.query(GenerationJob).filter(
        GenerationJob.user_id == current_user.id,
        GenerationJob.tier == 'free'
    ).count()

    premium_jobs = db.query(GenerationJob).filter(
        GenerationJob.user_id == current_user.id,
        GenerationJob.tier == 'premium'
    ).count()

    total_jobs = db.query(GenerationJob).filter(
        GenerationJob.user_id == current_user.id
    ).count()

    generation_history = {
        "total_jobs": total_jobs,
        "free_tier_jobs": free_jobs,
        "premium_tier_jobs": premium_jobs,
    }

    return ResetAccountResponse(
        message="Account successfully reset for testing. All tier flags cleared.",
        email=current_user.email,
        previous_state=previous_state,
        new_state=new_state,
        generation_history=generation_history,
    )
