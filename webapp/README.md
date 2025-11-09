# GradGen - AI Graduation Portrait Generator

Transform casual photos into professional graduation portraits with AI-powered regalia generation.

🚀 **Status**: ✅ Production Ready | 🎯 **Latest**: Nov 2025 - Tier limits, mobile fixes, admin tools

## 🚀 Quick Links

| Document | Purpose | For |
|----------|---------|-----|
| **[Admin Quick Start](./docs/ADMIN_QUICK_START.md)** | ⭐ Manage & reset accounts | Testing/Admin |
| **[Testing Checklist](./docs/TESTING_CHECKLIST.md)** | 30-test comprehensive guide | QA |
| **[Quick Start](./docs/QUICKSTART.md)** | Local development setup | Developers |
| **[Deployment Guide](./docs/DEPLOYMENT.md)** | Production deployment | DevOps |

## Project Structure

```
webapp/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Config & security
│   │   ├── db/       # Database
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── tasks/    # Celery tasks
│   │   └── main.py   # FastAPI app
│   ├── admin.py      # Standalone admin tool
│   ├── manage_test_accounts.py  # CLI account manager
│   └── README.md
├── frontend/         # Next.js frontend
│   ├── app/          # Next.js 15 App Router
│   ├── components/   # React components
│   ├── lib/          # API client & utilities
│   └── public/       # Static assets
└── docs/             # Documentation
    ├── README.md              # Documentation index
    ├── QUICKSTART.md          # Local development setup
    ├── DEPLOYMENT.md          # Production deployment
    ├── TESTING_CHECKLIST.md   # 30-test QA guide
    ├── ADMIN_QUICK_START.md   # Browser-based admin (recommended)
    └── [more docs...]
```

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL
- Redis
- Poetry (Python package manager)
- npm

### Backend Setup

