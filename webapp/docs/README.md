# GradGen Documentation

Welcome to the GradGen documentation. This folder contains all guides for setup, testing, admin, and deployment.

## 📚 Documentation Index

### Getting Started

| Document | Purpose | Audience |
|----------|---------|----------|
| **[Quick Start](./QUICKSTART.md)** | Local development setup | Developers |
| **[Deployment Guide](./DEPLOYMENT.md)** | Production deployment to Railway + Vercel | DevOps |

### Testing & Admin

| Document | Purpose | Audience |
|----------|---------|----------|
| **[Admin Quick Start](./ADMIN_QUICK_START.md)** ⭐ | Reset accounts via browser console (easiest!) | Testing/Admin |
| **[Admin Panel Instructions](./ADMIN_PANEL_INSTRUCTIONS.md)** | Complete browser-based admin guide | Testing/Admin |
| **[Account Management Guide](./ACCOUNT_MANAGEMENT_GUIDE.md)** | CLI tools reference (if Railway CLI works) | Testing/Admin |
| **[Reset Account Guide](./RESET_ACCOUNT_GUIDE.md)** | Multiple methods for account reset | Testing/Admin |
| **[Testing Checklist](./TESTING_CHECKLIST.md)** | 30-test comprehensive QA guide | QA/Testing |

### Component Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[Backend README](../backend/README.md)** | FastAPI backend setup & API docs | Backend Devs |
| **[Frontend README](../frontend/README.md)** | Next.js frontend setup & structure | Frontend Devs |
| **[Main README](../README.md)** | Project overview & quick links | Everyone |

---

## 🎯 Quick Navigation

### For New Developers
1. Read [Main README](../README.md)
2. Follow [Quick Start](./QUICKSTART.md)
3. Check [Backend README](../backend/README.md) and [Frontend README](../frontend/README.md)

### For Testers
1. Start with [Admin Quick Start](./ADMIN_QUICK_START.md)
2. Follow [Testing Checklist](./TESTING_CHECKLIST.md)
3. Reset accounts as needed using [Admin Panel Instructions](./ADMIN_PANEL_INSTRUCTIONS.md)

### For DevOps
1. Review [Main README](../README.md)
2. Follow [Deployment Guide](./DEPLOYMENT.md)
3. Set up monitoring and backups

### For Admins
1. Use [Admin Quick Start](./ADMIN_QUICK_START.md) for browser-based management
2. Refer to [Account Management Guide](./ACCOUNT_MANAGEMENT_GUIDE.md) if you need CLI tools
3. Check [Reset Account Guide](./RESET_ACCOUNT_GUIDE.md) for alternative methods

---

## 📖 Document Summaries

### Quick Start (QUICKSTART.md)
Complete local development setup guide for both backend and frontend. Covers:
- Prerequisites (Python, Node.js, PostgreSQL, Redis)
- Backend setup (Poetry, database, Celery)
- Frontend setup (npm, environment variables)
- Running the complete application locally

### Deployment Guide (DEPLOYMENT.md)
Production deployment to Railway (backend) + Vercel (frontend) + Cloudflare (DNS/R2). Covers:
- Domain registration
- Cloudflare setup and R2 bucket creation
- Railway deployment (API + Celery worker)
- Vercel frontend deployment
- Environment variables and CORS configuration

### Admin Quick Start (ADMIN_QUICK_START.md) ⭐
**Recommended for account management!** Browser console method that works reliably:
- Reset account to fresh state (30 seconds)
- Toggle between free and premium tiers
- Check account status
- Test complete user flows

**Why this doc?** Railway CLI doesn't work, database blocks external connections. Browser method uses deployed API and your login token.

### Admin Panel Instructions (ADMIN_PANEL_INSTRUCTIONS.md)
Comprehensive browser-based admin operations guide with JavaScript snippets for:
- Resetting account tier flags
- Viewing tier status
- Toggling premium access
- Checking generation job history
- Running complete test workflows

### Account Management Guide (ACCOUNT_MANAGEMENT_GUIDE.md)
Reference for the `manage_test_accounts.py` CLI tool (if Railway CLI works):
- Interactive menu mode
- Command-line mode
- Creating test accounts
- Resetting accounts (clears jobs + files)
- Toggling tiers
- Deleting accounts

### Reset Account Guide (RESET_ACCOUNT_GUIDE.md)
Multiple methods for resetting user accounts:
- Browser console method (recommended)
- Railway CLI method
- Admin API endpoint method
- Standalone admin.py script

### Testing Checklist (TESTING_CHECKLIST.md)
Comprehensive 30-test guide covering:
- Free tier functionality (4 tests)
- Premium purchase flow (3 tests)
- Premium usage and limits (7 tests)
- Mobile responsiveness (2 tests)
- Authentication (2 tests)
- API endpoints (2 tests)
- Edge cases and error handling (7 tests)

---

## 🔧 Tech Stack Summary

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Queue**: Celery + Redis
- **Auth**: JWT (python-jose)
- **Payments**: Stripe
- **AI**: Google Gemini API
- **Storage**: Cloudflare R2 (production) / Local filesystem (development)

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Payments**: Stripe.js + Stripe React

### Infrastructure
- **Backend Hosting**: Railway
- **Frontend Hosting**: Vercel
- **DNS & CDN**: Cloudflare
- **Storage**: Cloudflare R2
- **Database**: Railway PostgreSQL
- **Queue**: Railway Redis

---

## 🆘 Getting Help

### Local Development Issues
- Check [Backend README](../backend/README.md) for API setup
- Check [Frontend README](../frontend/README.md) for UI setup
- Review [Quick Start](./QUICKSTART.md) for prerequisites

### Deployment Issues
- Review [Deployment Guide](./DEPLOYMENT.md)
- Check Railway logs: `railway logs`
- Check Vercel build logs in dashboard

### Testing Issues
- Follow [Admin Quick Start](./ADMIN_QUICK_START.md) to reset account
- Use [Testing Checklist](./TESTING_CHECKLIST.md) systematically
- Check tier status using browser console

### Account Management Issues
- **Railway CLI not working?** Use browser method in [Admin Quick Start](./ADMIN_QUICK_START.md)
- **Database connection refused?** Use API-based methods instead of direct DB access
- **Token expired?** Logout and login again to refresh

---

## 📝 Notes

### Why Browser-Based Admin?
The browser console method is recommended because:
- ✅ Railway CLI has connection issues
- ✅ Direct database access is blocked in production
- ✅ Works through deployed API (already tested)
- ✅ Uses your JWT token (secure)
- ✅ No CLI setup required
- ✅ Works on any device

### File Organization
- `/docs` - All documentation (this folder)
- `/backend` - FastAPI backend code
- `/frontend` - Next.js frontend code
- Root-level files:
  - `README.md` - Main project overview
  - `pyproject.toml` - Python dependencies (backend)
  - `package.json` - Node dependencies (frontend)

---

**Last Updated**: November 2025
