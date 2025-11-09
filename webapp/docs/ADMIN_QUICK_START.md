# GradGen Admin - Quick Start Guide

## 🎯 The Easiest Way to Manage & Test Accounts

Railway CLI isn't working due to database connection restrictions. **Use the browser console instead** - it's actually easier!

---

## ⚡ Reset Your Account (30 Seconds)

### Step-by-Step:

1. **Open** https://gradgen-production.up.railway.app
2. **Login** with `admin@gradgen.ai`
3. **Press F12** (DevTools)
4. **Click Console tab**
5. **Paste this**:

```javascript
fetch('https://gradgen-production.up.railway.app/api/users/me', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    has_used_free_tier: false,
    has_purchased_premium: false,
    premium_generations_used: 0
  })
}).then(r => r.json()).then(d => {console.log('✅ Reset!', d); location.reload();});
```

6. **Press Enter**
7. **Done!** You're back to "Free (unused)" tier

---

## 📋 All Admin Commands

### Check Your Status

```javascript
fetch('https://gradgen-production.up.railway.app/api/generation/tier-status', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
}).then(r => r.json()).then(console.log);
```

### Give Yourself Premium

```javascript
fetch('https://gradgen-production.up.railway.app/api/users/me', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    has_purchased_premium: true,
    has_used_free_tier: true,
    premium_generations_used: 0
  })
}).then(r => r.json()).then(d => {console.log('✅ Premium!', d); location.reload();});
```

### Test Premium Exhausted

```javascript
fetch('https://gradgen-production.up.railway.app/api/users/me', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    has_purchased_premium: true,
    premium_generations_used: 2
  })
}).then(r => r.json()).then(d => {console.log('✅ Exhausted!', d); location.reload();});
```

---

## 📚 Documentation Files Created

All in `/webapp/backend/`:

1. **`ADMIN_PANEL_INSTRUCTIONS.md`** ⭐ Browser-based admin guide (RECOMMENDED)
2. **`ACCOUNT_MANAGEMENT_GUIDE.md`** - CLI guide (if Railway CLI works later)
3. **`admin.py`** - Standalone Python script (database connection issues)
4. **`manage_test_accounts.py`** - Full-featured tool (needs Railway CLI)

**Use #1 (browser method) - it works right now!**

---

## 🧪 Testing Workflow

### Complete Test Sequence:

```javascript
// 1. Reset to fresh
// (paste reset code from above)

// 2. Test free tier
//    - Go to /generate
//    - Upload photo, select university
//    - Generate 5 watermarked photos
//    - Check dashboard shows "Free (used)"

// 3. Toggle to premium
// (paste "Give Yourself Premium" code)

// 4. Test 1st premium generation
//    - Generate 5 unwatermarked photos
//    - Check dashboard shows "Premium (1/2 remaining)"

// 5. Test 2nd premium generation
//    - Generate 5 more unwatermarked photos
//    - Check dashboard shows "Premium (exhausted)"

// 6. Verify can't generate more
//    - Try to go to /generate
//    - Should see error or blocked
```

---

## 🔧 Why Railway CLI Doesn't Work

**Issue:** `railway run python manage_test_accounts.py`

**Error:** `No such file or directory (os error 2)`

**Root Cause:**
- Railway CLI not linked to backend service
- Database rejecting external connections
- Multiple environment variables required

**Solution:**
Use browser console method instead! ✅

---

## ✅ Ready to Test!

You now have:

- ✅ Browser-based admin panel
- ✅ 30-test comprehensive checklist
- ✅ Mobile responsive UI fixes
- ✅ Original photos in dashboard
- ✅ Premium tier with 2-generation limit
- ✅ All tier status banners working

**Just reset your account and start testing!** 🎉

---

## 🆘 Need Help?

### Database Access Issues?
- Use browser method instead of CLI
- All operations go through deployed API
- No direct database connection needed

### Token Expired?
- Logout and login again
- Token in localStorage gets refreshed

### Changes Not Showing?
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Or use `location.reload(true)` in console
