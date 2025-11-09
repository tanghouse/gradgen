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
    print("❌ ERROR: DATABASE_URL environment variable not set", flush=True)
    print("\nPlease set it first:", flush=True)
    print("  export DATABASE_URL='your_database_url'", flush=True)
    print("\nOr run on Railway where it's already set.", flush=True)
    sys.exit(1)

print(f"📡 Connecting to database...", flush=True)
print(f"   Database URL: {DATABASE_URL[:20]}...{DATABASE_URL[-20:]}", flush=True)

def run_migration():
    """Apply database schema changes for new business model"""
    try:
        engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})
        print("✅ Database engine created", flush=True)
    except Exception as e:
        print(f"❌ Failed to create database engine: {e}", flush=True)
        sys.exit(1)

    try:
        conn = engine.connect()
        print("✅ Database connection established", flush=True)
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}", flush=True)
        sys.exit(1)

    with conn:
        print("🚀 Starting business model migration...\n", flush=True)

        # 1. Add new columns to users table
        print("📝 Step 1: Updating users table...", flush=True)
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS has_used_free_tier BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS has_purchased_premium BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS premium_generations_used INTEGER DEFAULT 0,
                ADD COLUMN IF NOT EXISTS referral_discount_eligible BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS referral_code VARCHAR UNIQUE;
            """))
            conn.commit()
            print("   ✅ Users table updated\n", flush=True)
        except Exception as e:
            print(f"   ⚠️  Users table error (may already have columns): {e}\n", flush=True)
            conn.rollback()

        # 2. Add new columns to payments table
        print("📝 Step 2: Updating payments table...", flush=True)
        try:
            conn.execute(text("""
                ALTER TABLE payments
                ADD COLUMN IF NOT EXISTS original_price FLOAT,
                ADD COLUMN IF NOT EXISTS discount_applied FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS discount_source VARCHAR,
                ADD COLUMN IF NOT EXISTS promo_code_used VARCHAR,
                ADD COLUMN IF NOT EXISTS generation_job_id INTEGER;
            """))
            conn.commit()
            print("   ✅ Payments table columns added\n", flush=True)
        except Exception as e:
            print(f"   ⚠️  Payments table columns error (may already exist): {e}\n", flush=True)
            conn.rollback()

        # Add foreign key constraint (separate transaction)
        try:
            # Check if constraint exists first
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_payments_generation_job'
                AND table_name = 'payments';
            """))
            constraint_exists = result.scalar() > 0

            if not constraint_exists:
                conn.execute(text("""
                    ALTER TABLE payments
                    ADD CONSTRAINT fk_payments_generation_job
                    FOREIGN KEY (generation_job_id) REFERENCES generation_jobs(id);
                """))
                conn.commit()
                print("   ✅ Payments foreign key added\n", flush=True)
            else:
                print("   ℹ️  Payments foreign key already exists, skipping\n", flush=True)
        except Exception as e:
            print(f"   ⚠️  Payments FK error: {e}\n", flush=True)
            conn.rollback()

        # Update currency (separate transaction)
        try:
            conn.execute(text("""
                UPDATE payments SET currency = 'gbp' WHERE currency = 'usd';
            """))
            conn.commit()
            print("   ✅ Currency updated to GBP\n", flush=True)
        except Exception as e:
            print(f"   ⚠️  Currency update error: {e}\n", flush=True)
            conn.rollback()

        # 3. Add new columns to generation_jobs table
        print("📝 Step 3: Updating generation_jobs table...", flush=True)
        try:
            conn.execute(text("""
                ALTER TABLE generation_jobs
                ADD COLUMN IF NOT EXISTS tier VARCHAR DEFAULT 'free',
                ADD COLUMN IF NOT EXISTS is_watermarked BOOLEAN DEFAULT TRUE,
                ADD COLUMN IF NOT EXISTS prompts_used TEXT,
                ADD COLUMN IF NOT EXISTS payment_id INTEGER;
            """))
            conn.commit()
            print("   ✅ Generation jobs table columns added\n", flush=True)
        except Exception as e:
            print(f"   ⚠️  Generation jobs table columns error (may already exist): {e}\n", flush=True)
            conn.rollback()

        # Add foreign key constraint (separate transaction)
        try:
            # Check if constraint exists first
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_generation_jobs_payment'
                AND table_name = 'generation_jobs';
            """))
            constraint_exists = result.scalar() > 0

            if not constraint_exists:
                conn.execute(text("""
                    ALTER TABLE generation_jobs
                    ADD CONSTRAINT fk_generation_jobs_payment
                    FOREIGN KEY (payment_id) REFERENCES payments(id);
                """))
                conn.commit()
                print("   ✅ Generation jobs foreign key added\n", flush=True)
            else:
                print("   ℹ️  Generation jobs foreign key already exists, skipping\n", flush=True)
        except Exception as e:
            print(f"   ⚠️  Generation jobs FK error: {e}\n", flush=True)
            conn.rollback()

        # 4. Create promo_codes table
        print("📝 Step 4: Creating promo_codes table...", flush=True)
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
            print("   ✅ Promo codes table created\n", flush=True)
        except Exception as e:
            print(f"   ⚠️  Promo codes table error (may already exist): {e}\n", flush=True)
            conn.rollback()

        # 5. Create referrals table
        print("📝 Step 5: Creating referrals table...", flush=True)
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
            print("   ✅ Referrals table created\n", flush=True)
        except Exception as e:
            print(f"   ⚠️  Referrals table error (may already exist): {e}\n", flush=True)
            conn.rollback()

        print("\n✅ Migration completed successfully!", flush=True)
        print("\n📋 Next steps:", flush=True)
        print("  1. Generate referral codes for existing users", flush=True)
        print("  2. Create initial promo codes (if needed)", flush=True)
        print("  3. Test the new generation flow", flush=True)
        print("  4. Update frontend to use new business model\n", flush=True)


if __name__ == "__main__":
    run_migration()
