# GradGen Backend

FastAPI backend for the GradGen graduation portrait generation platform.

## Setup

### Prerequisites

- Python 3.13+
- Poetry
- PostgreSQL
- Redis

### Installation

```bash
# Install dependencies
poetry install

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Database Setup

```bash
# Create PostgreSQL database
createdb gradgen

# Update DATABASE_URL in .env
# DATABASE_URL=postgresql://user:password@localhost:5432/gradgen

# Run migrations (tables will be created automatically on first run)
poetry run python -m app.main
```

### Redis Setup

```bash
# Start Redis (macOS with Homebrew)
brew services start redis

# Or with Docker
docker run -d -p 6379:6379 redis:alpine
```

## Running

### Development Server

```bash
# Start FastAPI server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Celery Worker

In a separate terminal:

```bash
# Start Celery worker for background tasks
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Users
- `GET /api/users/me` - Get current user info
- `PUT /api/users/me` - Update current user

### Generation
- `GET /api/generation/universities` - List available universities
- `POST /api/generation/single` - Generate single portrait
- `POST /api/generation/batch` - Generate batch of portraits
- `GET /api/generation/jobs` - List user's jobs
- `GET /api/generation/jobs/{id}` - Get job details
- `GET /api/generation/jobs/{id}/status` - Poll job status
- `GET /api/generation/results/{image_id}` - Download result

### Payments
- `GET /api/payments/config` - Get Stripe public key
- `POST /api/payments/create-payment-intent` - Create payment
- `POST /api/payments/webhook` - Stripe webhook handler

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `GEMINI_API_KEY` - Google Gemini API key
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)

## Architecture

### Project Structure

```
app/
├── api/
│   ├── deps.py           # Dependencies (auth, db)
│   └── endpoints/        # API route handlers
│       ├── auth.py       # Authentication
│       ├── users.py      # User management
│       ├── generation.py # Image generation
│       └── payments.py   # Stripe payments
├── core/
│   ├── config.py         # Settings
│   └── security.py       # JWT & password hashing
├── db/
│   └── database.py       # SQLAlchemy setup
├── models/               # SQLAlchemy models
│   ├── user.py
│   ├── credit_transaction.py
│   ├── generation_job.py
│   ├── generated_image.py
│   └── payment.py
├── schemas/              # Pydantic schemas
│   ├── user.py
│   └── generation.py
├── services/             # Business logic
│   └── generation_service.py
├── tasks/                # Celery tasks
│   ├── celery_app.py
│   └── generation_tasks.py
└── main.py               # FastAPI app
```

### Database Schema

- **users** - User accounts with credits
- **credit_transactions** - Credit purchase/usage history
- **generation_jobs** - Portrait generation jobs
- **generated_images** - Individual generated images
- **payments** - Stripe payment records

### Background Processing

Uses Celery with Redis for asynchronous image generation:
- Single portrait: ~10-30 seconds
- Batch processing: Parallel processing of multiple portraits

## Credits System

- New users get 5 free credits
- Each portrait generation costs 1 credit
- Credits can be purchased via Stripe
- Default: 10 credits = $1 USD (configurable)

## Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=app
```

## Deployment

### Production Considerations

1. **Database**: Use managed PostgreSQL (e.g., AWS RDS, Google Cloud SQL)
2. **Redis**: Use managed Redis (e.g., AWS ElastiCache, Redis Cloud)
3. **File Storage**: Switch from local to S3 (set `STORAGE_TYPE=s3`)
4. **Workers**: Deploy multiple Celery workers for scalability
5. **Monitoring**: Add Sentry for error tracking
6. **Rate Limiting**: Add rate limiting middleware
7. **HTTPS**: Always use HTTPS in production
8. **Environment**: Use strong `SECRET_KEY` and secure credentials

### Docker Deployment

```bash
# Build image
docker build -t gradgen-backend .

# Run with docker-compose
docker-compose up -d
```

## License

See main project LICENSE file.
