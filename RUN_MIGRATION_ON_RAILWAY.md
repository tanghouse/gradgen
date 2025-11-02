# How to Run Database Migration on Railway

## 🎯 Goal
Run `migrate_business_model.py` on Railway to add new tables and columns for the business model.

---

## ✅ Method 1: Railway CLI (Easiest)

### Step 1: Install Railway CLI (if not installed)
```bash
# macOS
brew install railway

# Or via npm
npm i -g @railway/cli
```

### Step 2: Login to Railway
```bash
railway login
```

### Step 3: Link to Your Project
```bash
cd /Users/Haichen\ Shi/Library/CloudStorage/OneDrive-BaringaPartnersLLP/Desktop/Projects/tanghouse
railway link
# Select your GradGen project
```

### Step 4: Run Migration
```bash
railway run python webapp/backend/migrate_business_model.py
```

---

## ✅ Method 2: Railway Dashboard (No CLI needed)

### Step 1: Go to Railway Dashboard
1. Visit https://railway.app/
2. Login
3. Select your GradGen backend project

### Step 2: Open Deployment Logs
1. Click on "Deployments" tab
2. Click on the most recent deployment
3. You should see the logs

### Step 3: Run One-Off Command
Railway has a "Run" feature for one-off commands:

1. In your service settings, look for "Service" menu
2. Find "Run a command" or similar option
3. Enter:
   ```bash
   python migrate_business_model.py
   ```
4. Click "Run"

**Note:** Railway's UI may vary. Look for:
- "Command" or "Run Command" button
- "Shell" or "Console" access
- "Jobs" or "Tasks" section

---

## ✅ Method 3: Add to Procfile (Runs on Deploy)

**⚠️ NOT RECOMMENDED** - This runs migration on every deploy

Create/update `webapp/backend/Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
release: python migrate_business_model.py
```

Then deploy:
```bash
git add webapp/backend/Procfile
git commit -m "Add migration to release command"
git push
```

---

## ✅ Method 4: SSH Access (If Available)

Some Railway plans offer shell access:

```bash
railway shell
cd /app
python migrate_business_model.py
```

---

## ✅ Method 5: Trigger via API Deploy

You can also add the migration as part of the start script temporarily:

### Step 1: Update Start Command
In Railway dashboard:
1. Go to Settings
2. Find "Start Command"
3. Change to:
   ```bash
   python migrate_business_model.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Step 2: Redeploy
1. Make a small commit (or just redeploy)
2. Migration runs before app starts

### Step 3: Revert Start Command
After successful migration, change back to:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🧪 How to Verify Migration Worked

After running the migration, test these endpoints:

### 1. Check Tier Status
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.gradgen.ai/api/generation/tier-status
```

**Expected response:**
```json
{
  "tier": "free",
  "has_used_free_tier": false,
  "has_purchased_premium": false,
  "can_generate": true,
  "message": "Free tier available"
}
```

### 2. Check Referral Link
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.gradgen.ai/api/referrals/link
```

**Expected response:**
```json
{
  "referral_code": "ABCD1234",
  "referral_link": "https://www.gradgen.ai/register?ref=ABCD1234",
  "stats": {...}
}
```

### 3. Check Database Directly (Optional)
If you have database access:
```sql
-- Check if new columns exist
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'users'
  AND column_name IN ('has_used_free_tier', 'has_purchased_premium', 'referral_code');

-- Check if new tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('promo_codes', 'referrals');
```

---

## 🔍 Troubleshooting

### Error: "DATABASE_URL not set"
**Solution:** The script is not running in Railway environment. Make sure you're using `railway run` or running inside Railway.

### Error: "column already exists"
**Solution:** Migration was already run. This is safe - the script uses `IF NOT EXISTS`.

### Error: "permission denied"
**Solution:** Database user may not have ALTER TABLE permissions. Check Railway database settings.

### Migration seems stuck
**Solution:** Check Railway logs for errors. Some operations may take time on large databases.

---

## 📝 What the Migration Does

The migration script (`migrate_business_model.py`) performs these operations:

1. **users table:**
   - Adds `has_used_free_tier` (BOOLEAN)
   - Adds `has_purchased_premium` (BOOLEAN)
   - Adds `referral_discount_eligible` (BOOLEAN)
   - Adds `referral_code` (VARCHAR, UNIQUE)

2. **payments table:**
   - Adds `original_price` (FLOAT)
   - Adds `discount_applied` (FLOAT)
   - Adds `discount_source` (VARCHAR)
   - Adds `promo_code_used` (VARCHAR)
   - Adds `generation_job_id` (INTEGER, FK)
   - Updates `currency` from 'usd' to 'gbp'

3. **generation_jobs table:**
   - Adds `tier` (VARCHAR)
   - Adds `is_watermarked` (BOOLEAN)
   - Adds `prompts_used` (TEXT)
   - Adds `payment_id` (INTEGER, FK)

4. **Creates new tables:**
   - `promo_codes` table with indexes
   - `referrals` table with indexes

**All operations use `IF NOT EXISTS` so it's safe to run multiple times.**

---

## ✅ After Migration Success

1. **Test the API endpoints** (see verification section above)
2. **Generate referral codes for existing users** (if any):
   ```bash
   railway run python generate_codes_for_existing_users.py
   ```
3. **Create a test promo code** (optional):
   ```python
   # Run in Railway shell or create script
   from app.models import PromoCode
   promo = PromoCode(
       code="LAUNCH2025",
       discount_amount=20.00,
       max_uses=100,
       is_active=True
   )
   db.add(promo)
   db.commit()
   ```

---

## 🚀 Recommended Approach

**I recommend Method 1 (Railway CLI)** because:
- ✅ Most reliable
- ✅ Shows output in real-time
- ✅ Easy to debug if issues arise
- ✅ One command: `railway run python webapp/backend/migrate_business_model.py`

Install CLI with:
```bash
brew install railway
# or
npm i -g @railway/cli
```

Then run:
```bash
railway login
railway link  # Select your project
railway run python webapp/backend/migrate_business_model.py
```

Done! 🎉
