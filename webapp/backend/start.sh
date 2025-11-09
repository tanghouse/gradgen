#!/bin/bash
set -e

echo "🚀 Starting GradGen backend on Railway..."

# TEMPORARILY SKIP MIGRATION to test if app can start
echo "⚠️  SKIPPING migration temporarily for diagnostics..."
# timeout 30 python migrate_business_model.py || {
#     echo "⚠️  Migration failed or timed out (exit code: $?), but continuing..."
# }

# Get port from environment or use default
PORT=${PORT:-8000}
echo "🌐 Starting server on port $PORT..."

# Start FastAPI application with verbose output
echo "🔍 Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
