#!/bin/bash
set -e

echo "🚀 Starting GradGen backend on Railway..."

# Run database migration with timeout
echo "📝 Running database migration..."
timeout 30 python migrate_business_model.py || {
    echo "⚠️  Migration failed or timed out (exit code: $?), but continuing..."
}

# Get port from environment or use default
PORT=${PORT:-8000}
echo "🌐 Starting server on port $PORT..."

# Start FastAPI application with verbose output
echo "🔍 Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info
