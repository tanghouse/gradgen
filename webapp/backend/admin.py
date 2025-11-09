#!/usr/bin/env python3
"""
Standalone admin tool for managing GradGen accounts.
Works without Railway CLI - just needs DATABASE_URL.

Usage:
    export DATABASE_URL="postgresql://..."
    python admin.py list
    python admin.py reset admin@gradgen.ai
    python admin.py create free
    python admin.py toggle test@gradgen.ai
"""

import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime

# Minimal models (no dependencies on app config)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    oauth_provider = Column(String)
    oauth_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime)
    credits = Column(Integer, default=0)
    has_used_free_tier = Column(Boolean, default=False)
    has_purchased_premium = Column(Boolean, default=False)
    premium_generations_used = Column(Integer, default=0)
    referral_discount_eligible = Column(Boolean, default=False)
    referral_code = Column(String)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    job_type = Column(String, default="single")
    status = Column(String, default="pending")
    university = Column(String, nullable=False)
    degree_level = Column(String, nullable=False)
    prompt_id = Column(String, default="P2")
    total_images = Column(Integer, default=1)
    completed_images = Column(Integer, default=0)
    failed_images = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    tier = Column(String, default="free")
    is_watermarked = Column(Boolean, default=True)
    prompts_used = Column(Text)
    payment_id = Column(Integer)


def get_db():
    """Get database session."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not set")
        print("\nExport it first:")
        print('  export DATABASE_URL="postgresql://..."')
        return None

    engine = create_engine(DATABASE_URL)
    return Session(engine)


def list_accounts(db):
    """List all accounts."""
    users = db.query(User).all()

    if not users:
        print("\n📋 No accounts found!")
        return

    print("\n📋 All Accounts:")
    print("=" * 100)

    for user in users:
        job_count = db.query(GenerationJob).filter(GenerationJob.user_id == user.id).count()

        # Determine tier status
        premium_used = user.premium_generations_used or 0
        premium_remaining = max(0, 2 - premium_used) if user.has_purchased_premium else 0

        if user.has_purchased_premium and premium_remaining == 0:
            tier = "Premium (exhausted)"
        elif user.has_purchased_premium:
            tier = f"Premium ({premium_remaining}/2 remaining)"
        elif user.has_used_free_tier:
            tier = "Free (used)"
        else:
            tier = "Free (unused)"

        print(f"\n📧 {user.email}")
        print(f"   Name: {user.full_name or 'N/A'}")
        print(f"   ID: {user.id}")
        print(f"   Tier: {tier}")
        print(f"   Jobs: {job_count}")
        print(f"   Superuser: {'✅' if user.is_superuser else '❌'}")
        print(f"   Verified: {'✅' if user.email_verified else '❌'}")


def reset_account(db, email: str):
    """Reset account tier flags (keeps jobs for reference)."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ User {email} not found!")
        return

    print(f"\n🔄 Resetting {email} tier flags...")
    print(f"   Current: has_used_free_tier={user.has_used_free_tier}, "
          f"has_purchased_premium={user.has_purchased_premium}, "
          f"premium_generations_used={user.premium_generations_used or 0}")

    # Reset tier flags (KEEP jobs for reference)
    user.has_used_free_tier = False
    user.has_purchased_premium = False
    user.premium_generations_used = 0
    user.referral_discount_eligible = False

    db.commit()
    db.refresh(user)

    job_count = db.query(GenerationJob).filter(GenerationJob.user_id == user.id).count()

    print(f"   ✅ Reset to Free (unused) tier")
    print(f"   ℹ️  {job_count} generation jobs preserved for reference")
    print(f"\n💡 User can now test the complete flow from scratch!")


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
        user.premium_generations_used = 0  # Reset counter
    else:
        user.has_purchased_premium = False
        user.premium_generations_used = 0

    db.commit()
    print(f"   ✅ Now {new_tier} tier")


def main():
    if len(sys.argv) < 2:
        print("""
🧪 GradGen Admin Tool

Usage:
    python admin.py list                    # List all accounts
    python admin.py reset EMAIL             # Reset tier flags (keeps jobs)
    python admin.py toggle EMAIL            # Toggle free ↔ premium

Examples:
    python admin.py list
    python admin.py reset admin@gradgen.ai
    python admin.py toggle test@gradgen.ai

Environment:
    export DATABASE_URL="postgresql://user:pass@host:port/db"
        """)
        sys.exit(1)

    command = sys.argv[1]
    db = get_db()

    if not db:
        sys.exit(1)

    try:
        if command == "list":
            list_accounts(db)

        elif command == "reset" and len(sys.argv) > 2:
            email = sys.argv[2]
            reset_account(db, email)

        elif command == "toggle" and len(sys.argv) > 2:
            email = sys.argv[2]
            toggle_tier(db, email)

        else:
            print("❌ Invalid command or missing arguments")
            print("\nValid commands:")
            print("  list                    # List all accounts")
            print("  reset EMAIL             # Reset tier flags")
            print("  toggle EMAIL            # Toggle tier")

    except KeyboardInterrupt:
        print("\n\n👋 Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
