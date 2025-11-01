-- Database Migration for Email Verification and OAuth
-- Run this in your Railway PostgreSQL database

-- Step 1: Add new columns to users table (if they don't exist)
ALTER TABLE users
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR,
ADD COLUMN IF NOT EXISTS oauth_id VARCHAR,
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- Step 2: Make hashed_password nullable (for OAuth-only users)
ALTER TABLE users
ALTER COLUMN hashed_password DROP NOT NULL;

-- Step 3: Create email verification tokens table
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_email_verification_token ON email_verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_email_verification_user_id ON email_verification_tokens(user_id);

-- Step 5: IMPORTANT - Mark all existing users as verified (so they can still login)
UPDATE users
SET email_verified = TRUE,
    email_verified_at = NOW()
WHERE email_verified IS FALSE OR email_verified IS NULL;

-- Step 6: Verify the migration worked
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN ('email_verified', 'email_verified_at', 'oauth_provider', 'oauth_id', 'last_login_at', 'hashed_password')
ORDER BY column_name;

-- You should see all 6 columns listed above
