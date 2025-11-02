"""
Comprehensive test account manager.
Interactive CLI for managing test accounts during development.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User
from app.models.generation import GenerationJob, GeneratedImage
from app.services.referral_service import ReferralService
from app.services.storage_service import storage_service

try:
    from app.core.security import get_password_hash
    use_app_hash = True
except ImportError:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    use_app_hash = False


def get_db():
    """Get database session."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not set")
        print("\nFor Railway, run: railway run python manage_test_accounts.py")
        print("For local, set DATABASE_URL environment variable")
        return None

    engine = create_engine(DATABASE_URL)
    return Session(engine)


def list_test_accounts(db):
    """List all test accounts."""
    users = db.query(User).filter(User.is_superuser == True).all()

    if not users:
        print("\n📋 No test accounts found!")
        return

    print("\n📋 Test Accounts:")
    print("=" * 100)

    for user in users:
        job_count = db.query(GenerationJob).filter(GenerationJob.user_id == user.id).count()
        tier = "Premium" if user.has_purchased_premium else "Free (used)" if user.has_used_free_tier else "Free (unused)"

        print(f"\n📧 {user.email}")
        print(f"   Name: {user.full_name}")
        print(f"   ID: {user.id}")
        print(f"   Tier: {tier}")
        print(f"   Jobs: {job_count}")
        print(f"   Verified: {'✅' if user.email_verified else '❌'}")
        print(f"   Referral Code: {user.referral_code or 'None'}")


def create_test_account(db, tier: str):
    """Create a new test account."""
    print(f"\n🆕 Creating new {tier.upper()} test account...")

    # Generate unique email
    base_email = f"{tier}_test@gradgen.ai"
    counter = 1
    email = base_email

    while db.query(User).filter(User.email == email).first():
        email = f"{tier}_test{counter}@gradgen.ai"
        counter += 1

    password = f"{tier}123"
    full_name = f"{tier.capitalize()} Test User"

    # Hash password
    password_safe = password[:72]
    try:
        if use_app_hash:
            hashed_password = get_password_hash(password_safe)
        else:
            hashed_password = pwd_context.hash(password_safe)
    except Exception as e:
        import bcrypt
        password_bytes = password_safe.encode('utf-8')[:72]
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

    # Create user
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True,
        email_verified=True,
        credits=0,
        has_used_free_tier=(tier == 'premium'),  # Premium = free tier used
        has_purchased_premium=(tier == 'premium'),
        referral_discount_eligible=False
    )

    db.add(user)
    db.flush()

    # Generate referral code
    try:
        ReferralService.get_or_create_user_referral_code(db, user)
    except Exception as e:
        print(f"⚠️  Could not generate referral code: {e}")

    db.commit()
    db.refresh(user)

    print(f"\n✅ Account created!")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   Tier: {tier.upper()}")


def reset_account(db, email: str):
    """Reset account data."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ User {email} not found!")
        return

    print(f"\n🗑️  Resetting {email}...")

    # Delete all jobs and images
    jobs = db.query(GenerationJob).filter(GenerationJob.user_id == user.id).all()

    deleted_files = 0
    for job in jobs:
        images = db.query(GeneratedImage).filter(GeneratedImage.job_id == job.id).all()

        for image in images:
            # Delete files from storage
            for path in [image.input_image_path, image.output_image_path]:
                if path:
                    try:
                        storage_service.delete_file(path)
                        deleted_files += 1
                    except:
                        pass

            db.delete(image)

        db.delete(job)

    # Reset tier
    user.has_used_free_tier = False
    user.has_purchased_premium = False
    user.referral_discount_eligible = False

    db.commit()

    print(f"   ✅ Deleted {len(jobs)} jobs and {deleted_files} files")
    print(f"   ✅ Reset to Free (unused) tier")


def toggle_tier(db, email: str):
    """Toggle account tier."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ User {email} not found!")
        return

    current = "Premium" if user.has_purchased_premium else "Free"
    new_tier = "Free" if user.has_purchased_premium else "Premium"

    print(f"\n🔄 Toggling {email} from {current} to {new_tier}...")

    if new_tier == "Premium":
        user.has_purchased_premium = True
        user.has_used_free_tier = True
    else:
        user.has_purchased_premium = False

    db.commit()
    print(f"   ✅ Now {new_tier} tier")


def delete_account(db, email: str):
    """Delete test account completely."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ User {email} not found!")
        return

    print(f"\n⚠️  WARNING: Deleting {email} permanently!")
    print("   This will delete:")
    print("   - User account")
    print("   - All generation jobs")
    print("   - All uploaded/generated files")
    print("\n   Type 'DELETE' to confirm:")

    confirm = input("   > ")
    if confirm != "DELETE":
        print("   ❌ Cancelled")
        return

    # Delete all jobs and images
    jobs = db.query(GenerationJob).filter(GenerationJob.user_id == user.id).all()

    for job in jobs:
        images = db.query(GeneratedImage).filter(GeneratedImage.job_id == job.id).all()

        for image in images:
            for path in [image.input_image_path, image.output_image_path]:
                if path:
                    try:
                        storage_service.delete_file(path)
                    except:
                        pass

            db.delete(image)

        db.delete(job)

    # Delete user
    db.delete(user)
    db.commit()

    print(f"   ✅ Account deleted")


def main_menu():
    """Interactive menu."""
    db = get_db()
    if not db:
        return

    while True:
        print("\n" + "=" * 100)
        print("🧪 GradGen Test Account Manager")
        print("=" * 100)
        print("\n1. List all test accounts")
        print("2. Create new free tier account")
        print("3. Create new premium tier account")
        print("4. Reset account (clear data, reset to free tier)")
        print("5. Toggle account tier (free ↔ premium)")
        print("6. Delete account")
        print("7. Exit")

        choice = input("\nSelect option (1-7): ").strip()

        try:
            if choice == "1":
                list_test_accounts(db)

            elif choice == "2":
                create_test_account(db, "free")

            elif choice == "3":
                create_test_account(db, "premium")

            elif choice == "4":
                email = input("\nEnter email to reset: ").strip()
                reset_account(db, email)

            elif choice == "5":
                email = input("\nEnter email to toggle: ").strip()
                toggle_tier(db, email)

            elif choice == "6":
                email = input("\nEnter email to delete: ").strip()
                delete_account(db, email)

            elif choice == "7":
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid option")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            db.rollback()

    db.close()


if __name__ == "__main__":
    # Check for command-line arguments for non-interactive mode
    if len(sys.argv) > 1:
        command = sys.argv[1]
        db = get_db()

        if not db:
            sys.exit(1)

        try:
            if command == "list":
                list_test_accounts(db)

            elif command == "create" and len(sys.argv) > 2:
                tier = sys.argv[2]
                if tier in ['free', 'premium']:
                    create_test_account(db, tier)
                else:
                    print("❌ Invalid tier. Use 'free' or 'premium'")

            elif command == "reset" and len(sys.argv) > 2:
                email = sys.argv[2]
                reset_account(db, email)

            elif command == "toggle" and len(sys.argv) > 2:
                email = sys.argv[2]
                toggle_tier(db, email)

            else:
                print("❌ Usage:")
                print("  python manage_test_accounts.py                    # Interactive mode")
                print("  python manage_test_accounts.py list               # List accounts")
                print("  python manage_test_accounts.py create [free|premium]")
                print("  python manage_test_accounts.py reset <email>")
                print("  python manage_test_accounts.py toggle <email>")

        finally:
            db.close()
    else:
        # Interactive mode
        main_menu()
