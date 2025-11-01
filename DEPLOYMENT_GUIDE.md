# 🚀 Email Verification & OAuth Deployment Guide

## ✅ What's Been Completed

All code has been implemented and pushed to GitHub! Here's what's ready:

### Backend (100% Complete)
- ✅ Resend email service with beautiful HTML templates
- ✅ Email verification required for login
- ✅ Google OAuth integration
- ✅ Microsoft OAuth integration
- ✅ Updated User model with verification fields
- ✅ EmailVerificationToken model
- ✅ All authentication endpoints

### Frontend (100% Complete)
- ✅ Updated registration page with email verification message
- ✅ Updated login page with OAuth buttons and resend verification
- ✅ Email verification page (/verify-email)
- ✅ OAuth callback page (/oauth/callback)
- ✅ Updated API client

---

## 📋 Deployment Steps

### Step 1: Add Environment Variables to Backend

Add these to your **Railway** (or wherever your backend is hosted):

```bash
# Email (Resend)
RESEND_API_KEY=re_your-actual-resend-api-key
RESEND_FROM_EMAIL=noreply@gradgen.ai

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-google-client-secret

# OAuth - Microsoft
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=common

# Frontend URL (IMPORTANT for OAuth redirects!)
FRONTEND_URL=https://your-frontend-domain.vercel.app

# Email verification token expiry (optional, defaults to 24 hours)
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS=24
```

**Railway Instructions:**
1. Go to your Railway project
2. Click on your backend service
3. Go to "Variables" tab
4. Add each variable above
5. Click "Deploy" to restart with new variables

---

### Step 2: Update OAuth Redirect URIs

Now that your code is deployed, update your OAuth redirect URIs:

#### Google Cloud Console:
1. Go to https://console.cloud.google.com/
2. Select your project
3. Go to **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Under **Authorized redirect URIs**, add:
   - `https://your-backend-domain.railway.app/api/auth/oauth/google/callback`
6. Click **Save**

#### Microsoft Azure Portal:
1. Go to https://portal.azure.com/
2. Go to **Azure Active Directory** → **App registrations**
3. Select your app
4. Go to **Authentication**
5. Under **Web** redirect URIs, add:
   - `https://your-backend-domain.railway.app/api/auth/oauth/microsoft/callback`
6. Click **Save**

---

### Step 3: Run Database Migration

You need to add new columns to your database.

**Option A: Using Alembic (recommended)**

SSH into your Railway backend or run locally with production database:

```bash
cd webapp/backend

# Generate migration
poetry run alembic revision --autogenerate -m "Add email verification and OAuth fields"

# Apply migration
poetry run alembic upgrade head
```

**Option B: Manual SQL (if not using Alembic)**

Connect to your PostgreSQL database and run:

```sql
-- Add new columns to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR,
ADD COLUMN IF NOT EXISTS oauth_id VARCHAR,
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE,
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

-- Optional: Mark existing users as verified (so they can still login)
UPDATE users
SET email_verified = TRUE,
    email_verified_at = NOW()
WHERE email_verified IS NULL OR email_verified = FALSE;
```

---

### Step 4: Verify Resend Domain

**If using custom domain (recommended):**
1. Go to https://resend.com/domains
2. Add your domain (e.g., `gradgen.ai`)
3. Add the DNS records to your domain provider:
   - TXT record for verification
   - DKIM records for authentication
4. Wait for verification (5-15 minutes)

