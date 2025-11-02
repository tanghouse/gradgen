# Run Migration via Railway Dashboard

## 🎯 Goal
Run the database migration using Railway's web dashboard (no CLI needed)

---

## 📋 Step-by-Step Instructions

### Step 1: Access Railway Dashboard

1. Open your browser
2. Go to: **https://railway.app/dashboard**
3. Login if needed
4. You should see your projects

---

### Step 2: Open Your Backend Service

1. Click on your **GradGen** project (or whatever it's named)
2. You'll see your services (backend, database, maybe frontend)
3. Click on the **backend service** (the one running Python/FastAPI)

---

### Step 3: Choose Your Migration Method

Railway offers several ways to run commands. Try these in order:

---

## ✅ METHOD 1: Using "Run Command" (Recommended)

**If you see a "Run Command" or "Shell" option:**

1. Look for a button/tab that says:
   - "Shell"
   - "Terminal"
   - "Run Command"
   - "Console"

2. Click it to open a command interface

3. Type:
   ```bash
   python migrate_business_model.py
   ```

4. Press Enter

5. Watch the output - you should see:
   ```
   🚀 Starting business model migration...
   ✓ Users table updated
   ✓ Payments table updated
   ✓ Generation jobs table updated
   ✓ Promo codes table created
   ✓ Referrals table created
   ✅ Migration completed successfully!
   ```

---

## ✅ METHOD 2: Modify Start Command (Works on All Plans)

**This method temporarily changes how your service starts:**

### Step 2.1: Go to Settings

1. In your backend service, click **"Settings"** tab
2. Scroll down to find the start command section

### Step 2.2: Note Current Start Command

Your current command is probably:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Copy this somewhere safe!** You'll need it later.

### Step 2.3: Update Start Command

Change the start command to:
```bash
cd webapp/backend && python migrate_business_model.py && cd ../.. && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

This will:
1. Run the migration first
2. Then start your app normally

### Step 2.4: Redeploy

1. Click **"Deploy"** or the redeploy button
2. Go to **"Deployments"** tab
3. Click on the new deployment to see logs

### Step 2.5: Watch the Logs

You should see migration output in the logs:
```
🚀 Starting business model migration...
📝 Step 1: Updating users table...
   ✅ Users table updated
...
✅ Migration completed successfully!
```

### Step 2.6: Revert Start Command

**IMPORTANT:** After the migration succeeds:

1. Go back to **"Settings"**
2. Change start command back to:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Save and redeploy

---

## ✅ METHOD 3: Create a Migration Service (Advanced)

**If you want a dedicated migration runner:**

### Step 3.1: Add New Service

1. In your Railway project, click **"+ New"**
2. Select **"Empty Service"** or **"GitHub Repo"**
3. Connect to the same repository

### Step 3.2: Configure Migration Service

1. Set the start command to:
   ```bash
   python webapp/backend/migrate_business_model.py
   ```

2. Set environment variables (copy from backend service):
   - `DATABASE_URL` (should auto-sync if using same project)

3. Deploy this service

4. After migration completes, you can delete this service

---

## 🧪 Verify Migration Succeeded

After running the migration, test that it worked:

### Test 1: Check Backend Logs

Look for these success messages:
```
✅ Users table updated
✅ Payments table updated
✅ Generation jobs table updated
✅ Promo codes table created
✅ Referrals table created
```

### Test 2: Test API Endpoint

Open a new browser tab and visit:
```
https://api.gradgen.ai/health
```

Should return:
```json
{"status": "healthy"}
```

### Test 3: Test New Tier Status Endpoint

You'll need a JWT token for this. If you have one:

```bash
# Replace YOUR_TOKEN with actual JWT
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.gradgen.ai/api/generation/tier-status
```

Should return:
```json
{
  "tier": "free",
  "has_used_free_tier": false,
  "has_purchased_premium": false,
  "can_generate": true,
  "message": "Free tier available"
}
```

### Test 4: Check Database (Optional)

If you have database access via Railway:

1. Go to your **Database** service in Railway
2. Click **"Data"** or **"Query"** tab
3. Run this SQL:
   ```sql
   -- Check new tables exist
   SELECT table_name
   FROM information_schema.tables
   WHERE table_name IN ('promo_codes', 'referrals');
   ```

Should show both tables.

---

## ⚠️ Troubleshooting

### Error: "DATABASE_URL not set"

**Cause:** Migration script can't find database URL

**Solution:**
1. Make sure you're running in the backend service (not locally)
2. Check that DATABASE_URL exists in Settings → Variables
3. It should be automatically set by Railway if you have a database service

### Error: "relation already exists"

**Cause:** Migration already ran successfully

**Solution:** This is actually fine! The script uses `IF NOT EXISTS`, so this just means the tables/columns already exist. You can ignore this.

### Error: "permission denied"

**Cause:** Database user doesn't have permission to ALTER tables

**Solution:**
1. Check your Railway database plan
2. Some plans have restrictions
3. Try upgrading or contact Railway support

### App Won't Start After Migration

**Cause:** You forgot to revert the start command

**Solution:**
1. Go to Settings
2. Change start command back to:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Redeploy

### Migration Seems Stuck

**Cause:** Large database or slow connection

**Solution:**
1. Wait a bit longer (can take 1-2 minutes)
2. Check Railway logs for progress
3. If truly stuck after 5 minutes, cancel and retry

---

## 📸 What Railway Dashboard Looks Like

**Project Dashboard:**
- You'll see boxes/cards for each service
- Usually: Backend (Python), Database (PostgreSQL), maybe Frontend

**Service View:**
- Tabs at top: Deployments, Settings, Metrics, Logs
- Settings tab has: Variables, Start Command, Build settings

**Deployments Tab:**
- List of recent deployments
- Click one to see logs
- Look for green checkmarks (successful) or red X (failed)

---

## ✅ After Successful Migration

### 1. Generate Referral Codes for Existing Users

If you have existing users, run this next:

```bash
# Via Railway CLI (if you login later)
railway run python webapp/backend/generate_codes_for_existing_users.py

# OR via same dashboard method
# Change start command to run this script, then revert
```

### 2. Create Test Promo Code (Optional)

You can create a promo code via the Django admin or a script:

```python
# If you have shell access
from app.models import PromoCode
from app.db.database import SessionLocal

db = SessionLocal()
promo = PromoCode(
    code="LAUNCH2025",
    discount_amount=20.00,
    discount_type="fixed",
    max_uses=100,
    is_active=True,
    description="Launch promotion"
)
db.add(promo)
db.commit()
print(f"✅ Created promo code: {promo.code}")
```

### 3. Test the New Features

- Try registering a new user
- Check if referral code is generated
- Test the tier status endpoint
- Try generating with free tier

---

## 🎉 Success Checklist

- [ ] Migration script ran without errors
- [ ] Backend service is running normally
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Tier status endpoint works (returns tier info)
- [ ] Referral link endpoint works (returns referral code)
- [ ] No errors in Railway logs

If all checked, you're ready to move on to:
1. Payment system updates
2. Frontend tier UI
3. Promo code API

---

## 🆘 Need Help?

If you run into issues:

1. **Check Railway Logs:**
   - Go to Deployments tab
   - Click latest deployment
   - Look for error messages

2. **Check Migration Output:**
   - Look for specific error messages
   - Share them if you need help

3. **Rollback if Needed:**
   - Railway keeps previous deployments
   - Can rollback to before migration
   - Database changes would remain though

4. **Safe to Retry:**
   - The migration script uses `IF NOT EXISTS`
   - Safe to run multiple times
   - Won't duplicate or break existing data

---

Good luck! The migration should take less than 1 minute to complete. 🚀
