# Test Account Management Scripts

A comprehensive suite of scripts for managing test accounts during development and testing.

---

## 🚀 Quick Start

### Railway SSH Access
```bash
railway ssh --project=11adc61a-7673-4b1a-9f2d-9a0a2f6e2787 --environment=ff70c481-995a-4372-a8f8-a41799540c8a --service=a9702ad1-29b5-45f0-9478-add38dc91d7b
```

Or if you've linked Railway locally:
```bash
railway link
railway ssh
```

---

## 📜 Available Scripts

### 1. **Interactive Test Account Manager** (Recommended!)

The easiest way to manage everything in one place.

```bash
# Interactive menu
python manage_test_accounts.py

# Command-line mode
python manage_test_accounts.py list
python manage_test_accounts.py create free
python manage_test_accounts.py create premium
python manage_test_accounts.py reset admin@gradgen.ai
python manage_test_accounts.py toggle admin@gradgen.ai
```

**Features:**
- ✅ List all test accounts with tier status
- ✅ Create new free/premium accounts (auto-generates unique emails)
- ✅ Reset accounts (clear data + reset tier)
- ✅ Toggle tier (free ↔ premium)
- ✅ Delete accounts permanently
- ✅ Interactive menu or command-line mode

---

### 2. **Create Admin Account**

Create a free tier admin account for testing.

```bash
python create_admin.py
```

**Creates:**
- Email: `admin@gradgen.ai`
- Password: `admin123`
- Tier: Free (unused) - can test free tier flow

**Custom credentials:**
```bash
python create_admin.py your@email.com YourPassword "Your Name"
```

---

### 3. **Create Premium Admin Account**

Create a premium tier admin account for testing.

```bash
python create_premium_admin.py
```

**Creates:**
- Email: `premium@gradgen.ai`
- Password: `premium123`
- Tier: Premium (active) - unlimited generations

**Custom credentials:**
```bash
python create_premium_admin.py your@email.com YourPassword "Your Name"
```

---

### 4. **Reset Account**

Clear all generation data and reset tier to free (unused).

```bash
python reset_account.py admin@gradgen.ai
```

**What it does:**
- ✅ Deletes all generation jobs
- ✅ Deletes all generated images from database
- ✅ Deletes uploaded/generated files from storage (R2/local)
- ✅ Resets `has_used_free_tier = False`
- ✅ Resets `has_purchased_premium = False`
- ✅ Keeps account active and verified

**Perfect for:**
- Testing free tier flow again
- Clearing test data
- Resetting before demo

---

### 5. **Toggle Tier**

Switch account between free and premium tiers.

```bash
# Auto-toggle (premium → free, free → premium)
python toggle_tier.py admin@gradgen.ai

# Set specific tier
python toggle_tier.py admin@gradgen.ai premium
python toggle_tier.py admin@gradgen.ai free
```

**Perfect for:**
- Testing premium features without payment
- Testing locked state (free tier used)
- Switching between tiers quickly

---

## 🎯 Common Testing Workflows

### Test Complete User Journey

```bash
# 1. Create fresh free tier account
python create_admin.py test@gradgen.ai test123 "Test User"

# 2. Login and generate 5 free watermarked photos
# (do this in browser)

# 3. Try to generate again → see pricing modal
# (do this in browser)

# 4. Toggle to premium to test without payment
python toggle_tier.py test@gradgen.ai premium

# 5. Generate 5 more premium unwatermarked photos
# (do this in browser)

# 6. Reset for next test
python reset_account.py test@gradgen.ai
```

---

### Test Premium Features

```bash
# Create premium account
python create_premium_admin.py

# Login as premium@gradgen.ai / premium123
# Generate unlimited unwatermarked photos
# Test download functionality
```

---

### Test Free → Premium Upgrade Flow

```bash
# 1. Reset existing account to free (unused)
python reset_account.py admin@gradgen.ai

# 2. Login and use free tier (5 photos)
# 3. See upgrade prompt
# 4. Complete payment with test card
# 5. Generate premium photos

# Alternative: Skip payment with toggle
python toggle_tier.py admin@gradgen.ai premium
```

---

### Clean Up After Testing

