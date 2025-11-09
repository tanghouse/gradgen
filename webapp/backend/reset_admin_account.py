"""
Reset admin account for testing - clears all tier flags and generation history
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set", flush=True)
    sys.exit(1)

print(f"📡 Connecting to database...", flush=True)

def reset_account(email: str):
    """Reset account to fresh state"""
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
        # Find the user
        result = conn.execute(text("""
            SELECT id, email, has_used_free_tier, has_purchased_premium, premium_generations_used
            FROM users WHERE email = :email;
        """), {"email": email})
        
        user = result.fetchone()
        if not user:
            print(f"❌ User not found: {email}", flush=True)
            sys.exit(1)
        
        print(f"\n📊 Current Status for {user[1]}:", flush=True)
        print(f"   User ID: {user[0]}", flush=True)
        print(f"   has_used_free_tier: {user[2]}", flush=True)
        print(f"   has_purchased_premium: {user[3]}", flush=True)
        print(f"   premium_generations_used: {user[4]}", flush=True)
        
        # Reset all tier flags
        print(f"\n🔄 Resetting account to fresh state...", flush=True)
        conn.execute(text("""
            UPDATE users
            SET has_used_free_tier = FALSE,
                has_purchased_premium = FALSE,
                premium_generations_used = 0,
                referral_discount_eligible = FALSE
            WHERE email = :email;
        """), {"email": email})
        conn.commit()
        
        print(f"✅ Account reset successfully!", flush=True)
        
        # Show generation jobs count
        result = conn.execute(text("""
            SELECT COUNT(*), 
                   SUM(CASE WHEN tier = 'free' THEN 1 ELSE 0 END) as free_jobs,
                   SUM(CASE WHEN tier = 'premium' THEN 1 ELSE 0 END) as premium_jobs
            FROM generation_jobs WHERE user_id = :user_id;
        """), {"user_id": user[0]})
        
        jobs = result.fetchone()
        print(f"\n📈 Generation History:", flush=True)
        print(f"   Total Jobs: {jobs[0]}", flush=True)
        print(f"   Free Tier Jobs: {jobs[1]}", flush=True)
        print(f"   Premium Jobs: {jobs[2]}", flush=True)
        print(f"\n💡 Note: Generation history preserved for testing, but tier flags reset", flush=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reset_admin_account.py <email>", flush=True)
        sys.exit(1)
    
    reset_account(sys.argv[1])
