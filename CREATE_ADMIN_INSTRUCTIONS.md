# Create Admin Account for Testing

## Quick Method: Via Railway Dashboard

### Option 1: Use Railway Shell (Easiest)

1. Go to https://railway.app/dashboard
2. Click on your **GradGen backend service**
3. Look for **"Shell"** or **"Terminal"** tab
4. Run this command:
   ```bash
   python create_admin.py
   ```

This will create an admin account with:
- **Email:** `admin@gradgen.ai`
- **Password:** `admin123`
- **Free tier available:** ✅
- **Email verified:** ✅
- **Superuser:** ✅

### Option 2: Custom Email/Password

If you want a different email or password:

```bash
python create_admin.py your.email@example.com YourPassword123 "Your Name"
```

---

## Option 3: Via Railway CLI (If You Have It)

If you have Railway CLI installed and logged in:

```bash
cd webapp/backend
railway run python create_admin.py
```

Or with custom details:

```bash
railway run python create_admin.py your.email@example.com YourPassword123
```

---

## What You Get

After running the script, you'll have a test account with:

✅ **Email Verified** - No need to click verification link
✅ **Superuser Status** - Full admin access
✅ **Free Tier Available** - Can test free generation (5 watermarked photos)
✅ **Referral Code** - Test the referral system
❌ **Premium Not Purchased** - So you can test the upgrade flow!

---

## How to Test the Full Flow

### 1. Test Free Tier
- Login with admin@gradgen.ai / admin123
- Go to `/generate`
- Upload a photo
- Select university and degree level
- Click "Generate 5 Watermarked Photos"
- Wait for processing
- View photos with prominent watermarks in dashboard

### 2. Test Premium Upgrade
- After free tier used, go back to `/generate`
- See pricing modal (£39.99 or £19.99 with referral)
- Click "Proceed to Payment"
- Use Stripe test card: `4242 4242 4242 4242`
- Expiry: Any future date
- CVC: Any 3 digits
- Complete payment
- Redirected to success page
- Generate 5 more premium photos
- Download all 10 without watermarks!

### 3. Test Referral System

Get your referral link:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.gradgen.ai/api/referrals/link
```

Or create 3 test accounts:
1. Register 3 friends with `?ref=YOUR_CODE`
2. Have them verify emails
3. Check your pricing - should show £19.99!

---

## Troubleshooting

**If script fails with "User already exists":**
- The account already exists! Just use those credentials
- The script will show you the current status

**If you can't access Railway Shell:**
- Go to Settings → Look for "Run Command" or "Jobs"
- Some Railway plans have different UI

**If you need to reset the account:**
You can run the script again, and it will update the existing user to superuser status.

---

## Default Admin Credentials

```
Email: admin@gradgen.ai
Password: admin123
```

**⚠️ Remember to change this password if you're using it in production!**

---

## Alternative: Quick SQL Command

If you prefer, you can also create an admin by connecting to Railway's PostgreSQL and running:

```sql
-- First, get the password hash from Python:
-- python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('admin123'))"

INSERT INTO users (
  email,
  full_name,
  hashed_password,
  is_active,
  is_superuser,
  email_verified,
  credits,
  created_at
) VALUES (
  'admin@gradgen.ai',
  'Admin User',
  '$2b$12$YOUR_HASH_HERE',  -- Replace with actual hash
  true,
  true,
  true,
  1000,
  NOW()
);
```

But the Python script is much easier! 🚀
