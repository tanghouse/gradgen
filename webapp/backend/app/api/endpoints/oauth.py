from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import urlencode
import secrets
from app.core.security import create_access_token
from app.core.config import settings
from app.db.database import get_db
from app.models import User
from app.services.email import EmailService
import httpx

router = APIRouter()

# Google OAuth configuration
GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_backend_base_url():
    """Get backend base URL from environment or construct it."""
    # Try to get from environment or use default
    backend_url = settings.FRONTEND_URL.replace('//www.', '//').replace('://', '://api.')
    if 'localhost:3000' in settings.FRONTEND_URL:
        backend_url = 'http://localhost:8000'
    return backend_url.rstrip('/')


@router.get("/google/authorize")
async def google_authorize():
    """Initiate Google OAuth flow."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to environment variables."
        )

    # Build redirect URI (backend callback URL)
    backend_url = get_backend_base_url()
    redirect_uri = f"{backend_url}/api/auth/oauth/google/callback"

    # Build authorization URL
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'online',
        'prompt': 'select_account',
    }

    auth_url = f"{GOOGLE_AUTHORIZATION_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback."""
    try:
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No authorization code provided"
            )

        # Exchange code for access token
        backend_url = get_backend_base_url()
        redirect_uri = f"{backend_url}/api/auth/oauth/google/callback"

        token_data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }

        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get access token: {token_response.text}"
                )

            token_json = token_response.json()
            access_token = token_json.get('access_token')

            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token in response"
                )

            # Get user info
            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )

            user_info = userinfo_response.json()

        email = user_info.get('email')
        google_id = user_info.get('sub')
        full_name = user_info.get('name')

        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or Google ID not provided by Google"
            )

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if user:
            # User exists - update OAuth info if not set
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = google_id

            # Ensure email is verified for OAuth users
            if not user.email_verified:
                user.email_verified = True
                user.email_verified_at = datetime.utcnow()

            # Update last login
            user.last_login_at = datetime.utcnow()
            db.commit()
        else:
            # Create new user
            user = User(
                email=email,
                full_name=full_name,
                oauth_provider='google',
                oauth_id=google_id,
                email_verified=True,  # OAuth emails are pre-verified
                email_verified_at=datetime.utcnow(),
                hashed_password=None,  # No password for OAuth-only users
                credits=5,  # Give new users 5 free credits
                last_login_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Send welcome email
            await EmailService.send_welcome_email(
                email=user.email,
                full_name=user.full_name
            )

        # Create access token
        jwt_token = create_access_token(data={"sub": str(user.id)})

        # Redirect to frontend with token
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        return RedirectResponse(
            url=f"{frontend_url}/oauth/callback?token={jwt_token}",
            status_code=302
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Google OAuth error: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=oauth_failed",
            status_code=302
        )


# Microsoft OAuth endpoints (placeholder for future implementation)
@router.get("/microsoft/authorize")
async def microsoft_authorize():
    """Initiate Microsoft OAuth flow."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Microsoft OAuth is not yet implemented. Coming soon!"
    )


@router.get("/microsoft/callback")
async def microsoft_callback():
    """Handle Microsoft OAuth callback."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Microsoft OAuth is not yet implemented. Coming soon!"
    )
