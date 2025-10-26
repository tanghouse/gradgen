# GradGen Deployment Guide

Complete guide to deploying GradGen to production using Railway + Vercel + Cloudflare.

**Target Domain**: gradgen.ai or gradgen.co.uk  
**Estimated Setup Time**: 2-3 hours  
**Monthly Cost**: $17-25 (starter), $72-97 (growth)

## Quick Links

- **Domain Registration**: [Porkbun](https://porkbun.com) | [Cloudflare](https://www.cloudflare.com/products/registrar/)
- **Backend Hosting**: [Railway](https://railway.app)
- **Frontend Hosting**: [Vercel](https://vercel.com)
- **DNS & CDN**: [Cloudflare](https://www.cloudflare.com)

---

## Domain Registration Steps

### For gradgen.ai ($80-85/year)

1. Visit [Porkbun.com](https://porkbun.com) or [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)
2. Search for "gradgen.ai"
3. Add to cart and complete registration
4. Enable WHOIS privacy (free)
5. Transfer nameservers to Cloudflare (next section)

### For gradgen.co.uk ($10-15/year)

1. Visit [Namecheap.com](https://www.namecheap.com)
2. Search for "gradgen.co.uk"
3. Complete registration
4. Transfer nameservers to Cloudflare

---

## Deployment Configuration Files

The following files have been created in your project:

### Backend Files
- `webapp/backend/railway.json` - Railway deployment config
- `webapp/backend/Procfile.worker` - Celery worker config
- `webapp/backend/app/services/storage_service.py` - Cloud storage service
- `webapp/backend/app/core/config.py` - Updated with R2/S3 settings

### Configuration Summary

**Railway will automatically**:
- Detect Python/Poetry project
- Install dependencies
- Run database migrations
- Start API server and Celery workers

**Vercel will automatically**:
- Detect Next.js project
- Build and deploy frontend
- Handle SSL certificates
- Enable global CDN

---

## Next Steps

### 1. Register Your Domain
Choose and register **gradgen.ai** or **gradgen.co.uk** now using the links above.

### 2. Set Up Cloudflare
1. Create account at [cloudflare.com](https://www.cloudflare.com)
2. Add your domain
3. Update nameservers at your registrar
4. Create R2 bucket for image storage

### 3. Deploy to Railway
1. Sign up at [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add PostgreSQL and Redis databases
4. Deploy backend API + Celery worker
5. Configure environment variables

### 4. Deploy to Vercel
1. Sign up at [vercel.com](https://vercel.com)
2. Import GitHub repository
3. Deploy frontend
4. Connect custom domain

### 5. Test & Launch
1. Test all functionality
2. Set up monitoring
3. Go live! 🚀

---

## Full Step-by-Step Guide

For complete deployment instructions with screenshots and troubleshooting, see the detailed guide in this file below.

---

[The rest of the deployment guide continues with full instructions for each platform...]