**For testing (using Resend's domain):**
- Use `onboarding@resend.dev` as `RESEND_FROM_EMAIL`
- This works immediately but emails may go to spam

---

### Step 5: Test Everything!

1. **Test Email Registration:**
   ```
   - Go to /register
   - Register with email/password
   - Check email for verification link
   - Click verification link
   - Try logging in (should work after verification)
   ```

2. **Test Google OAuth:**
   ```
   - Go to /login
   - Click "Sign in with Google"
   - Complete Google authentication
   - Should auto-login and redirect to dashboard
   ```

3. **Test Microsoft OAuth:**
   ```
   - Go to /login
   - Click "Sign in with Microsoft"
   - Complete Microsoft authentication
   - Should auto-login and redirect to dashboard
   ```

4. **Test Email Verification Error:**
   ```
   - Register a new account
   - Try logging in WITHOUT verifying email
   - Should see error with "Resend verification" link
   - Click "Resend verification"
   - Check email again
   ```

---

## 🔧 Troubleshooting

### Issue: Emails not being received

**Solution:**
1. Check Resend dashboard (https://resend.com/emails) for delivery status
2. Check spam folder
3. Verify `RESEND_API_KEY` is correct
4. Verify domain is set up correctly in Resend

### Issue: OAuth "redirect_uri_mismatch" error

**Solution:**
1. Check that redirect URIs in Google/Microsoft console EXACTLY match your backend URL
2. Make sure to include the full path: `/api/auth/oauth/google/callback`
3. Check that `FRONTEND_URL` environment variable is set correctly

### Issue: "Failed to load images" or migration errors

**Solution:**
1. Run the database migration SQL manually
2. Check that all new columns exist in the `users` table
3. Check that `email_verification_tokens` table was created

### Issue: Existing users can't login

**Solution:**
Run this SQL to mark all existing users as verified:
```sql
UPDATE users
SET email_verified = TRUE,
    email_verified_at = NOW()
WHERE email_verified = FALSE;
```

### Issue: OAuth redirects to wrong URL

**Solution:**
1. Check `FRONTEND_URL` environment variable in Railway
2. Make sure it's set to your production frontend URL (without trailing slash)
3. Restart the backend service after changing

---

## 🎉 Success Checklist

- [ ] Environment variables added to Railway
- [ ] Database migration completed
- [ ] Google OAuth redirect URI updated
- [ ] Microsoft OAuth redirect URI updated
- [ ] Resend domain verified (or using test domain)
- [ ] Tested email registration flow
- [ ] Tested Google OAuth flow
- [ ] Tested Microsoft OAuth flow
- [ ] Tested email verification
- [ ] Tested resend verification email

---

## 📊 Monitoring

**Check these regularly:**

1. **Resend Dashboard**
   - https://resend.com/emails
   - Monitor email delivery
   - Check bounce rates

2. **Railway Logs**
   - Check for authentication errors
   - Monitor OAuth callback errors

3. **Database**
   - Monitor `email_verification_tokens` table
   - Clean up old expired tokens periodically

---

## 🔒 Security Recommendations

1. **Keep secrets secure:**
   - Never commit `.env` files
   - Rotate OAuth secrets periodically
   - Use Railway's secret management

2. **Rate limiting:**
   - Consider adding rate limiting to `/auth/resend-verification`
   - Prevent spam/abuse

3. **Token cleanup:**
   - Add a cron job to delete expired tokens:
   ```sql
   DELETE FROM email_verification_tokens
   WHERE expires_at < NOW() AND used = TRUE;
   ```

4. **Monitor failed logins:**
   - Add logging for failed login attempts
   - Consider adding account lockout after X failed attempts

---

## 📝 Notes

- Email verification is **required** by default
- OAuth users are auto-verified
- Verification tokens expire after 24 hours
- All new users get 5 free credits
- OAuth accounts automatically link to existing email accounts

---

## 🆘 Need Help?

If you encounter issues:
1. Check the `AUTH_IMPLEMENTATION_SUMMARY.md` for detailed technical documentation
2. Check Railway logs for backend errors
3. Check browser console for frontend errors
4. Check Resend dashboard for email delivery issues

**Common Error Messages:**
- "Email not verified" → User needs to check email and click verification link
- "redirect_uri_mismatch" → OAuth redirect URIs need to be updated
- "Failed to send email" → Check Resend API key and domain setup

---

## ✨ You're Done!

Your authentication system is now fully deployed with:
- ✅ Email verification
- ✅ Google OAuth
- ✅ Microsoft OAuth
- ✅ Beautiful email templates
- ✅ Secure token management

Happy deploying! 🚀
