"""
Database migrations - runs automatically on startup
"""
from sqlalchemy import text, create_engine
from app.db.database import engine
import os


def run_migrations():
    """Run database migrations for email verification and OAuth support."""

    # Create engine with shorter timeout for Railway
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        migration_engine = create_engine(
            DATABASE_URL,
            connect_args={
                "connect_timeout": 10,
                "options": "-c statement_timeout=30000"  # 30 second query timeout
            }
        )
    else:
        migration_engine = engine

    migration_sql = """
    -- Add new columns to users table (if they don't exist)
    DO $$
    BEGIN
        -- Add email_verified column
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='users' AND column_name='email_verified'
        ) THEN
            ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
        END IF;

        -- Add email_verified_at column
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='users' AND column_name='email_verified_at'
        ) THEN
            ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP WITH TIME ZONE;
        END IF;

        -- Add oauth_provider column
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='users' AND column_name='oauth_provider'
        ) THEN
            ALTER TABLE users ADD COLUMN oauth_provider VARCHAR;
        END IF;

        -- Add oauth_id column
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='users' AND column_name='oauth_id'
        ) THEN
            ALTER TABLE users ADD COLUMN oauth_id VARCHAR;
        END IF;

        -- Add last_login_at column
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='users' AND column_name='last_login_at'
        ) THEN
            ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP WITH TIME ZONE;
        END IF;
    END $$;

    -- Make hashed_password nullable (for OAuth-only users)
    ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;

    -- Create email verification tokens table
    CREATE TABLE IF NOT EXISTS email_verification_tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        token VARCHAR UNIQUE NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        used BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_email_verification_token ON email_verification_tokens(token);
    CREATE INDEX IF NOT EXISTS idx_email_verification_user_id ON email_verification_tokens(user_id);

    -- Mark all existing users as verified (so they can still login)
    UPDATE users
    SET email_verified = TRUE,
        email_verified_at = NOW()
    WHERE email_verified IS FALSE OR email_verified IS NULL;
    """

    try:
        print("📡 Connecting to database for email/OAuth migration...", flush=True)
        with migration_engine.connect() as connection:
            print("🔄 Executing migration SQL...", flush=True)
            # Execute migration
            connection.execute(text(migration_sql))
            connection.commit()
            print("✅ Database migration completed successfully!", flush=True)
            return True
    except Exception as e:
        print(f"⚠️  Migration error (may already be applied): {e}", flush=True)
        return False
