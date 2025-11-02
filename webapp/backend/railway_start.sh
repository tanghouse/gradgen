#!/bin/bash
set -e

echo "🚀 Starting GradGen backend on Railway..."

# Run database migration
echo "📝 Running database migration..."
python migrate_business_model.py

# Get port from environment or use default
PORT=${PORT:-8000}
echo "🌐 Starting server on port $PORT..."

# Start FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
