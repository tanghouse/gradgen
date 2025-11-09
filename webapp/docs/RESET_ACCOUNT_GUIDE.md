# How to Reset Your Account for Testing

## Option 1: Using Browser Console (Easiest)

1. **Login to your account** at https://gradgen-production.up.railway.app (or your frontend URL)

2. **Open browser DevTools**:
   - Chrome/Edge: Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - Safari: Enable Developer Menu first, then `Cmd+Option+I`

3. **Go to Console tab**

4. **Copy and paste this code** into the console:

```javascript
// Reset account for testing
async function resetAccount() {
  const token = localStorage.getItem('token');

  if (!token) {
    console.error('❌ No token found. Please login first!');
    return;
  }

  console.log('🔄 Resetting account...');

  try {
    const response = await fetch('https://gradgen-production.up.railway.app/api/admin/reset-account', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ Reset failed:', error);
      return;
    }

    const result = await response.json();
    console.log('✅ Account reset successfully!');
    console.log('\n📊 Previous State:', result.previous_state);
    console.log('📊 New State:', result.new_state);
    console.log('📈 Generation History:', result.generation_history);
    console.log('\n💡 Refresh the page to see updated tier status!');

    return result;
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

// Run the reset
resetAccount();
```

5. **Press Enter** to run the code

6. **Expected output**:
```
🔄 Resetting account...
✅ Account reset successfully!

📊 Previous State: {
  has_used_free_tier: true,
  has_purchased_premium: true,
  premium_generations_used: 2,
  referral_discount_eligible: false
}
📊 New State: {
  has_used_free_tier: false,
  has_purchased_premium: false,
  premium_generations_used: 0,
  referral_discount_eligible: false
}
📈 Generation History: {
  total_jobs: 5,
  free_tier_jobs: 2,
  premium_tier_jobs: 3
}

💡 Refresh the page to see updated tier status!
```

7. **Refresh the page** (F5 or Cmd+R) to see your account reset to fresh state

---

## Option 2: Using curl (Command Line)

### Step 1: Get your JWT token

First, login via browser and open DevTools Console, then run:

```javascript
console.log(localStorage.getItem('token'));
```

Copy the token (it will be a long string starting with "eyJ...")

### Step 2: Run curl command

Replace `YOUR_TOKEN_HERE` with your actual token:

```bash
curl -X POST https://gradgen-production.up.railway.app/api/admin/reset-account \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  | python3 -m json.tool
```

### Expected Response:

```json
{
  "message": "Account successfully reset for testing. All tier flags cleared.",
  "email": "admin@gradgen.ai",
  "previous_state": {
    "has_used_free_tier": true,
    "has_purchased_premium": true,
    "premium_generations_used": 2,
    "referral_discount_eligible": false
  },
  "new_state": {
    "has_used_free_tier": false,
    "has_purchased_premium": false,
    "premium_generations_used": 0,
    "referral_discount_eligible": false
  },
  "generation_history": {
    "total_jobs": 5,
    "free_tier_jobs": 2,
    "premium_tier_jobs": 3
  }
}
```

---

## Option 3: Using Postman/Insomnia (API Client)

1. **Create a new POST request**:
   - URL: `https://gradgen-production.up.railway.app/api/admin/reset-account`
   - Method: `POST`

2. **Add Authorization header**:
   - Key: `Authorization`
   - Value: `Bearer YOUR_TOKEN_HERE`

3. **Send the request**

4. **View the response** with your account's before/after state

---

## What Gets Reset

When you reset your account:

✅ **Reset (Cleared)**:
- `has_used_free_tier`: FALSE
- `has_purchased_premium`: FALSE
- `premium_generations_used`: 0
- `referral_discount_eligible`: FALSE

✅ **Preserved**:
- All previous generation jobs
- Generation history (free tier jobs, premium jobs)
- User credentials and profile
- Payment records

---

## After Reset

Your account will be in "Fresh User" state:

- **Dashboard Banner**: Shows "Free Tier Available" 🎁
- **Tier Status**: `tier: "free"`
- **Can Generate**: 5 watermarked photos available
- **Previous Jobs**: Still visible in dashboard for reference

Now you can test the complete flow from free tier → premium purchase → premium exhaustion!

---

## Troubleshooting

### ❌ "No token found. Please login first!"
- Make sure you're logged in
- Refresh the page and try again

### ❌ 401 Unauthorized
- Your token has expired
- Logout and login again to get a fresh token

### ❌ Network Error
- Check that the backend is online: https://gradgen-production.up.railway.app/
- Should return: `{"name":"GradGen API","version":"0.1.0","status":"online"}`

---

## Quick Start

**Fastest way to reset:**

1. Login to https://gradgen-production.up.railway.app
2. Press F12 (DevTools)
3. Go to Console tab
4. Paste the resetAccount() function (from Option 1 above)
5. Press Enter
6. Refresh page (F5)
7. Start testing! 🎉
