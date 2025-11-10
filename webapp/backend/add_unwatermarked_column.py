"""
Add output_image_path_unwatermarked column to generated_images table.

This migration adds a new column to store non-watermarked versions of images,
allowing premium users to access watermark-free versions of photos that were
originally generated during their free tier.

Run with: poetry run python add_unwatermarked_column.py
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
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='generated_images'
                AND column_name='output_image_path_unwatermarked'
            """))

            if result.fetchone():
                print("✅ Column 'output_image_path_unwatermarked' already exists")
                return True

            # Add the new column
            print("Adding column 'output_image_path_unwatermarked'...")
            conn.execute(text("""
                ALTER TABLE generated_images
                ADD COLUMN output_image_path_unwatermarked VARCHAR
            """))
            conn.commit()

            print("✅ Successfully added column 'output_image_path_unwatermarked'")
            return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
