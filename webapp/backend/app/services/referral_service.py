"""
Referral service for managing referral codes and tracking
"""

import secrets
import string
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.referral import Referral, ReferralStatus
from app.models.user import User
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class ReferralService:
    """Service for managing referrals"""

    # Configuration
    REFERRAL_CODE_LENGTH = 8
    REQUIRED_REFERRALS_FOR_DISCOUNT = 3

    @classmethod
    def generate_referral_code(cls) -> str:
        """
        Generate a unique referral code (8 characters, alphanumeric)
        Format: XXXX-XXXX for readability
        """
        # Use uppercase letters and digits only
        alphabet = string.ascii_uppercase + string.digits
        # Avoid confusing characters (0, O, I, 1, etc.)
        alphabet = alphabet.replace('0', '').replace('O', '').replace('I', '').replace('1', '')

        # Generate two 4-character segments
        segment1 = ''.join(secrets.choice(alphabet) for _ in range(4))
        segment2 = ''.join(secrets.choice(alphabet) for _ in range(4))

        return f"{segment1}{segment2}"

    @classmethod
    def get_or_create_user_referral_code(cls, db: Session, user: User) -> str:
        """
        Get user's referral code or create one if they don't have one

        Args:
            db: Database session
            user: User object

        Returns:
            Referral code string
        """
        if user.referral_code:
            return user.referral_code

        # Generate unique code
        max_attempts = 10
        for _ in range(max_attempts):
            code = cls.generate_referral_code()

            # Check if code already exists
            existing = db.query(User).filter(User.referral_code == code).first()
            if not existing:
                user.referral_code = code
                db.commit()
                logger.info(f"Generated referral code {code} for user {user.id}")
                return code

        raise ValueError("Failed to generate unique referral code")

    @classmethod
    def track_referral(
        cls,
        db: Session,
        referral_code: str,
        referred_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Referral]:
        """
        Track a referral signup

        Args:
            db: Database session
            referral_code: The referral code used
            referred_email: Email of person signing up
            ip_address: IP address for fraud detection
            user_agent: User agent for fraud detection

        Returns:
            Referral object or None if referrer not found
        """
        # Find referrer by code
        referrer = db.query(User).filter(User.referral_code == referral_code).first()

        if not referrer:
            logger.warning(f"Referral code not found: {referral_code}")
            return None

        # Check if this email was already referred by this user
        if referred_email:
            existing = db.query(Referral).filter(
                Referral.referrer_id == referrer.id,
                Referral.referred_email == referred_email
            ).first()

            if existing:
                logger.warning(f"Duplicate referral attempt: {referred_email} by user {referrer.id}")
                return existing

        # Create referral record
        referral = Referral(
            referrer_id=referrer.id,
            referral_code=referral_code,
            referred_email=referred_email,
            ip_address=ip_address,
            user_agent=user_agent,
            status=ReferralStatus.PENDING
        )

        db.add(referral)
        db.commit()
        db.refresh(referral)

        logger.info(f"Tracked referral: {referral_code} -> {referred_email}")
        return referral

    @classmethod
    def complete_referral(
        cls,
        db: Session,
        referred_user: User,
        referral_code: str
    ) -> bool:
        """
        Mark a referral as completed when the referred user verifies their email

        Args:
            db: Database session
            referred_user: The user who just verified their email
            referral_code: The referral code they used

        Returns:
            True if referral completed successfully
        """
        # Find the pending referral
        referral = db.query(Referral).filter(
            Referral.referral_code == referral_code,
            Referral.referred_email == referred_user.email,
            Referral.status == ReferralStatus.PENDING
        ).first()

        if not referral:
            logger.warning(f"No pending referral found for {referred_user.email} with code {referral_code}")
            return False

        # Update referral
        referral.referred_user_id = referred_user.id
        referral.status = ReferralStatus.COMPLETED
        referral.completed_at = func.now()

        db.commit()

        # Check if referrer now has 3 completed referrals
        cls.check_and_apply_referral_discount(db, referral.referrer_id)

        logger.info(f"Completed referral for user {referred_user.id} from referrer {referral.referrer_id}")
        return True

    @classmethod
    def check_and_apply_referral_discount(cls, db: Session, user_id: int) -> bool:
        """
        Check if user has 3 completed referrals and make them eligible for discount

        Args:
            db: Database session
            user_id: Referrer user ID

        Returns:
            True if user is now eligible for discount
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        # If already eligible, no need to check again
        if user.referral_discount_eligible:
            return True

        # Count completed referrals
        completed_count = db.query(Referral).filter(
            Referral.referrer_id == user_id,
            Referral.status == ReferralStatus.COMPLETED
        ).count()

        if completed_count >= cls.REQUIRED_REFERRALS_FOR_DISCOUNT:
            user.referral_discount_eligible = True
            db.commit()

            logger.info(f"User {user_id} is now eligible for referral discount ({completed_count} referrals)")
            return True

        return False

    @classmethod
    def get_referral_stats(cls, db: Session, user_id: int) -> Dict:
        """
        Get referral statistics for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with referral stats
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return {
                "referral_code": None,
                "total_referrals": 0,
                "completed_referrals": 0,
                "pending_referrals": 0,
                "discount_eligible": False,
                "referrals_needed": cls.REQUIRED_REFERRALS_FOR_DISCOUNT
            }

        # Count referrals by status
        total = db.query(Referral).filter(Referral.referrer_id == user_id).count()

        completed = db.query(Referral).filter(
            Referral.referrer_id == user_id,
            Referral.status == ReferralStatus.COMPLETED
        ).count()

        pending = db.query(Referral).filter(
            Referral.referrer_id == user_id,
            Referral.status == ReferralStatus.PENDING
        ).count()

        return {
            "referral_code": user.referral_code,
            "total_referrals": total,
            "completed_referrals": completed,
            "pending_referrals": pending,
            "discount_eligible": user.referral_discount_eligible,
            "referrals_needed": cls.REQUIRED_REFERRALS_FOR_DISCOUNT,
            "referrals_remaining": max(0, cls.REQUIRED_REFERRALS_FOR_DISCOUNT - completed)
        }

    @classmethod
    def get_referral_link(cls, db: Session, user: User, frontend_url: str) -> str:
        """
        Get the user's referral link

        Args:
            db: Database session
            user: User object
            frontend_url: Frontend base URL

        Returns:
            Full referral URL
        """
        code = cls.get_or_create_user_referral_code(db, user)
        return f"{frontend_url}/register?ref={code}"

    @classmethod
    def get_referred_users(cls, db: Session, user_id: int) -> List[Dict]:
        """
        Get list of users referred by this user

        Args:
            db: Database session
            user_id: Referrer user ID

        Returns:
            List of referral dictionaries
        """
        referrals = db.query(Referral).filter(
            Referral.referrer_id == user_id
        ).order_by(Referral.created_at.desc()).all()

        return [
            {
                "email": ref.referred_email,
                "status": ref.status.value,
                "created_at": ref.created_at.isoformat() if ref.created_at else None,
                "completed_at": ref.completed_at.isoformat() if ref.completed_at else None
            }
            for ref in referrals
        ]
