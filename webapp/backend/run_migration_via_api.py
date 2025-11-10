"""
Run database migration via API endpoint.
This script logs in as a superuser and calls the migration endpoint.
"""

import requests
import sys

# Configuration
API_BASE = "https://gradgen-production.up.railway.app/api"

def run_migration(email: str, password: str):
    """Run the migration via API."""
    print(f"🔐 Logging in as {email}...")

    # Login
    login_response = requests.post(
        f"{API_BASE}/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False

    token = login_response.json()["access_token"]
    print("✅ Logged in successfully")

    # Run migration
    print("\n🔧 Running migration...")
    migration_response = requests.post(
        f"{API_BASE}/generation/admin/run-migration",
        headers={"Authorization": f"Bearer {token}"}
    )

    if migration_response.status_code != 200:
        print(f"❌ Migration failed: {migration_response.text}")
        return False

    result = migration_response.json()
    print(f"✅ {result['message']}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_migration_via_api.py <email> <password>")
        print("Example: python run_migration_via_api.py admin@gradgen.ai admin123")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    success = run_migration(email, password)
    sys.exit(0 if success else 1)
