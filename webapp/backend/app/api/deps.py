from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    print(f"[DEBUG] get_current_user called with token: {token[:50] if token else 'None'}...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    print(f"[DEBUG] Payload after decode: {payload}")

    if payload is None:
        print("[DEBUG] Payload is None, raising exception")
        raise credentials_exception

    user_id_str = payload.get("sub")
    print(f"[DEBUG] Extracted user_id_str: {user_id_str}, type: {type(user_id_str)}")

    if user_id_str is None:
        print("[DEBUG] user_id_str is None, raising exception")
        raise credentials_exception

    try:
        user_id = int(user_id_str)
        print(f"[DEBUG] Converted to user_id: {user_id}")
    except (ValueError, TypeError) as e:
        print(f"[DEBUG] Failed to convert user_id: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    print(f"[DEBUG] User query result: {user}")

    if user is None:
        print("[DEBUG] User not found in database, raising exception")
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
