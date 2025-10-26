#!/usr/bin/env python3
"""
Script to create a new user with credits.
Usage: python scripts/create_user.py email@example.com "Full Name" password 100
"""
import sys
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_user(email: str, full_name: str, password: str, credits: int = 10):
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Error: User with email {email} already exists!")
            return
        
        # Create new user
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            credits=credits,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✓ User created successfully!")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.full_name}")
        print(f"  Credits: {user.credits}")
        print(f"  ID: {user.id}")
        
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python scripts/create_user.py email@example.com \"Full Name\" password [credits]")
        print("Example: python scripts/create_user.py admin@gradgen.ai \"Admin User\" mysecurepassword 1000")
        sys.exit(1)
    
    email = sys.argv[1]
    full_name = sys.argv[2]
    password = sys.argv[3]
    credits = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    
    create_user(email, full_name, password, credits)
