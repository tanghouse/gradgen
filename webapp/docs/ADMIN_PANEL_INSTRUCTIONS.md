# GradGen Admin Panel - Browser-Based Account Management

## ✅ The EASIEST Way to Manage Accounts

Since Railway database connections and CLI tools are having issues, use this **browser-based method** that works through the deployed backend API.

---

## Quick Reset (30 Seconds)

### Reset Your Admin Account

1. **Login** to https://gradgen-production.up.railway.app
2. **Press F12** (or Cmd+Option+I on Mac)
3. **Go to Console tab**
4. **Paste this code**:

```javascript
// Reset account to fresh state
fetch('https://gradgen-production.up.railway.app/api/users/me', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    has_used_free_tier: false,
    has_purchased_premium: false,
    premium_generations_used: 0,
    referral_discount_eligible: false
  })
}).then(r => r.json()).then(data => {
  console.log('✅ Account Reset!', data);
  console.log('\n📊 Previous State:');
  console.log(`   has_used_free_tier: ${data.has_used_free_tier}`);
  console.log(`   has_purchased_premium: ${data.has_purchased_premium}`);
  console.log(`   premium_generations_used: ${data.premium_generations_used || 0}`);
  console.log('\n💡 Refresh the page to see updated tier status!');
  setTimeout(() => location.reload(), 2000);
});
```

5. **Wait 2 seconds** - page will auto-reload
6. **Done!** You're back to "Free (unused)" tier

---

## View Account Status

### Check Your Tier and Generation Count

```javascript
fetch('https://gradgen-production.up.railway.app/api/generation/tier-status', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
}).then(r => r.json()).then(data => {
  console.log('📊 Your Account Status:');
  console.log('='.repeat(50));
  console.log(`Tier: ${data.tier}`);
  console.log(`Free Tier Used: ${data.has_used_free_tier}`);
  console.log(`Premium Purchased: ${data.has_purchased_premium}`);
  console.log(`Premium Generations Used: ${data.premium_generations_used}`);
  console.log(`Premium Generations Remaining: ${data.premium_generations_remaining}`);
  console.log(`Can Generate: ${data.can_generate ? '✅' : '❌'}`);
  console.log(`Message: ${data.message}`);
});
```

---

## Toggle to Premium (Without Payment)

### Give Yourself Premium Access for Testing

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
}).then(r => r.json()).then(data => {
  console.log('✅ Upgraded to Premium!', data);
  location.reload();
});
```

---

## Set Premium to Exhausted State

### Test the "Premium Exhausted" Banner

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
    premium_generations_used: 2  // Exhausted!
  })
}).then(r => r.json()).then(data => {
  console.log('✅ Premium Exhausted!', data);
  location.reload();
});
```

---

## View All Your Generation Jobs

### See Job History

