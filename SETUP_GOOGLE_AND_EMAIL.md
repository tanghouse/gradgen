# 🚀 Complete Setup Guide: Email + Google OAuth Only

This guide will help you set up email authentication with verification and Google OAuth login.

---

## 📋 What You Need

1. **Resend account** (for sending verification emails)
2. **Google Cloud Console** (for Google OAuth)
3. **Your backend URL** (Railway deployment URL)
4. **Your frontend URL** (Vercel deployment URL)

---

## Part 1: Resend Email Service Setup (5 minutes)

### Step 1: Create Resend Account
1. Go to https://resend.com/
2. Click **Sign Up**
3. Use your email or sign up with GitHub
4. Verify your email address

### Step 2: Get Your API Key
1. After logging in, you'll see the Resend dashboard
2. Click **API Keys** in the left sidebar
3. Click **+ Create API Key**
4. Fill in:
   - **Name**: `TangHouse Production`
   - **Permission**: `Sending access` (Full access)
5. Click **Add**
6. **COPY THE API KEY** - it starts with `re_`
   - ⚠️ You won't be able to see this again!
   - Save it somewhere safe (we'll use it later)

### Step 3A: Set Up Custom Domain (Recommended for Production)

**If you own `gradgen.ai` or your custom domain:**

1. In Resend dashboard, go to **Domains**
2. Click **+ Add Domain**
3. Enter your domain: `gradgen.ai`
4. Resend will show you DNS records to add

5. **Go to your domain provider** (Cloudflare, GoDaddy, Namecheap, etc.)
6. Add these DNS records:

   **TXT Record** (for verification):
   ```
   Name: @
   Value: [shown by Resend]
   TTL: Auto or 3600
   ```

   **DKIM Records** (for authentication - IMPORTANT):
   ```
   Name: resend._domainkey
   Value: [shown by Resend]
   TTL: Auto or 3600

   Name: resend2._domainkey
   Value: [shown by Resend]
   TTL: Auto or 3600

   Name: resend3._domainkey
   Value: [shown by Resend]
   TTL: Auto or 3600
   ```

7. Wait 5-15 minutes for DNS propagation
8. Go back to Resend and click **Verify** on your domain
9. Once verified, your "From" email will be: **`noreply@gradgen.ai`**

### Step 3B: Use Test Domain (Quick Start for Testing)

**If you want to start testing immediately:**

1. Skip domain setup for now
2. Use Resend's test email: **`onboarding@resend.dev`**
3. ⚠️ Note: Emails may go to spam folder
4. ✅ Perfect for testing, but set up custom domain before launch

### Step 4: Save Your Resend Values

You now have:
- `RESEND_API_KEY`: `re_xxxxxxxxxxxxxxxxxxxxx`
- `RESEND_FROM_EMAIL`: `noreply@gradgen.ai` OR `onboarding@resend.dev`

---

## Part 2: Google OAuth Setup (10 minutes)

### Step 1: Go to Google Cloud Console
1. Visit https://console.cloud.google.com/
2. Sign in with your Google account

### Step 2: Create or Select Project
1. Click the **project dropdown** at the top (next to "Google Cloud")
2. Click **NEW PROJECT**
3. Fill in:
   - **Project name**: `TangHouse`
   - **Location**: Leave as is (or select your organization)
4. Click **CREATE**
5. Wait a few seconds, then select your new project

### Step 3: Configure OAuth Consent Screen (REQUIRED FIRST!)

1. In the left sidebar (☰ menu), go to:
   - **APIs & Services** → **OAuth consent screen**

2. **Choose User Type**:
   - Select **External** (for any Google user)
   - Click **CREATE**

3. **OAuth Consent Screen - Page 1 (App Information)**:
   ```
   App name: TangHouse
   User support email: [your-email@gmail.com]
   App logo: [optional - skip for now]
   ```

4. **App domain** (optional but recommended):
   ```
   Application home page: https://gradgen.ai
   Application privacy policy link: https://gradgen.ai/privacy
   Application terms of service link: https://gradgen.ai/terms
   ```

5. **Authorized domains**:
   - Add: `gradgen.ai` (your main domain)
   - ⚠️ Don't include `https://` or `www.`

6. **Developer contact information**:
   - Enter your email address

7. Click **SAVE AND CONTINUE**

8. **Scopes - Page 2**:
   - Click **ADD OR REMOVE SCOPES**
   - Filter and select these scopes:
     - ✅ `.../auth/userinfo.email`
     - ✅ `.../auth/userinfo.profile`
     - ✅ `openid`
   - Click **UPDATE**
   - Click **SAVE AND CONTINUE**

9. **Test users - Page 3**:
   - Click **+ ADD USERS**
   - Add your email and any other test emails
   - Click **ADD**
   - Click **SAVE AND CONTINUE**

10. **Summary - Page 4**:
    - Review everything
    - Click **BACK TO DASHBOARD**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** (at the top)
3. Select **OAuth client ID**

4. **Application type**: Choose **Web application**

5. **Name**: `TangHouse Web Client`

6. **Authorized JavaScript origins**:
   - Click **+ ADD URI**
   - Add: `http://localhost:8000` (for local backend testing)
   - Click **+ ADD URI**
   - Add: `https://your-backend-domain.railway.app` (your production backend)

7. **Authorized redirect URIs** (VERY IMPORTANT):
   - Click **+ ADD URI**
   - Add: `http://localhost:8000/api/auth/oauth/google/callback`
   - Click **+ ADD URI**
   - Add: `https://your-backend-domain.railway.app/api/auth/oauth/google/callback`

   ⚠️ **Make sure the path is EXACTLY**: `/api/auth/oauth/google/callback`

8. Click **CREATE**

9. **A popup will appear** with your credentials:
   ```
   Your Client ID:
   xxxxx-xxxxxxx.apps.googleusercontent.com

   Your Client Secret:
   GOCSPX-xxxxxxxxxxxxx
   ```

10. **COPY BOTH VALUES** and save them!
    - Click the download button to download as JSON (backup)
    - Or click the copy icons to copy each one

### Step 5: Publish Your App (When Ready)

Your app starts in **Testing** mode (limited to 100 test users).

**When ready for production:**
1. Go to **OAuth consent screen**
2. Under **Publishing status**, click **PUBLISH APP**
3. Click **CONFIRM**

⚠️ **Note**: For apps using only non-sensitive scopes (email, profile), you don't need Google verification. Your app will show a warning but users can still proceed.

### Step 6: Save Your Google Values

You now have:
- `GOOGLE_CLIENT_ID`: `xxxxx-xxxxxxx.apps.googleusercontent.com`
- `GOOGLE_CLIENT_SECRET`: `GOCSPX-xxxxxxxxxxxxx`

---

## Part 3: Add Environment Variables to Railway (5 minutes)

### Step 1: Go to Railway
1. Visit https://railway.app/
2. Go to your project
3. Click on your **backend service**

### Step 2: Add Variables
1. Click the **Variables** tab
2. Click **+ New Variable**
3. Add each of these (click **+ New Variable** for each one):

```bash
# Email Service (Resend)
RESEND_API_KEY=re_your-actual-api-key-from-step-1
RESEND_FROM_EMAIL=noreply@gradgen.ai

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret

# Microsoft OAuth (leave empty for now - we'll add later)
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_TENANT_ID=common

# URLs
FRONTEND_URL=https://your-frontend-domain.vercel.app

# Optional Settings
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS=24
```

### Step 3: Deploy
1. After adding all variables, Railway will automatically redeploy
2. Or click **Deploy** button if it doesn't auto-deploy
3. Wait for deployment to complete (check the **Deployments** tab)

---

## Part 4: Run Database Migration (5 minutes)

You need to add new columns to your database for email verification.

### Option A: Using Railway Database Dashboard

1. Go to your Railway project
2. Click on your **PostgreSQL** database
3. Click **Data** tab
4. Click **Query** (or **Execute SQL**)
5. Copy and paste this SQL:

```sql
-- Add new columns to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR,
ADD COLUMN IF NOT EXISTS oauth_id VARCHAR,
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- Make hashed_password nullable (for OAuth-only users)
ALTER TABLE users
ALTER COLUMN hashed_password DROP NOT NULL;

-- Create email verification tokens table
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_email_verification_token ON email_verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_email_verification_user_id ON email_verification_tokens(user_id);

-- IMPORTANT: Mark existing users as verified (so they can still login)
UPDATE users
SET email_verified = TRUE,
    email_verified_at = NOW()
WHERE email_verified IS FALSE OR email_verified IS NULL;
```

6. Click **Execute** or **Run**
7. You should see success messages

### Option B: Using Alembic (Alternative)

If you prefer using Alembic migrations:

```bash
cd webapp/backend

# Create migration
poetry run alembic revision --autogenerate -m "Add email verification and OAuth fields"

# Apply migration
poetry run alembic upgrade head
```

---

## Part 5: Update Google Redirect URIs (After Deployment)

Once your backend is deployed on Railway:

1. **Get your Railway backend URL**:
   - In Railway, click your backend service
   - Click **Settings** tab
   - Copy the **Public Domain** (e.g., `your-app.railway.app`)

2. **Update Google Console**:
   - Go back to https://console.cloud.google.com/
   - Go to **APIs & Services** → **Credentials**
   - Click on your OAuth client
   - Under **Authorized redirect URIs**, make sure you have:
     - `https://your-app.railway.app/api/auth/oauth/google/callback`
   - Click **SAVE**

---

## Part 6: Test Everything! (10 minutes)

### Test 1: Email Registration Flow

1. Go to your website: `https://your-frontend-domain.vercel.app/register`
2. Fill in the registration form with:
   - Full name
   - Email address
   - Password (at least 6 characters)
   - Confirm password
3. Click **Create Account**
4. ✅ You should see a success message: "Registration successful! Check your email..."
5. Check your email inbox (and spam folder)
6. You should receive a beautiful verification email from Resend
7. Click the **Verify Email Address** button in the email
8. ✅ You should be redirected to a success page
9. Click **Go to Login**
10. Try logging in with your email and password
11. ✅ You should be logged in and redirected to dashboard

### Test 2: Email Not Verified Error

1. Register a new account
2. **Don't verify the email**
3. Try to login immediately
4. ✅ You should see error: "Email not verified. Please check your email..."
5. Click **Resend verification email**
6. ✅ Check your email - you should receive a new verification email

### Test 3: Google OAuth Flow

1. Go to login page: `https://your-frontend-domain.vercel.app/login`
2. Click **Google** button
3. You'll be redirected to Google sign-in
4. Sign in with your Google account
5. Google will ask for permissions (email, profile)
6. Click **Allow** or **Continue**
7. ✅ You should be redirected back to your site
8. ✅ You should be automatically logged in
9. ✅ You should be on the dashboard

### Test 4: Check Resend Dashboard

1. Go to https://resend.com/emails
2. ✅ You should see your sent emails listed
3. Check delivery status, opens, etc.

---

## 🎉 Success Checklist

- [ ] Resend account created and API key obtained
- [ ] Resend domain verified (or using test domain)
- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] Google OAuth credentials created (Client ID & Secret)
- [ ] Environment variables added to Railway
- [ ] Backend redeployed with new variables
- [ ] Database migration completed
- [ ] Google redirect URIs updated with production URL
- [ ] Tested email registration → verification → login
- [ ] Tested "email not verified" error
- [ ] Tested resend verification email
- [ ] Tested Google OAuth sign-in
- [ ] Checked Resend dashboard for email delivery