```bash
cd backend

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Edit .env with your settings:
# - DATABASE_URL (PostgreSQL)
# - REDIS_URL
# - GEMINI_API_KEY
# - STRIPE keys
# - SECRET_KEY
nano .env

# Create database
createdb gradgen

# Start the server
poetry run uvicorn app.main:app --reload

# In another terminal, start Celery worker
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

The backend will be running at http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

The frontend will be running at http://localhost:3000

For detailed setup instructions, see **[docs/QUICKSTART.md](./docs/QUICKSTART.md)**

## ✅ Complete Features

### Backend (100% Complete)

- ✅ **Authentication System**
  - JWT-based authentication
  - User registration/login
  - Password hashing with bcrypt
  - Protected routes with OAuth2

- ✅ **Database Models**
  - Users with credits system
  - Generation jobs tracking
  - Generated images storage
  - Credit transactions history
  - Payment records (Stripe)

- ✅ **API Endpoints**
  - `/api/auth/*` - Authentication (login, register)
  - `/api/users/*` - User management (get/update profile)
  - `/api/generation/*` - Image generation (single, batch, status, download)
  - `/api/payments/*` - Stripe integration (payment intents, webhooks)

- ✅ **Portrait Generation**
  - Single portrait generation
  - Batch processing support
  - Celery background tasks
  - Google Gemini API integration
  - University/degree level support
  - Job status polling
  - Error handling and recovery

- ✅ **Credits & Payments**
  - Credits-based system
  - Stripe payment integration
  - Webhook handling
  - Transaction history
  - Free credits for new users (5 credits)

### Frontend (100% Complete)

- ✅ **Authentication Pages**
  - Login page (`/login`)
  - Registration page (`/register`)
  - Auth context with persistent sessions
  - Protected routes

- ✅ **Core Pages**
  - Landing page with hero, features, pricing (`/`)
  - Generation page with upload & selectors (`/generate`)
  - Dashboard with job history (`/dashboard`)
  - Credits purchase page with Stripe (`/credits`)
  - Examples showcase page (`/examples`)

- ✅ **Components**
  - Responsive navigation bar
  - File upload with drag & drop
  - University/degree selector
  - Real-time job polling
  - Progress tracking
  - Download management

- ✅ **User Experience**
  - Fully responsive design
  - Loading states
  - Error handling
  - Success notifications
  - TypeScript type safety
  - Tailwind CSS styling

## 🧪 Testing & Admin

### For Testers & QA
Use the **[Testing Checklist](./docs/TESTING_CHECKLIST.md)** for comprehensive 30-test coverage.

### For Admins & Account Management
**Recommended:** Use the **[Admin Quick Start](./docs/ADMIN_QUICK_START.md)** browser console method to:
- Reset accounts to fresh state (30 seconds)
- Toggle between free and premium tiers
- Check account status and generation limits
- Test complete user flows

**Why browser method?** Railway CLI and direct database access have connection issues. The browser method uses the deployed API with your login token.

**All Admin Documentation:**
- **[Admin Quick Start](./docs/ADMIN_QUICK_START.md)** - Browser console (easiest, recommended)
- **[Admin Panel Instructions](./docs/ADMIN_PANEL_INSTRUCTIONS.md)** - Complete browser guide
- **[Account Management Guide](./docs/ACCOUNT_MANAGEMENT_GUIDE.md)** - CLI tools reference
- **[Reset Account Guide](./docs/RESET_ACCOUNT_GUIDE.md)** - Multiple reset methods

---

## 🎯 Optional Enhancements

These features can be added based on your needs:

### Backend
- [ ] Database migrations with Alembic
- [x] S3/R2 file storage (Cloudflare R2 integrated)
- [ ] Unit and integration tests
- [ ] Rate limiting
- [ ] Email notifications
- [ ] Multiple prompt selection
- [ ] Batch download as ZIP

### Frontend
- [ ] User profile page
- [ ] Transaction history page
- [ ] Real example images
- [ ] Image preview before generation
- [ ] Batch result gallery view
- [ ] Share results on social media
- [ ] Dark mode
- [ ] Internationalization (i18n)

### Infrastructure
- [ ] Docker Compose configuration
- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Monitoring and alerting (Sentry, BetterStack)
- [ ] CDN for static assets

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Queue**: Celery + Redis
- **Auth**: JWT (python-jose)
- **Payments**: Stripe
- **AI**: Google Gemini API
- **Image Processing**: Pillow

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Payments**: Stripe.js + Stripe React

## Development Commands

### Backend

```bash
# Run server
poetry run uvicorn app.main:app --reload

# Run Celery worker
poetry run celery -A app.tasks.celery_app worker --loglevel=info

# Run tests
poetry run pytest

# Format code
poetry run black app/
```

### Frontend

```bash
# Development
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint
npm run lint
```

## Environment Variables

### Backend (.env)

Required variables:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SECRET_KEY` - JWT secret
- `GEMINI_API_KEY` - Google Gemini API key
- `STRIPE_SECRET_KEY` - Stripe secret
- `STRIPE_PUBLISHABLE_KEY` - Stripe public key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `ALLOWED_ORIGINS` - CORS origins

### Frontend (.env.local)

Required variables:
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

## Credits System

- New users receive 5 free credits
- Each portrait generation costs 1 credit
- Default pricing: 10 credits = $1 USD
- Credits can be purchased via Stripe

## API Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚀 Deployment

Ready to deploy to production? See **[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)** for complete Railway + Vercel deployment guide.

**Deployment Stack:**
- **Backend**: Railway (FastAPI + Celery worker + PostgreSQL + Redis)
- **Frontend**: Vercel (Next.js)
- **DNS & CDN**: Cloudflare
- **Storage**: Cloudflare R2

**Estimated Setup Time**: 2-3 hours
**Monthly Cost**: $17-25 (starter), $72-97 (growth)

---

## 📚 Complete Documentation

All documentation is in the **[`/docs`](./docs/)** folder:

| Document | Purpose |
|----------|---------|
| **[Docs Index](./docs/README.md)** | Complete documentation overview |
| **[Quick Start](./docs/QUICKSTART.md)** | Local development setup |
| **[Deployment](./docs/DEPLOYMENT.md)** | Production deployment guide |
| **[Testing Checklist](./docs/TESTING_CHECKLIST.md)** | 30-test comprehensive QA |
| **[Admin Quick Start](./docs/ADMIN_QUICK_START.md)** | Browser-based account management |
| **[Backend README](./backend/README.md)** | FastAPI backend documentation |
| **[Frontend README](./frontend/README.md)** | Next.js frontend documentation |

---

## 🤝 Contributing

This is a graduation portrait generation platform. The core generation logic is ported from the research codebase in the root `src/` directory.

**Key Areas for Contribution:**
- Testing and QA (see [Testing Checklist](./docs/TESTING_CHECKLIST.md))
- UI/UX improvements
- Additional university templates
- Performance optimizations
- Documentation improvements

---

## 📄 License

See main project LICENSE file.
