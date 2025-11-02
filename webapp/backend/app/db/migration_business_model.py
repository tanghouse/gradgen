"""
Database migration for new business model
Run this after updating the models to add new tables and columns
"""

from sqlalchemy import create_engine, text
from app.core.config import get_settings

settings = get_settings()


def run_migration():
    """Apply database schema changes for new business model"""
    engine = create_engine(str(settings.DATABASE_URL))

    with engine.connect() as conn:
        print("Starting business model migration...")

        # 1. Add new columns to users table
        print("  - Adding new columns to users table...")
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS has_used_free_tier BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS has_purchased_premium BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS referral_discount_eligible BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS referral_code VARCHAR UNIQUE;
            """))
            conn.commit()
            print("    ✓ Users table updated")
        except Exception as e:
            print(f"    ⚠️  Users table may already have these columns: {e}")
            conn.rollback()

        # 2. Add new columns to payments table
        print("  - Adding new columns to payments table...")
        try:
            conn.execute(text("""
                ALTER TABLE payments
                ADD COLUMN IF NOT EXISTS original_price FLOAT,
                ADD COLUMN IF NOT EXISTS discount_applied FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS discount_source VARCHAR,
                ADD COLUMN IF NOT EXISTS promo_code_used VARCHAR,
                ADD COLUMN IF NOT EXISTS generation_job_id INTEGER REFERENCES generation_jobs(id);
            """))
            conn.execute(text("""
                UPDATE payments SET currency = 'gbp' WHERE currency = 'usd';
            """))
            conn.commit()
            print("    ✓ Payments table updated")
        except Exception as e:
            print(f"    ⚠️  Payments table may already have these columns: {e}")
            conn.rollback()

        # 3. Add new columns to generation_jobs table
        print("  - Adding new columns to generation_jobs table...")
        try:
            conn.execute(text("""
                ALTER TABLE generation_jobs
                ADD COLUMN IF NOT EXISTS tier VARCHAR DEFAULT 'free',
                ADD COLUMN IF NOT EXISTS is_watermarked BOOLEAN DEFAULT TRUE,
                ADD COLUMN IF NOT EXISTS prompts_used TEXT,
                ADD COLUMN IF NOT EXISTS payment_id INTEGER REFERENCES payments(id);
            """))
            conn.commit()
            print("    ✓ Generation jobs table updated")
        except Exception as e:
            print(f"    ⚠️  Generation jobs table may already have these columns: {e}")
            conn.rollback()

        # 4. Create promo_codes table
        print("  - Creating promo_codes table...")
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
            print("    ✓ Promo codes table created")
        except Exception as e:
            print(f"    ⚠️  Promo codes table may already exist: {e}")
            conn.rollback()

        # 5. Create referrals table
        print("  - Creating referrals table...")
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
            print("    ✓ Referrals table created")
        except Exception as e:
            print(f"    ⚠️  Referrals table may already exist: {e}")
            conn.rollback()

        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Generate referral codes for existing users")
        print("  2. Create initial promo codes (if needed)")
        print("  3. Test the new generation flow")


if __name__ == "__main__":
    run_migration()
