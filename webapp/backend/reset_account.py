"""
Reset account data for testing purposes.
Clears all generation jobs, images, and resets tier status.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import User, GenerationJob, GeneratedImage, Payment
from app.services.storage_service import storage_service


def reset_account(email: str):
    """
    Reset an account's generation data and tier status.

    This will:
    - Delete all generation jobs and images
    - Delete uploaded files from storage (R2/local)
    - Delete generated results from storage
    - Reset has_used_free_tier to False
    - Reset has_purchased_premium to False
    - Keep the account active and verified
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not set")
        print("\nFor Railway, run: railway run python reset_account.py user@email.com")
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
        print(f"   Current status:")
        print(f"   - Free tier used: {user.has_used_free_tier}")
        print(f"   - Premium purchased: {user.has_purchased_premium}")
        print(f"   - Jobs: {len(user.generation_jobs) if user.generation_jobs else 0}")

        # Get all jobs and images for this user
        jobs = db.query(GenerationJob).filter(GenerationJob.user_id == user.id).all()

        print(f"\n🗑️  Deleting {len(jobs)} jobs...")

        deleted_files = 0
        failed_files = 0

        for job in jobs:
            # Get all images for this job
            images = db.query(GeneratedImage).filter(GeneratedImage.job_id == job.id).all()

            for image in images:
                # Delete input image from storage
                if image.input_image_path:
                    try:
                        storage_service.delete_file(image.input_image_path)
                        deleted_files += 1
                    except Exception as e:
                        print(f"   ⚠️  Failed to delete {image.input_image_path}: {e}")
                        failed_files += 1

                # Delete output image from storage
                if image.output_image_path:
                    try:
                        storage_service.delete_file(image.output_image_path)
                        deleted_files += 1
                    except Exception as e:
                        print(f"   ⚠️  Failed to delete {image.output_image_path}: {e}")
                        failed_files += 1

                # Delete image record
                db.delete(image)

            # Delete job record
            db.delete(job)

        print(f"   ✅ Deleted {deleted_files} files from storage")
        if failed_files > 0:
            print(f"   ⚠️  Failed to delete {failed_files} files (may not exist)")

        # Reset tier status
        user.has_used_free_tier = False
        user.has_purchased_premium = False
        user.referral_discount_eligible = False

        db.commit()

        print(f"\n🎉 Account reset successfully!")
        print(f"\n📊 Updated status:")
        print(f"   - Free tier used: {user.has_used_free_tier} ✅")
        print(f"   - Premium purchased: {user.has_purchased_premium} ✅")
        print(f"   - Jobs: 0 ✅")
        print(f"\n💡 You can now:")
        print(f"   1. Login with {email}")
        print(f"   2. Test free tier again (5 watermarked photos)")
        print(f"   3. Test upgrade flow")
        print(f"   4. Generate premium photos after payment")

    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting account: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python reset_account.py <email>")
        print("\nExample:")
        print("  python reset_account.py admin@gradgen.ai")
        print("  railway run python reset_account.py admin@gradgen.ai")
        sys.exit(1)

    email = sys.argv[1]

    print(f"⚠️  WARNING: This will delete ALL generation data for {email}")
    print("   Press Ctrl+C to cancel, or Enter to continue...")

    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(0)

    reset_account(email)
