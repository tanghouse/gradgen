#!/bin/bash
# Railway startup script that runs migration then starts the app

echo "🚀 Starting GradGen with migration..."

# Run migration
python migrate_business_model.py

# Check if migration succeeded
if [ $? -ne 0 ]; then
    echo "❌ Migration failed, exiting..."
    exit 1
fi

echo "✅ Migration complete, starting app..."

# Start the FastAPI app
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
