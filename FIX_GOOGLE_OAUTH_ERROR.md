# Fix Google OAuth "Access Blocked" Error

## 🚨 The Error
"Access blocked: GradGen's request is invalid"

This happens when the OAuth consent screen is not properly configured.

---

## ✅ Step-by-Step Fix

### Step 1: Go to Google Cloud Console
1. Visit https://console.cloud.google.com/
2. Make sure you're in the correct project (TangHouse/GradGen)

### Step 2: Check OAuth Consent Screen Status
1. Go to **APIs & Services** → **OAuth consent screen**
2. Look at the status - it should show:
   - **Publishing status**: Testing or Published
   - **User type**: External

### Step 3: Verify Consent Screen Configuration

Click **EDIT APP** and verify each section:

#### **OAuth consent screen (Page 1)**
```
✅ App name: TangHouse (or GradGen)
✅ User support email: [your-email@gmail.com]
✅ App logo: (optional)
✅ App domain - Application home page: https://gradgen.ai
✅ Authorized domains: gradgen.ai
✅ Developer contact information: [your-email@gmail.com]
```

**IMPORTANT**: Make sure "Authorized domains" has `gradgen.ai` (no https://, no www.)

#### **Scopes (Page 2)**
Click **ADD OR REMOVE SCOPES** and make sure you have:
```
✅ .../auth/userinfo.email (View your email address)
✅ .../auth/userinfo.profile (See your personal info)
✅ openid (Associate you with your personal info on Google)
```

These are NON-SENSITIVE scopes and don't require verification.

#### **Test users (Page 3)**
```
✅ Add your email address
✅ Add any other test users' emails
```

In "Testing" mode, only these users can sign in.

### Step 4: Save Everything
1. Click through all pages
2. Click **SAVE AND CONTINUE** on each page
3. On the final page, click **BACK TO DASHBOARD**

### Step 5: Check Publishing Status

**Option A: Keep in Testing Mode (Recommended for now)**
- In "Testing" status, up to 100 test users can sign in
- No verification needed from Google
- Users will see a warning but can proceed

**Option B: Publish Your App**
1. Click **PUBLISH APP**
2. Click **CONFIRM**
3. For non-sensitive scopes, your app is published immediately
4. No Google verification needed

---

## 🔍 Common Issues

### Issue: "Authorized domains" error
**Fix:**
- Add ONLY the domain: `gradgen.ai`
- Do NOT include:
  - ❌ `https://gradgen.ai`
  - ❌ `www.gradgen.ai`
  - ❌ `api.gradgen.ai`
- Just: ✅ `gradgen.ai`

### Issue: Scopes not showing up
**Fix:**
1. Go to **Scopes** page
2. Click **ADD OR REMOVE SCOPES**
3. Search for: `userinfo.email`
4. Check the boxes for:
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
   - `openid`
5. Click **UPDATE**
6. Click **SAVE AND CONTINUE**

### Issue: Can't find OAuth consent screen
**Fix:**
1. Make sure you selected the correct project at the top
2. Go to: **APIs & Services** → **OAuth consent screen**
3. If it says "Configure consent screen", click it and follow the wizard

---

## 🎯 Quick Checklist

Before testing again, verify:

- [ ] OAuth consent screen is configured (not blank)
- [ ] User type is "External"
- [ ] App name is filled in
- [ ] User support email is filled in
- [ ] Authorized domains includes `gradgen.ai`
- [ ] Scopes include: email, profile, openid
- [ ] Test users includes your email (if in Testing mode)
- [ ] All pages saved with "SAVE AND CONTINUE"

---

## 🧪 Test Again

1. Go to https://www.gradgen.ai/login
2. Click **Google** button
3. You should see Google sign-in page
4. If in Testing mode, you might see:
   - "This app isn't verified"
   - Click **Advanced**
   - Click **Go to GradGen (unsafe)**
5. Grant permissions (email, profile)
6. ✅ You should be redirected back and logged in

---

## 📸 What You Should See in Google Cloud Console

**OAuth consent screen page should show:**
```
Publishing status: Testing (or Published)
App name: TangHouse
User type: External
Scopes: 3 scopes (email, profile, openid)
Test users: 1 (or more)
```

**Credentials page should show:**
```
OAuth 2.0 Client IDs
Name: TangHouse Web Client
Type: Web application
Client ID: xxxxx.apps.googleusercontent.com
Authorized redirect URIs:
  - https://api.gradgen.ai/api/auth/oauth/google/callback
```

---

## 🆘 Still Not Working?

If you're still getting "Access blocked" after following all steps:

1. **Delete and recreate OAuth credentials:**
   - Go to Credentials
   - Delete the old OAuth client
   - Create a new one
   - Make sure redirect URI is exact

2. **Wait a few minutes:**
   - OAuth changes can take 5-10 minutes to propagate

3. **Try incognito mode:**
   - Clear cache or use incognito window

4. **Check the exact error message:**
   - Screenshot the error
   - Look for specific details about what's invalid