```bash
# List all test accounts
python manage_test_accounts.py list

# Delete old test accounts
python manage_test_accounts.py
# Choose option 6, enter email
```

---

## 🔄 Feature Development Workflow

When pushing new features:

```bash
# 1. Test with fresh free tier account
python reset_account.py admin@gradgen.ai

# 2. Test feature with free tier
# (do testing in browser)

# 3. Toggle to premium
python toggle_tier.py admin@gradgen.ai premium

# 4. Test feature with premium tier
# (do testing in browser)

# 5. Reset for next feature
python reset_account.py admin@gradgen.ai
```

---

## 📊 Account States

### Free Tier (Unused)
- `has_used_free_tier = False`
- `has_purchased_premium = False`
- Dashboard: 🎁 Blue "Free Tier Available" banner
- Can generate: 5 watermarked photos

### Free Tier (Used)
- `has_used_free_tier = True`
- `has_purchased_premium = False`
- Dashboard: 🔒 Gray "Free Tier Used" banner
- Can generate: No (shows pricing modal)

### Premium Tier
- `has_used_free_tier = True`
- `has_purchased_premium = True`
- Dashboard: 👑 Purple "Premium Account" banner
- Can generate: Unlimited unwatermarked photos

---

## 💡 Tips

### Quick Reset During Testing
```bash
# Add to your shell profile for quick access
alias gradgen-reset="railway run python reset_account.py admin@gradgen.ai"
alias gradgen-premium="railway run python toggle_tier.py admin@gradgen.ai premium"
alias gradgen-free="railway run python toggle_tier.py admin@gradgen.ai free"
```

### Interactive Manager for Multiple Actions
```bash
# Use interactive mode when doing multiple operations
python manage_test_accounts.py

# Menu lets you:
# - List accounts
# - Create multiple test accounts
# - Reset/toggle/delete in sequence
# - No need to re-authenticate between commands
```

### Automatic Test Account Creation
```bash
# Create multiple test accounts quickly
for i in {1..5}; do
  python manage_test_accounts.py create free
done
```

---

## ⚠️ Important Notes

- **Data Loss**: Reset and delete operations are permanent
- **Storage Cleanup**: Scripts clean up R2/local storage automatically
- **Referral Codes**: Preserved during reset/toggle operations
- **Superuser Status**: All test accounts are created as superusers
- **Email Verification**: All test accounts are pre-verified

---

## 🐛 Troubleshooting

### "DATABASE_URL not set"
```bash
# Make sure you're running via Railway
railway run python script.py

# Or set locally
export DATABASE_URL="postgresql://..."
python script.py
```

### "User not found"
```bash
# List all accounts first
python manage_test_accounts.py list

# Check exact email spelling
```

### "Failed to delete files"
```bash
# This is usually fine - files may not exist
# Script continues and completes the reset
```

---

## 📝 Script Reference

| Script | Purpose | Use Case |
|--------|---------|----------|
| `manage_test_accounts.py` | All-in-one manager | Most testing scenarios |
| `create_admin.py` | Create free tier admin | Initial setup |
| `create_premium_admin.py` | Create premium admin | Testing premium features |
| `reset_account.py` | Clear data + reset tier | Clean slate testing |
| `toggle_tier.py` | Switch tier | Quick tier changes |

---

## 🎉 Example Session

```bash
# SSH into Railway
railway ssh

# Start interactive manager
python manage_test_accounts.py

# Menu appears:
# 1. List all test accounts
# 2. Create new free tier account
# 3. Create new premium tier account
# 4. Reset account
# 5. Toggle account tier
# 6. Delete account
# 7. Exit

# Choose 1 to see all accounts
1

# 📋 Test Accounts:
# ================
#
# 📧 admin@gradgen.ai
#    Tier: Free (used)
#    Jobs: 3
#
# 📧 premium@gradgen.ai
#    Tier: Premium
#    Jobs: 7

# Choose 4 to reset admin account
4
# Enter email: admin@gradgen.ai
# ✅ Deleted 3 jobs and 8 files
# ✅ Reset to Free (unused) tier

# Choose 7 to exit
7
# 👋 Goodbye!
```

---

Happy testing! 🚀
