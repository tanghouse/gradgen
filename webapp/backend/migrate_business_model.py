"""
Standalone database migration for new business model
Run this with: python migrate_business_model.py
"""

import os
import sys
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment or Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    print("\nPlease set it first:")
    print("  export DATABASE_URL='your_database_url'")
    print("\nOr run on Railway where it's already set.")
    sys.exit(1)

def run_migration():
    """Apply database schema changes for new business model"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("🚀 Starting business model migration...\n")

        # 1. Add new columns to users table
        print("📝 Step 1: Updating users table...")
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS has_used_free_tier BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS has_purchased_premium BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS referral_discount_eligible BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS referral_code VARCHAR UNIQUE;
            """))
            conn.commit()
            print("   ✅ Users table updated\n")
        except Exception as e:
            print(f"   ⚠️  Users table error (may already have columns): {e}\n")
            conn.rollback()

        # 2. Add new columns to payments table
        print("📝 Step 2: Updating payments table...")
        try:
            conn.execute(text("""
                ALTER TABLE payments
                ADD COLUMN IF NOT EXISTS original_price FLOAT,
                ADD COLUMN IF NOT EXISTS discount_applied FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS discount_source VARCHAR,
                ADD COLUMN IF NOT EXISTS promo_code_used VARCHAR,
                ADD COLUMN IF NOT EXISTS generation_job_id INTEGER;
            """))
            # Add foreign key constraint if it doesn't exist
            try:
                conn.execute(text("""
                    ALTER TABLE payments
                    ADD CONSTRAINT fk_payments_generation_job
                    FOREIGN KEY (generation_job_id) REFERENCES generation_jobs(id);
                """))
            except:
                pass  # Constraint may already exist

            # Update currency
            conn.execute(text("""
                UPDATE payments SET currency = 'gbp' WHERE currency = 'usd';
            """))
            conn.commit()
            print("   ✅ Payments table updated\n")
        except Exception as e:
            print(f"   ⚠️  Payments table error (may already have columns): {e}\n")
            conn.rollback()

        # 3. Add new columns to generation_jobs table
        print("📝 Step 3: Updating generation_jobs table...")
        try:
            conn.execute(text("""
                ALTER TABLE generation_jobs
                ADD COLUMN IF NOT EXISTS tier VARCHAR DEFAULT 'free',
                ADD COLUMN IF NOT EXISTS is_watermarked BOOLEAN DEFAULT TRUE,
                ADD COLUMN IF NOT EXISTS prompts_used TEXT,
                ADD COLUMN IF NOT EXISTS payment_id INTEGER;
            """))
            # Add foreign key constraint
            try:
                conn.execute(text("""
                    ALTER TABLE generation_jobs
                    ADD CONSTRAINT fk_generation_jobs_payment
                    FOREIGN KEY (payment_id) REFERENCES payments(id);
                """))
            except:
                pass  # Constraint may already exist
            conn.commit()
            print("   ✅ Generation jobs table updated\n")
        except Exception as e:
            print(f"   ⚠️  Generation jobs table error (may already have columns): {e}\n")
            conn.rollback()

        # 4. Create promo_codes table
        print("📝 Step 4: Creating promo_codes table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS promo_codes (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR UNIQUE NOT NULL,
                    discount_amount FLOAT NOT NULL,
                    discount_type VARCHAR DEFAULT 'fixed',
                    max_uses INTEGER,
                    current_uses INTEGER DEFAULT 0,
                    valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    valid_until TIMESTAMP WITH TIME ZONE,
                    is_active BOOLEAN DEFAULT TRUE,
                    description VARCHAR,
                    created_by VARCHAR,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                );
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_promo_codes_code ON promo_codes(code);
            """))
            conn.commit()
            print("   ✅ Promo codes table created\n")
        except Exception as e:
            print(f"   ⚠️  Promo codes table error (may already exist): {e}\n")
            conn.rollback()

        # 5. Create referrals table
        print("📝 Step 5: Creating referrals table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id SERIAL PRIMARY KEY,
                    referrer_id INTEGER NOT NULL REFERENCES users(id),
                    referred_user_id INTEGER REFERENCES users(id),
                    referral_code VARCHAR UNIQUE NOT NULL,
                    status VARCHAR DEFAULT 'pending',
                    referred_email VARCHAR,
                    ip_address VARCHAR,
                    user_agent VARCHAR,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP WITH TIME ZONE,
                    rewarded_at TIMESTAMP WITH TIME ZONE
                );
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);
                CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referral_code);
            """))
            conn.commit()
            print("   ✅ Referrals table created\n")
        except Exception as e:
            print(f"   ⚠️  Referrals table error (may already exist): {e}\n")
            conn.rollback()

        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("  1. Generate referral codes for existing users")
        print("  2. Create initial promo codes (if needed)")
        print("  3. Test the new generation flow")
        print("  4. Update frontend to use new business model\n")


if __name__ == "__main__":
    run_migration()
