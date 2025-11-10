"""
Make success column nullable in generated_images table.

This allows us to distinguish between:
- None/NULL: Image is still processing
- True: Image generated successfully
- False: Image generation failed

Run with: poetry run python update_success_column.py
"""

import os
from sqlalchemy import create_engine, text

def run_migration():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not set")
        return False

    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            print("Making 'success' column nullable in generated_images table...")

            # PostgreSQL command to alter column to allow NULL
            conn.execute(text("""
                ALTER TABLE generated_images
                ALTER COLUMN success DROP NOT NULL
            """))
            conn.commit()

            print("✅ Successfully made 'success' column nullable")
            return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