---

## 🐛 Troubleshooting

### Issue: Not receiving verification emails

**Checks:**
1. ✅ Check spam/junk folder
2. ✅ Check Resend dashboard (https://resend.com/emails) for delivery status
3. ✅ Verify `RESEND_API_KEY` is correct in Railway
4. ✅ If using custom domain, verify domain is verified in Resend
5. ✅ Check Railway backend logs for any errors

### Issue: Google OAuth shows "redirect_uri_mismatch" error

**Fix:**
1. Go to Google Cloud Console → Credentials
2. Check that redirect URI is EXACTLY:
   - `https://your-backend.railway.app/api/auth/oauth/google/callback`
3. Make sure no trailing slash
4. Make sure it's the backend URL, not frontend
5. Wait a few minutes after saving changes

### Issue: "Email not verified" but I clicked the link

**Fix:**
1. Check if the verification link expired (24 hours)
2. Try clicking "Resend verification email" on login page
3. Check backend logs for any errors
4. Verify database migration ran successfully:
   ```sql
   SELECT column_name FROM information_schema.columns
   WHERE table_name = 'users' AND column_name = 'email_verified';
   ```

### Issue: Google sign-in works but user not logged in

**Checks:**
1. ✅ Check browser console for errors
2. ✅ Verify `FRONTEND_URL` is set correctly in Railway
3. ✅ Check that OAuth callback page exists at `/oauth/callback`
4. ✅ Check Railway backend logs for OAuth errors

---

## 📊 Environment Variables Summary

Here's what you should have in Railway:

```bash
# Required for Email
RESEND_API_KEY=re_xxxxx
RESEND_FROM_EMAIL=noreply@gradgen.ai

# Required for Google OAuth
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx

# Required for System
FRONTEND_URL=https://your-frontend.vercel.app

# Optional (leave empty for now)
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_TENANT_ID=common

# Optional Settings
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS=24
```

---

## 📝 Important URLs

Save these for reference:

**Google Cloud Console:**
- Project: https://console.cloud.google.com/
- Credentials: https://console.cloud.google.com/apis/credentials
- OAuth Consent: https://console.cloud.google.com/apis/credentials/consent

**Resend:**
- Dashboard: https://resend.com/
- Emails: https://resend.com/emails
- API Keys: https://resend.com/api-keys
- Domains: https://resend.com/domains

**Your App:**
- Frontend: https://your-frontend.vercel.app
- Backend: https://your-backend.railway.app
- Backend Docs: https://your-backend.railway.app/docs

---

## 🔒 Security Notes

1. **Never commit secrets to Git**
   - API keys and secrets should only be in Railway/Vercel
   - Never in code or `.env` files committed to GitHub

2. **Rotate secrets periodically**
   - Resend API keys can be regenerated
   - Google OAuth secrets can be rotated in Console

3. **Monitor Resend usage**
   - Free tier: 3,000 emails/month, 100/day
   - Set up billing alerts if needed

4. **Keep Google app in Testing mode until ready**
   - Limited to 100 test users
   - Publish when ready for production

---

## ✨ You're Done!

Your authentication system is now live with:
- ✅ Email registration with verification
- ✅ Google OAuth sign-in
- ✅ Beautiful email templates
- ✅ Secure token management

**Microsoft OAuth has been moved to backlog and can be added later if needed.**

Need help? Check the error messages and troubleshooting section above!
