#!/bin/bash
set -e

echo "🚀 Starting GradGen backend on Railway..."

# Run migrations before starting the app
# This runs outside of app import to avoid table locks
echo "📝 Running database migrations..."

# First, run the basic schema creation
timeout 30 python -c "
from app.db.database import Base, engine
import sys

print('🔧 Creating database tables...', flush=True)
try:
    Base.metadata.create_all(bind=engine)
    print('✅ Tables created', flush=True)
except Exception as e:
    print(f'⚠️  Table creation error: {e}', flush=True)
    sys.exit(1)
" || echo "⚠️  Table creation timed out or failed, continuing..."

# Then run email/OAuth migrations with timeout
timeout 30 python -c "
from app.db.migrations import run_migrations
import sys

print('🔧 Running email/OAuth migrations...', flush=True)
try:
    run_migrations()
    print('✅ Email/OAuth migrations complete', flush=True)
except Exception as e:
    print(f'⚠️  Migration error: {e}', flush=True)
" || echo "⚠️  Email/OAuth migrations timed out or failed, continuing..."

# Then run business model migration
echo "🔧 Running business model migration..."
timeout 60 python migrate_business_model.py || {
    echo "⚠️  Business model migration failed or timed out (exit code: $?), but continuing..."
}

# Get port from environment or use default
PORT=${PORT:-8000}
echo "🌐 Starting server on port $PORT..."

# Start FastAPI application
echo "🔍 Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info
