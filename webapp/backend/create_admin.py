"""
Create an admin/test account with all features enabled
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User
from app.services.referral_service import ReferralService

# Try to use the app's password hashing utilities
try:
    from app.core.security import get_password_hash
    use_app_hash = True
    print("✅ Using app's password hashing")
except ImportError:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    use_app_hash = False
    print("✅ Using passlib directly")

def create_admin_account(
    email: str = "admin@gradgen.ai",
    password: str = "admin123",
    full_name: str = "Admin User"
):
    """Create an admin account with all features enabled for testing"""

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not set")
        print("\nFor Railway, run: railway run python create_admin.py")
        print("For local, set DATABASE_URL environment variable")
        return

    engine = create_engine(DATABASE_URL)
    db = Session(engine)

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            print(f"✅ User {email} already exists!")
            print(f"   ID: {existing_user.id}")
            print(f"   Email Verified: {existing_user.email_verified}")
            print(f"   Is Superuser: {existing_user.is_superuser}")
            print(f"   Has Used Free Tier: {existing_user.has_used_free_tier}")
            print(f"   Has Purchased Premium: {existing_user.has_purchased_premium}")
            print(f"   Referral Code: {existing_user.referral_code}")

            # Update to admin if not already
            if not existing_user.is_superuser:
                existing_user.is_superuser = True
                db.commit()
                print("\n✨ Updated to superuser!")

            return existing_user

        # Create new admin user
        # Truncate password to 72 bytes for bcrypt (strict enforcement)
        password_bytes = password.encode('utf-8')
        print(f"📏 Password length: {len(password_bytes)} bytes")

        if len(password_bytes) > 72:
            print(f"⚠️  Password exceeds 72 bytes, truncating...")
            password_bytes = password_bytes[:72]
            password = password_bytes.decode('utf-8', errors='ignore')
            print(f"✂️  Truncated to: {len(password_bytes)} bytes")

        # Force password to be within bcrypt limits
        password = password[:72] if isinstance(password, str) else password_bytes[:72].decode('utf-8', errors='ignore')

        print(f"🔐 Hashing password...")
        try:
            if use_app_hash:
                hashed_password = get_password_hash(password)
            else:
                hashed_password = pwd_context.hash(password)
            print(f"✅ Password hashed successfully")
        except Exception as e:
            print(f"❌ Hash error: {e}")
            print(f"🔄 Trying alternative method...")
            # Manual bcrypt as last resort
            import bcrypt
            password_safe = password.encode('utf-8')[:72]
            hashed_password = bcrypt.hashpw(password_safe, bcrypt.gensalt()).decode('utf-8')
            print(f"✅ Password hashed with bcrypt directly")

        admin_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True,
            email_verified=True,  # Auto-verify for testing
            credits=1000,  # Give some credits (legacy)
            has_used_free_tier=False,  # Haven't used free tier yet
            has_purchased_premium=False,  # Haven't purchased premium
            referral_discount_eligible=False
        )

        db.add(admin_user)
        db.flush()

        # Generate referral code
        try:
            referral_code = ReferralService.get_or_create_user_referral_code(db, admin_user)
            print(f"✅ Generated referral code: {referral_code}")
        except Exception as e:
            print(f"⚠️  Could not generate referral code: {e}")

        db.commit()
        db.refresh(admin_user)

        print(f"\n🎉 Admin account created successfully!")
        print(f"\n📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"👤 User ID: {admin_user.id}")
        print(f"🎫 Referral Code: {admin_user.referral_code}")
        print(f"\n🔐 Account Details:")
        print(f"   - Superuser: ✅")
        print(f"   - Email Verified: ✅")
        print(f"   - Free Tier Available: ✅")
        print(f"   - Premium Tier: ❌ (test the upgrade flow!)")
        print(f"\n💡 You can now:")
        print(f"   1. Login with {email} / {password}")
        print(f"   2. Generate 5 free watermarked photos")
        print(f"   3. Test the premium upgrade flow")
        print(f"   4. Share referral code with test accounts")

        return admin_user

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin account: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Check for custom email/password from command line
    import sys

    email = sys.argv[1] if len(sys.argv) > 1 else "admin@gradgen.ai"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    full_name = sys.argv[3] if len(sys.argv) > 3 else "Admin User"

    print(f"🚀 Creating admin account for {email}...")
    create_admin_account(email, password, full_name)
