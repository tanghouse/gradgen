#!/bin/bash
# Railway Migration Script
# This script can be run as a one-off command in Railway

echo "🚀 Starting GradGen Business Model Migration..."
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set"
    echo "This script must be run in Railway environment where DATABASE_URL is available"
    exit 1
fi

echo "✅ DATABASE_URL found"
echo ""

# Run migration
cd /app/webapp/backend
python migrate_business_model.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Migration completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Generate referral codes for existing users (if any)"
    echo "  2. Test the new /api/generation/tier-status endpoint"
    echo "  3. Test the new /api/referrals/link endpoint"
    echo ""
else
    echo ""
    echo "❌ Migration failed. Check logs above for details."
    exit 1
fi
