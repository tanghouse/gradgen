from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.endpoints import auth, users, generation, payments, oauth, referrals, admin
from app.db.database import Base, engine
# from app.db.migrations import run_migrations  # Disabled: migrations run in start.sh
import os

# IMPORTANT: Migrations are now run in start.sh BEFORE the app starts
# This prevents table lock issues and startup hangs
# The lines below are commented out to avoid duplicate migration attempts

# Create database tables
# Base.metadata.create_all(bind=engine)  # Disabled: can cause locks

# Run migrations for email verification and OAuth
# try:
#     run_migrations()
# except Exception as e:
#     print(f"Migration warning: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for GradGen - AI-powered graduation portrait generation"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(oauth.router, prefix="/api/auth/oauth", tags=["oauth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(generation.router, prefix="/api/generation", tags=["generation"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(referrals.router, prefix="/api/referrals", tags=["referrals"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Mount static files for serving uploaded and generated images
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/results", StaticFiles(directory="results"), name="results")


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online"
    }


@app.get("/health")
async def health():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "service": "gradgen-api"}