```javascript
fetch('https://gradgen-production.up.railway.app/api/generation/jobs?limit=50', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
}).then(r => r.json()).then(jobs => {
  console.log(`📋 Your Generation Jobs (${jobs.length} total):`);
  console.log('='.repeat(50));

  jobs.forEach((job, i) => {
    console.log(`\n${i+1}. Job #${job.id} - ${job.status}`);
    console.log(`   University: ${job.university} (${job.degree_level})`);
    console.log(`   Tier: ${job.tier || 'N/A'}`);
    console.log(`   Watermarked: ${job.is_watermarked ? 'Yes' : 'No'}`);
    console.log(`   Images: ${job.completed_images}/${job.total_images}`);
    console.log(`   Created: ${new Date(job.created_at).toLocaleString()}`);
  });
});
```

---

## Testing Workflows

### Complete Free → Premium → Exhausted Flow

```javascript
// Helper function for testing
async function testFlow() {
  const token = localStorage.getItem('token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  console.log('🧪 Starting Test Flow...\n');

  // Step 1: Reset to Fresh
  console.log('1️⃣ Resetting to Fresh State...');
  await fetch('https://gradgen-production.up.railway.app/api/users/me', {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      has_used_free_tier: false,
      has_purchased_premium: false,
      premium_generations_used: 0
    })
  }).then(r => r.json());
  console.log('   ✅ Now: Free (unused)\n');

  await new Promise(r => setTimeout(r, 1000));

  // Step 2: Use Free Tier
  console.log('2️⃣ Simulating Free Tier Used...');
  await fetch('https://gradgen-production.up.railway.app/api/users/me', {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      has_used_free_tier: true
    })
  }).then(r => r.json());
  console.log('   ✅ Now: Free (used)\n');

  await new Promise(r => setTimeout(r, 1000));

  // Step 3: Purchase Premium
  console.log('3️⃣ Simulating Premium Purchase...');
  await fetch('https://gradgen-production.up.railway.app/api/users/me', {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      has_purchased_premium: true,
      premium_generations_used: 0
    })
  }).then(r => r.json());
  console.log('   ✅ Now: Premium (2/2 remaining)\n');

  await new Promise(r => setTimeout(r, 1000));

  // Step 4: Use 1 Premium Generation
  console.log('4️⃣ Simulating 1st Premium Generation...');
  await fetch('https://gradgen-production.up.railway.app/api/users/me', {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      premium_generations_used: 1
    })
  }).then(r => r.json());
  console.log('   ✅ Now: Premium (1/2 remaining)\n');

  await new Promise(r => setTimeout(r, 1000));

  // Step 5: Use 2nd Premium Generation
  console.log('5️⃣ Simulating 2nd Premium Generation...');
  await fetch('https://gradgen-production.up.railway.app/api/users/me', {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      premium_generations_used: 2
    })
  }).then(r => r.json());
  console.log('   ✅ Now: Premium (exhausted)\n');

  console.log('🎉 Test Flow Complete! Reload page to see final state.');
  setTimeout(() => location.reload(), 3000);
}

// Run it!
testFlow();
```

---

## Copy Your JWT Token

### For API Testing Tools (Postman, curl)

```javascript
console.log('🔑 Your JWT Token:');
console.log(localStorage.getItem('token'));
console.log('\nCopy this token for use in Postman or curl!');
```

Then use in curl:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  https://gradgen-production.up.railway.app/api/generation/tier-status
```

---

## Advantages of Browser Method

✅ **No CLI Setup** - Works in any browser
✅ **No Database Credentials** - Uses your login token
✅ **Instant Results** - Auto-refreshes page
✅ **Safe** - Only affects your account
✅ **Easy Copy-Paste** - No typing commands
✅ **Works Anywhere** - Mobile, desktop, any device

---

## Quick Reference

| Task | Code Snippet |
|------|--------------|
| Reset to Fresh | Update with `has_used_free_tier: false, has_purchased_premium: false, premium_generations_used: 0` |
| Make Premium | Update with `has_purchased_premium: true, premium_generations_used: 0` |
| Exhaust Premium | Update with `premium_generations_used: 2` |
| Check Status | GET `/api/generation/tier-status` |
| View Jobs | GET `/api/generation/jobs?limit=50` |

---

## Troubleshooting

### "401 Unauthorized"
- Your token expired
- Logout and login again
- Re-run the command

### "Not Found"
- Check the API URL is correct
- Backend might be deploying

### Changes Not Showing
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear cache and reload

---

## Why This Works When Railway CLI Doesn't

1. **Uses Deployed API** - Goes through your working backend
2. **No Direct DB Access** - Uses app's ORM and validation
3. **Standard HTTP** - Works from any device
4. **Token-Based Auth** - Secure and simple

---

## Bookmark This!

Save these snippets in a text file for quick access:

```bash
# Create: ~/gradgen-admin-snippets.txt
# Paste browser console code snippets
# Copy-paste when needed
```

---

## Next Steps

1. **Open browser** to https://gradgen-production.up.railway.app
2. **Login** with admin@gradgen.ai
3. **Open Console** (F12)
4. **Paste reset code** from above
5. **Start testing** from fresh state!

Easy! 🎉
