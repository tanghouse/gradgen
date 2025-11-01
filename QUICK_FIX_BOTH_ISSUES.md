# 🚀 Quick Fix for Both Issues

## Issue 1: Email Registration Failed ❌

### **Problem**
Database columns for email verification don't exist yet.

### **Fix (5 minutes)**

1. **Go to Railway Dashboard**
   - Visit https://railway.app/
   - Select your project
   - Click on your **PostgreSQL** database

2. **Open Data Tab**
   - Click **Data** tab
   - Click **Query** (or you might see a SQL editor)

3. **Run Migration SQL**
   - Copy the entire contents of `database_migration.sql` (in your project root)
   - Paste into the query editor
   - Click **Execute** or **Run**

4. **Verify Success**
   - You should see: "Query executed successfully" or similar
   - The last query will show 6 columns (email_verified, email_verified_at, etc.)

5. **Test Email Registration**
   - Go to https://www.gradgen.ai/register
   - Try registering with email again
   - ✅ Should work now!

---

## Issue 2: Google OAuth "Access Blocked" ❌

### **Problem**
Google OAuth consent screen is not properly configured or published.

### **Quick Fix (10 minutes)**

#### **Option A: Publish Your App (Easiest)**

1. Go to https://console.cloud.google.com/
2. Select your TangHouse project
3. Go to **APIs & Services** → **OAuth consent screen**
4. You should see a **PUBLISH APP** button
5. Click **PUBLISH APP**
6. Click **CONFIRM**
7. ✅ Done! Try Google login again

**Why this works:**
- For non-sensitive scopes (email, profile), Google doesn't require verification
- Publishing makes it available to all Google users
- Testing mode limits you to 100 test users

#### **Option B: Add Yourself as Test User (Alternative)**

If you want to keep it in Testing mode:

1. Go to **OAuth consent screen**
2. Scroll to **Test users** section
3. Click **+ ADD USERS**
4. Add your Google email address
5. Click **SAVE**
6. ✅ Try Google login again

---

## 🧪 Test Everything

### Test 1: Email Registration
```bash
1. Go to: https://www.gradgen.ai/register
2. Fill in form:
   - Full name: Test User
   - Email: your-email@gmail.com
   - Password: test123
   - Confirm: test123
3. Click "Create Account"
4. ✅ Should show: "Registration successful! Check your email..."
5. Check email for verification link
6. Click verification link
7. ✅ Should show: "Email Verified!"
8. Go to login page
9. Login with email and password
10. ✅ Should be logged in to dashboard
```

### Test 2: Google OAuth
```bash
1. Go to: https://www.gradgen.ai/login
2. Click "Google" button
3. ✅ Should go to Google sign-in page (not "Access blocked")
4. Sign in with your Google account
5. If you see "This app isn't verified":
   - Click "Advanced"
   - Click "Go to GradGen (unsafe)"
6. Click "Allow" to grant permissions
7. ✅ Should be redirected back and logged in
8. ✅ Should be on dashboard
```

---

## 📋 Quick Checklist

Before testing, make sure:

**Database:**
- [ ] Ran migration SQL in Railway
- [ ] Saw success message
- [ ] Saw 6 columns in verification query

**Google OAuth:**
- [ ] OAuth consent screen is configured
- [ ] App is Published OR you're added as test user
- [ ] Authorized domains has `gradgen.ai`
- [ ] Scopes include: email, profile, openid
- [ ] Redirect URI is: `https://api.gradgen.ai/api/auth/oauth/google/callback`

**Environment Variables in Railway:**
- [ ] `GOOGLE_CLIENT_ID` is set
- [ ] `GOOGLE_CLIENT_SECRET` is set
- [ ] `RESEND_API_KEY` is set
- [ ] `RESEND_FROM_EMAIL` is set
- [ ] `FRONTEND_URL` is set to `https://www.gradgen.ai`

---

## 🆘 Still Having Issues?

### For Email Registration:
1. Check Railway logs for backend errors
2. Check browser console for frontend errors
3. Verify migration ran successfully:
   ```sql
   SELECT column_name FROM information_schema.columns
   WHERE table_name = 'users' AND column_name = 'email_verified';
   ```
   Should return one row

### For Google OAuth:
1. Check the exact error message
2. Verify OAuth consent screen has all required fields
3. Try in incognito mode (clears cache)
4. Wait 5-10 minutes after making changes
5. Check Railway logs when you click "Google" button

---

## 🎯 Expected Results After Fixes

✅ **Email registration**: Shows success message, sends email
✅ **Email verification**: Link in email works, marks as verified
✅ **Email login**: Works after verification
✅ **Google OAuth**: No "access blocked", redirects to Google sign-in
✅ **Google login**: After sign-in, automatically logs you in

---

## 📞 Next Steps

1. **Fix database first** (5 min)
   - Run migration SQL in Railway
   - Test email registration

2. **Fix Google OAuth** (10 min)
   - Publish app in Google Console
   - Test Google login

3. **Report back** with results! 🎉
