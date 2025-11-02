"""
Toggle account tier between free and premium for testing.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import User


def toggle_tier(email: str, target_tier: str = None):
    """
    Toggle account tier or set to specific tier.

    Args:
        email: User email
        target_tier: 'free', 'premium', or None for auto-toggle
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not set")
        print("\nFor Railway, run: railway run python toggle_tier.py user@email.com [free|premium]")
        print("For local, set DATABASE_URL environment variable")
        return

    engine = create_engine(DATABASE_URL)
    db = Session(engine)

    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User {email} not found!")
            return

        print(f"\n🔍 Found user: {user.full_name} ({user.email})")
        print(f"   Current tier: {'Premium' if user.has_purchased_premium else 'Free (used)' if user.has_used_free_tier else 'Free (unused)'}")

        # Determine target tier
        if target_tier:
            target_tier = target_tier.lower()
            if target_tier not in ['free', 'premium']:
                print(f"❌ Invalid tier: {target_tier}. Use 'free' or 'premium'")
                return
        else:
            # Auto-toggle
            if user.has_purchased_premium:
                target_tier = 'free'
            else:
                target_tier = 'premium'

        print(f"\n🔄 Changing tier to: {target_tier.upper()}")

        # Apply tier changes
        if target_tier == 'free':
            user.has_purchased_premium = False
            # Keep has_used_free_tier as-is (preserves test state)
            user.referral_discount_eligible = False
            new_tier = 'Free (used)' if user.has_used_free_tier else 'Free (unused)'

        elif target_tier == 'premium':
            user.has_purchased_premium = True
            user.has_used_free_tier = True  # Premium users have "used" free tier
            user.referral_discount_eligible = False
            new_tier = 'Premium'

        db.commit()

        print(f"\n✅ Tier updated successfully!")
        print(f"\n📊 New status:")
        print(f"   - Tier: {new_tier}")
        print(f"   - Free tier used: {user.has_used_free_tier}")
        print(f"   - Premium purchased: {user.has_purchased_premium}")
        print(f"\n💡 Next steps:")

        if target_tier == 'premium':
            print(f"   - Login and generate unlimited unwatermarked photos")
            print(f"   - Dashboard shows purple '👑 Premium Account' banner")
        else:
            if user.has_used_free_tier:
                print(f"   - Dashboard shows gray '🔒 Free Tier Used' banner")
                print(f"   - User will see pricing modal when trying to generate")
            else:
                print(f"   - Dashboard shows blue '🎁 Free Tier Available' banner")
                print(f"   - User can generate 5 free watermarked photos")

    except Exception as e:
        db.rollback()
        print(f"❌ Error toggling tier: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python toggle_tier.py <email> [free|premium]")
        print("\nExamples:")
        print("  python toggle_tier.py admin@gradgen.ai          # Auto-toggle")
        print("  python toggle_tier.py admin@gradgen.ai premium  # Set to premium")
        print("  python toggle_tier.py admin@gradgen.ai free     # Set to free")
        print("\nRailway:")
        print("  railway run python toggle_tier.py admin@gradgen.ai")
        sys.exit(1)

    email = sys.argv[1]
    target_tier = sys.argv[2] if len(sys.argv) > 2 else None

    toggle_tier(email, target_tier)
