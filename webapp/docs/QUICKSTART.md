# GradGen Deployment Quick Start

**Ready to launch GradGen?** Follow these 5 simple steps to get your app live in 2-3 hours.

## ✅ Prerequisites Checklist

Before starting, make sure you have:

- [ ] GitHub account with your code pushed
- [ ] Google Gemini API key
- [ ] Stripe account (test mode is fine to start)
- [ ] Credit card for domain registration

## 🚀 5 Steps to Launch

### Step 1: Register Domain (10 minutes)

**Option A: gradgen.ai** (Recommended - $80-85/year)
1. Go to [Porkbun.com](https://porkbun.com)
2. Search "gradgen.ai" → Add to cart → Checkout
3. Enable WHOIS privacy (free)

**Option B: gradgen.co.uk** (Budget - $10-15/year)
1. Go to [Namecheap.com](https://www.namecheap.com)
2. Search "gradgen.co.uk" → Add to cart → Checkout

---

### Step 2: Setup Cloudflare (20 minutes)

1. **Create account**: [cloudflare.com](https://www.cloudflare.com)
2. **Add site**: Enter your domain → Free plan
3. **Update nameservers**: 
   - Cloudflare shows you 2 nameservers
   - Go to your domain registrar
   - Update NS records → Wait 5-30 min

4. **Create R2 bucket**:
   - Cloudflare Dashboard → R2
   - Create bucket: `gradgen-images`
   - Create API token → Save credentials

---

### Step 3: Deploy Backend on Railway (30 minutes)

1. **Sign up**: [railway.app](https://railway.app) with GitHub

2. **Create project**: 
   - New Project → Deploy from GitHub
   - Select your `gradgen` repo

3. **Add databases**:
   - Add PostgreSQL database
   - Add Redis database

4. **Deploy backend**:
   - New Service → GitHub repo
   - Root directory: `webapp/backend`
   - Add environment variables (see `.env.production.template`)
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Deploy worker**:
   - New Service → Same repo
   - Root directory: `webapp/backend`
   - Same environment variables
   - Start command: `celery -A app.tasks.celery_app worker --loglevel=info`

6. **Add custom domain**:
   - Backend service → Domains → `api.gradgen.ai`
   - Add CNAME in Cloudflare: `api` → Railway URL

**Test**: Visit `https://api.gradgen.ai/health` → Should return `{"status":"healthy"}`

---

### Step 4: Deploy Frontend on Vercel (15 minutes)

1. **Sign up**: [vercel.com](https://vercel.com) with GitHub

2. **Import project**:
   - New Project → Import from GitHub
   - Select your `gradgen` repo
   - Root directory: `webapp/frontend`

3. **Add environment variable**:
   ```
   NEXT_PUBLIC_API_URL=https://api.gradgen.ai
   ```

4. **Deploy** → Wait 2-3 minutes

5. **Add custom domains**:
   - Vercel → Domains
   - Add: `gradgen.ai` and `www.gradgen.ai`
   - Add DNS records in Cloudflare:
     ```
     A     @     76.76.21.21
     CNAME www   cname.vercel-dns.com
     ```

**Test**: Visit `https://gradgen.ai` → Should load your app!

---

### Step 5: Final Configuration (15 minutes)

1. **Update CORS in Railway**:
   - Backend service → Variables
   - Update `ALLOWED_ORIGINS`: `https://gradgen.ai,https://www.gradgen.ai`

2. **Configure Stripe webhook**:
   - [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
   - Add endpoint: `https://api.gradgen.ai/api/payments/webhook`
   - Events: `payment_intent.succeeded`, `payment_intent.payment_failed`
   - Copy signing secret → Update `STRIPE_WEBHOOK_SECRET` in Railway

3. **Create admin user**:
   - Railway → PostgreSQL → Connect
   - Run SQL to add yourself with credits

4. **Upload university templates** to R2 bucket

---

## 🎉 You're Live!

Your app is now running at:
- **Website**: https://gradgen.ai
- **API**: https://api.gradgen.ai

### Test Everything

- [ ] User registration
- [ ] Login
- [ ] Image upload
- [ ] Generation (test with 1 portrait)
- [ ] Download result
- [ ] Credit purchase (test mode)

---

## 💰 Monthly Costs

**Starter Plan** (~$17-25/month):
- Domain: $7/month
- Railway: $5-15/month
- Cloudflare R2: $0-2/month
- Vercel: FREE

**As you grow**, costs scale with usage. Monitor in Railway dashboard.

---

## 📊 Monitoring Setup (Optional but Recommended)

1. **Uptime monitoring**: [BetterStack](https://betterstack.com) (free)
   - Monitor `https://gradgen.ai`
   - Monitor `https://api.gradgen.ai/health`

2. **Error tracking**: [Sentry](https://sentry.io) (free tier)
   - Add to backend and frontend

3. **Railway metrics**: Built-in CPU, memory, bandwidth tracking

---

## 🆘 Quick Troubleshooting

**Backend won't deploy?**
- Check Railway logs
- Verify all env vars are set
- Check Python version in `pyproject.toml`

**Frontend build fails?**
- Check Vercel build logs
- Verify `NEXT_PUBLIC_API_URL` is set
- Try clearing Vercel cache

**Images not uploading?**
- Verify R2 credentials in Railway
- Check R2 bucket permissions
- Test R2 connection manually

**Payments not working?**
- Verify Stripe webhook is receiving events
- Check signing secret matches
- Test with Stripe test card: `4242 4242 4242 4242`

---

## 📞 Need Help?

- **Railway**: https://railway.app/help
- **Vercel**: https://vercel.com/support
- **Cloudflare**: https://community.cloudflare.com

---

**Happy deploying! 🚀**

See `DEPLOYMENT.md` for detailed step-by-step instructions with screenshots.
