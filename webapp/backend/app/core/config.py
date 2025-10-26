from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    # File Storage
    STORAGE_TYPE: str = "local"  # 'local', 's3', or 'r2'

    # AWS S3 Settings
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = ""

    # Cloudflare R2 Settings
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET: str = "gradgen-images"

    # Domain (for constructing public URLs)
    DOMAIN: str = "gradgen.ai"  # Change to your domain

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Credits & Pricing
    CREDITS_PER_PORTRAIT: int = 1
    CREDITS_PER_DOLLAR: int = 10

    # App Settings
    PROJECT_NAME: str = "GradGen API"
    VERSION: str = "0.1.0"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
