# GradGen Account Management Guide

## Overview

The `manage_test_accounts.py` script is your **all-in-one tool** for managing user accounts in the database. It supports both **interactive menu mode** and **command-line mode**.

---

## Quick Start

### Interactive Mode (Recommended)

```bash
cd backend
railway run python manage_test_accounts.py
```

This launches an interactive menu:

```
================================================================================
🧪 GradGen Test Account Manager
================================================================================

1. List all test accounts
2. Create new free tier account
3. Create new premium tier account
4. Reset account (clear data, reset to free tier)
5. Toggle account tier (free ↔ premium)
6. Delete account
7. Exit

Select option (1-7):
```

---

## Command Reference

### 1. List All Accounts

**Interactive:**
```bash
railway run python manage_test_accounts.py
# Select option 1
```

**Command-line:**
```bash
railway run python manage_test_accounts.py list
```

**Output Example:**
```
📋 Test Accounts:
====================================================================================================

📧 admin@gradgen.ai
   Name: Admin User
   ID: 1
   Tier: Premium (1/2 remaining)
   Jobs: 3
   Verified: ✅
   Referral Code: ADMIN123

📧 test_user@gradgen.ai
   Name: Test User
   ID: 2
   Tier: Free (used)
   Jobs: 1
   Verified: ✅
   Referral Code: TEST456
```

### Tier Status Explained:
- **Free (unused)**: Brand new account, 5 watermarked photos available
- **Free (used)**: Used free tier, needs to upgrade
- **Premium (2/2 remaining)**: Just purchased premium, 2 generations left
- **Premium (1/2 remaining)**: Used 1 premium generation, 1 left
- **Premium (exhausted)**: Used all 2 premium generations

---

### 2. Create Test Account

**Interactive:**
```bash
railway run python manage_test_accounts.py
# Select option 2 (free) or 3 (premium)
```

**Command-line:**
```bash
# Create free tier account
railway run python manage_test_accounts.py create free

# Create premium tier account
railway run python manage_test_accounts.py create premium
```

**Output:**
```
🆕 Creating new FREE test account...

✅ Account created!
   Email: free_test@gradgen.ai
   Password: free123
   Tier: FREE
```

**What it creates:**
- Unique email (auto-increments: `free_test@gradgen.ai`, `free_test1@gradgen.ai`, etc.)
- Simple password: `{tier}123` (e.g., `free123` or `premium123`)
- Email verified by default
- Superuser flag enabled (for testing)
- Referral code auto-generated

---

### 3. Reset Account

**⚠️ Important:** Reset clears ALL generation jobs and files but keeps the account!

**Interactive:**
```bash
railway run python manage_test_accounts.py
# Select option 4
# Enter: admin@gradgen.ai
```

**Command-line:**
```bash
railway run python manage_test_accounts.py reset admin@gradgen.ai
```

**What it does:**
1. Deletes all generation jobs
2. Deletes all uploaded/generated images from storage
3. Resets tier flags:
   - `has_used_free_tier = FALSE`
   - `has_purchased_premium = FALSE`
   - `premium_generations_used = 0`
4. Account returns to "Free (unused)" state

**Output:**
```
🗑️  Resetting admin@gradgen.ai...
   ✅ Deleted 5 jobs and 25 files
   ✅ Reset to Free (unused) tier
```

**Perfect for:**
- ✅ Testing the complete user journey from fresh account
- ✅ Clearing test data while keeping login credentials
- ✅ Re-running test scenarios

---

### 4. Toggle Tier

**Interactive:**
```bash
railway run python manage_test_accounts.py
# Select option 5
# Enter: test_user@gradgen.ai
```

**Command-line:**
```bash
railway run python manage_test_accounts.py toggle test_user@gradgen.ai
```

**What it does:**
- **Free → Premium**: Sets `has_purchased_premium = TRUE`, `has_used_free_tier = TRUE`
- **Premium → Free**: Sets `has_purchased_premium = FALSE`

**Output:**
```
🔄 Toggling test_user@gradgen.ai from Free to Premium...
   ✅ Now Premium tier
```

**Note:** This does NOT delete jobs/files, only changes tier status!

---

### 5. Delete Account

**⚠️ DANGER:** This permanently deletes everything!

**Interactive:**
```bash
railway run python manage_test_accounts.py
# Select option 6
# Enter: old_test@gradgen.ai
# Type: DELETE (to confirm)
```

**Command-line:**
```bash
# Not available in CLI mode for safety
# Must use interactive mode
```

**What it deletes:**
1. All generation jobs
2. All uploaded/generated files from storage
3. All generated images records
4. The user account itself

**Confirmation required:**
```
⚠️  WARNING: Deleting old_test@gradgen.ai permanently!
   This will delete:
   - User account
   - All generation jobs
   - All uploaded/generated files

   Type 'DELETE' to confirm:
   > DELETE
   ✅ Account deleted
```

---

## Common Use Cases

### Reset Your Admin Account for Testing

```bash
cd backend
railway run python manage_test_accounts.py reset admin@gradgen.ai
```

