from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from datetime import datetime
from app.core.security import create_access_token
from app.core.config import settings
from app.db.database import get_db
from app.models import User
from app.services.email import EmailService

router = APIRouter()

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Register Microsoft OAuth
oauth.register(
    name='microsoft',
    client_id=settings.MICROSOFT_CLIENT_ID,
    client_secret=settings.MICROSOFT_CLIENT_SECRET,
    server_metadata_url=f'https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/v2.0/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@router.get("/google/authorize")
async def google_authorize(request: Request):
    """Initiate Google OAuth flow."""
    redirect_uri = f"{request.base_url}api/auth/oauth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )

        email = user_info.get('email')
        google_id = user_info.get('sub')
        full_name = user_info.get('name')

        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or Google ID not provided"
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
        access_token = create_access_token(data={"sub": str(user.id)})

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/oauth/callback?token={access_token}",
            status_code=status.HTTP_302_FOUND
        )

    except Exception as e:
        print(f"Google OAuth error: {e}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=oauth_failed",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/microsoft/authorize")
async def microsoft_authorize(request: Request):
    """Initiate Microsoft OAuth flow."""
    redirect_uri = f"{request.base_url}api/auth/oauth/microsoft/callback"
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)


@router.get("/microsoft/callback")
async def microsoft_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Microsoft OAuth callback."""
    try:
        # Get access token from Microsoft
        token = await oauth.microsoft.authorize_access_token(request)

        # Get user info from Microsoft
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Microsoft"
            )

        email = user_info.get('email') or user_info.get('preferred_username')
        microsoft_id = user_info.get('sub') or user_info.get('oid')
        full_name = user_info.get('name')

        if not email or not microsoft_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or Microsoft ID not provided"
            )

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if user:
            # User exists - update OAuth info if not set
            if not user.oauth_provider:
                user.oauth_provider = 'microsoft'
                user.oauth_id = microsoft_id

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
                oauth_provider='microsoft',
                oauth_id=microsoft_id,
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
        access_token = create_access_token(data={"sub": str(user.id)})

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/oauth/callback?token={access_token}",
            status_code=status.HTTP_302_FOUND
        )

    except Exception as e:
        print(f"Microsoft OAuth error: {e}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=oauth_failed",
            status_code=status.HTTP_302_FOUND
        )