Then login and test the complete flow:
1. Free tier generation (5 watermarked photos)
2. Premium purchase
3. First premium generation (5 unwatermarked photos)
4. Second premium generation (5 unwatermarked photos)
5. Premium exhausted state

---

### Create Test Users for Different Scenarios

```bash
# Create fresh free tier user
railway run python manage_test_accounts.py create free
# Email: free_test@gradgen.ai
# Password: free123

# Create premium user
railway run python manage_test_accounts.py create premium
# Email: premium_test@gradgen.ai
# Password: premium123
```

---

### View All Accounts and Their Status

```bash
railway run python manage_test_accounts.py list
```

Quick check:
- Who has used free tier?
- Who has premium?
- How many generations remaining?
- Any accounts stuck?

---

### Quick Tier Status Change (No Data Loss)

```bash
# Give test user premium access without payment
railway run python manage_test_accounts.py toggle test_user@gradgen.ai

# Verify
railway run python manage_test_accounts.py list
```

---

## Troubleshooting

### Error: "DATABASE_URL not set"

**Solution:**
Always use `railway run` to ensure Railway environment variables are loaded:

```bash
# ✅ Correct
railway run python manage_test_accounts.py

# ❌ Wrong
python manage_test_accounts.py
```

---

### Error: "No test accounts found"

The script looks for users with `is_superuser = True`.

**Solution:**
Check if your admin account has the superuser flag:

```bash
railway run python -c "
from app.db.database import SessionLocal
from app.models import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@gradgen.ai').first()
print(f'Superuser: {user.is_superuser if user else \"Not found\"}')
"
```

If not a superuser, update:
```sql
UPDATE users SET is_superuser = TRUE WHERE email = 'admin@gradgen.ai';
```

---

### Files Not Deleting from Storage

The script uses `storage_service.delete_file()` which works with:
- Local filesystem (development)
- Cloudflare R2 (production)

If files remain, check:
1. R2 credentials in Railway environment
2. File permissions
3. Storage service logs

---

## Script Features

### ✅ Safe Operations
- Confirmation required for destructive actions (delete account)
- Rollback on errors
- Clear feedback at each step

### ✅ Smart Auto-Incrementing
- Automatically finds next available email (`free_test1`, `free_test2`, etc.)
- No manual email management needed

### ✅ Complete Cleanup
- Deletes files from storage (not just database)
- Removes all foreign key relationships
- Leaves no orphaned data

### ✅ Referral Code Integration
- Auto-generates referral codes for new accounts
- Preserves codes during tier toggles
- Resets codes during full account reset

---

## Best Practices

### 1. Use Reset (Not Delete) for Testing
```bash
# ✅ Good: Preserves account, quick reset
railway run python manage_test_accounts.py reset admin@gradgen.ai

# ❌ Avoid: Loses account, need to recreate
railway run python manage_test_accounts.py (then option 6)
```

### 2. List Before Making Changes
```bash
# Always check current state first
railway run python manage_test_accounts.py list

# Then make changes
railway run python manage_test_accounts.py reset admin@gradgen.ai
```

### 3. Use Descriptive Test Emails
When creating custom accounts, use clear names:
```bash
# Good
free_tier_test@gradgen.ai
premium_exhausted_test@gradgen.ai
mobile_test@gradgen.ai

# Confusing
test1@gradgen.ai
user@gradgen.ai
```

---

## Integration with Testing Checklist

This script pairs perfectly with `TESTING_CHECKLIST.md`:

**Before each test phase:**
```bash
railway run python manage_test_accounts.py reset admin@gradgen.ai
```

**Test Sequence:**
1. Reset account → Fresh state
2. Run free tier tests (1-4)
3. Toggle to premium → Run premium tests (8-14)
4. Reset again → Run mobile tests (15-16)

---

## Alternative: Quick Reset via API

If Railway CLI is slow, use the browser console method:

```javascript
fetch('https://gradgen-production.up.railway.app/api/admin/reset-account', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
}).then(r => r.json()).then(console.log);
```

*(Note: The admin API endpoint needs to be deployed first)*

---

## Summary

**Primary Tool:** `manage_test_accounts.py`

**Most Common Commands:**

```bash
# Daily use
railway run python manage_test_accounts.py list
railway run python manage_test_accounts.py reset admin@gradgen.ai

# Setup
railway run python manage_test_accounts.py create free
railway run python manage_test_accounts.py create premium

# Quick tier change
railway run python manage_test_accounts.py toggle test@gradgen.ai
```

**Interactive Mode:** Best for exploratory work, safe with confirmations
**CLI Mode:** Best for scripts, automation, quick resets

---

## Quick Reference Card

| Task | Command |
|------|---------|
| List accounts | `railway run python manage_test_accounts.py list` |
| Reset account | `railway run python manage_test_accounts.py reset EMAIL` |
| Create free account | `railway run python manage_test_accounts.py create free` |
| Create premium account | `railway run python manage_test_accounts.py create premium` |
| Toggle tier | `railway run python manage_test_accounts.py toggle EMAIL` |
| Interactive menu | `railway run python manage_test_accounts.py` |
