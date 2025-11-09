# GradGen Testing Checklist

## Test Environment Setup

### 1. Reset Admin Account
```bash
cd backend
poetry run python reset_admin_account.py YOUR_EMAIL@example.com
```

This will reset your account to:
- `has_used_free_tier`: FALSE
- `has_purchased_premium`: FALSE
- `premium_generations_used`: 0
- Previous generation jobs preserved for reference

---

## Feature Tests

### A. Free Tier Flow (First-Time User)

#### Test 1: Free Tier Status Display
**Steps:**
1. Login to your account
2. Go to `/dashboard`

**Expected Results:**
- Banner shows: "Free Tier Available" with 🎁 emoji
- Banner color: Blue gradient (from-blue-600 to-cyan-600)
- Description: "5 free watermarked photos available • Try it now!"
- Button: "Try Free Tier"

#### Test 2: Free Tier Generation
**Steps:**
1. Click "Try Free Tier" or go to `/generate`
2. Upload a portrait photo
3. Select university and degree level
4. Click "Generate Photos"

**Expected Results:**
- Generation job created with `tier: 'free'`
- Job creates 5 images
- All images are watermarked (`is_watermarked: true`)
- Backend sets `has_used_free_tier: TRUE` after job completes

#### Test 3: Free Tier Exhausted Status
**Steps:**
1. Wait for free tier generation to complete
2. Return to `/dashboard`

**Expected Results:**
- Banner shows: "Free Tier Used" with 🔒 emoji
- Banner color: Gray gradient (from-gray-600 to-gray-700)
- Description: "Upgrade to Premium to generate more professional photos"
- Button: "Upgrade to Premium"

#### Test 4: Dashboard Photo Display (Free Tier)
**Steps:**
1. View completed free tier job in dashboard

**Expected Results:**
- Grid layout: 5 columns on desktop (lg:grid-cols-5)
- Each card shows BOTH original and generated photos stacked vertically
- Original photo labeled "Original" with gray background
- Generated photo labeled "Generated" with primary color background
- Watermark indicator: "(Watermarked - Free Tier)" in orange text
- Download button available for each photo

---

### B. Premium Purchase Flow

#### Test 5: Premium Upgrade (No Promo Code)
**Steps:**
1. From dashboard or generate page, click "Upgrade to Premium"
2. Don't enter any promo code
3. Click "Proceed to Checkout"

**Expected Results:**
- Pricing shows: £39.99 (base price)
- No discount message shown
- Stripe checkout opens with £39.99

#### Test 6: Premium Upgrade (With Promo Code)
**Steps:**
1. Click "Upgrade to Premium"
2. Enter promo code: "LAUNCH20" (if you created one)
3. Click "Proceed to Checkout"

**Expected Results:**
- Pricing shows discounted price (e.g., £31.99 if 20% off)
- Discount message displayed
- Stripe checkout opens with discounted price

#### Test 7: Complete Premium Purchase
**Steps:**
1. In Stripe checkout, use test card: `4242 4242 4242 4242`
2. Expiry: Any future date (e.g., 12/25)
3. CVC: Any 3 digits (e.g., 123)
4. Complete payment

**Expected Results:**
- Stripe webhook processes payment
- Database updated: `has_purchased_premium: TRUE`
- User redirected back to app
- Dashboard banner updates to Premium status

---

### C. Premium Tier Flow

#### Test 8: Premium Status Display (2 Generations Remaining)
**Steps:**
1. After purchasing premium, go to `/dashboard`

**Expected Results:**
- Banner shows: "Premium Account" with 👑 emoji
- Banner color: Purple gradient (from-purple-600 to-indigo-600)
- Description: "2 generations remaining • 5 photos per generation • No watermarks"
- Button: "Generate Photos"

#### Test 9: First Premium Generation
**Steps:**
1. Click "Generate Photos"
2. Upload a portrait photo
3. Select university and degree level
4. Click "Generate Photos"

**Expected Results:**
- Generation job created with `tier: 'premium'`
- Job creates 5 images
- All images WITHOUT watermark (`is_watermarked: false`)
- Backend increments `premium_generations_used: 1`

#### Test 10: Premium Status Update (1 Generation Remaining)
**Steps:**
1. After first premium generation completes
2. Return to `/dashboard`

**Expected Results:**
- Banner still shows: "Premium Account" with 👑 emoji
- Description updates to: "1 generation remaining • 5 photos per generation • No watermarks"
- Button: "Generate Photos" still available

#### Test 11: Second Premium Generation
**Steps:**
1. Click "Generate Photos" again
2. Upload another portrait photo
3. Select university and degree level
4. Click "Generate Photos"

**Expected Results:**
- Second generation job created with `tier: 'premium'`
- Job creates 5 images without watermarks
- Backend increments `premium_generations_used: 2`

#### Test 12: Premium Exhausted Status
**Steps:**
1. After second premium generation completes
2. Return to `/dashboard`

**Expected Results:**
- Banner shows: "All Generations Used" with ✅ emoji
- Banner color: Green gradient (from-green-600 to-teal-600)
- Description: "Thank you for using GradGen! You've used all your generations."
- No button displayed (cannot generate more)

#### Test 13: Cannot Generate After Premium Exhausted
**Steps:**
1. Try to access `/generate` page

**Expected Results:**
- Tier status API returns `can_generate: false`
- Generate page should show error or redirect
- API endpoint `/generate-tier` returns 403 Forbidden if attempted

#### Test 14: Dashboard Photo Display (Premium Tier)
**Steps:**
1. View completed premium jobs in dashboard

**Expected Results:**
- Grid layout: 5 columns on desktop (lg:grid-cols-5)
- Each card shows BOTH original and generated photos
- Original photo labeled "Original"
- Generated photo labeled "Generated"
- Watermark indicator: "(Premium - No Watermark)" in green text
- Download button available

---

### D. Mobile Responsiveness

#### Test 15: Mobile Navbar (Squashed Buttons Fixed)
**Steps:**
1. Open website on phone or use browser DevTools mobile view
2. View navbar

**Expected Results:**
- On mobile (< md breakpoint):
  - Only logo and hamburger menu visible
  - Hamburger icon (☰) on right side
- Click hamburger menu:
  - Menu slides down vertically
  - All nav items displayed with proper spacing
  - Email displayed at top
  - Links: Generate, My Photos, Logout
  - No squashed/overlapping buttons

#### Test 16: Mobile Dashboard Grid
**Steps:**
1. View dashboard on mobile device

**Expected Results:**
- Grid adapts: 2 columns on mobile (grid-cols-2)
- Each photo card stacks vertically
- Original and generated photos visible
- Download buttons accessible

---

### E. Authentication Tests

#### Test 17: Regular Login
**Steps:**
1. Logout
2. Go to `/login`
3. Enter email and password
4. Click "Login"

**Expected Results:**
- Successfully logged in
- Redirected to dashboard
- JWT token stored in localStorage
- User data loaded

#### Test 18: Google OAuth Login
**Steps:**
1. Logout
2. Go to `/login`
3. Click "Sign in with Google"

**Expected Results:**
- Google OAuth consent screen opens
- After selecting account, redirected back to app
- Logged in successfully
- User created/logged in via OAuth
- Dashboard accessible

---

### F. Original Photos in Dashboard

#### Test 19: Original Photo Loading
**Steps:**
1. View any completed job in dashboard

**Expected Results:**
- For each generated image:
  - Original input photo loads via `/api/generation/input/{image_id}`
  - Generated output photo loads via `/api/generation/results/{image_id}`
  - Both displayed in same card, stacked vertically
  - Labels clearly distinguish "Original" vs "Generated"

#### Test 20: Original Photo Error Handling
**Steps:**
1. Check browser console for any errors while loading photos

**Expected Results:**
- If original photo fails to load: Only generated photo shown, no crash
- Console may show warning but component continues working
- Generated photo still displayed and downloadable

---

## Backend API Tests

### Test 21: Tier Status Endpoint
```bash
# Get your JWT token from browser localStorage
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://gradgen-production.up.railway.app/api/generation/tier-status
```

**Expected Response (Free Tier Available):**
```json
{
  "tier": "free",
  "has_used_free_tier": false,
  "has_purchased_premium": false,
  "premium_generations_used": 0,
  "premium_generations_remaining": 0,
  "can_generate": true,
  "message": "You have 5 free watermarked photos available"
}
```

**Expected Response (Premium - 1 Remaining):**
```json
{
  "tier": "premium",
  "has_used_free_tier": true,
  "has_purchased_premium": true,
  "premium_generations_used": 1,
  "premium_generations_remaining": 1,
  "can_generate": true,
  "message": "Premium tier: 1 generation remaining"
}
```

**Expected Response (Premium Exhausted):**
```json
{
  "tier": "premium_exhausted",
  "has_used_free_tier": true,
  "has_purchased_premium": true,
  "premium_generations_used": 2,
  "premium_generations_remaining": 0,
  "can_generate": false,
  "message": "You have used all your premium generations (2/2)"
}
```

### Test 22: Generation Endpoint Validation
```bash
# Try to generate when premium exhausted (should fail)
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_photo.jpg" \
  -F "university=Oxford" \
  -F "degree_level=Undergraduate" \
  https://gradgen-production.up.railway.app/api/generation/generate-tier
```

**Expected Response (if exhausted):**
```json
{
  "detail": "You have used all your premium generation opportunities (2/2). Thank you for using GradGen!"
}
```
HTTP Status: 403 Forbidden

---

## Edge Cases & Error Handling

### Test 23: Rapid Double-Click on Generate
**Steps:**
1. On generate page, quickly double-click "Generate Photos" button

**Expected Results:**
- Only ONE job created
- Button disabled during submission
- No race condition creating duplicate jobs

### Test 24: Browser Refresh During Generation
**Steps:**
1. Start a generation job
2. Refresh browser while job is processing

**Expected Results:**
- Job continues processing in background
- After refresh, dashboard shows job status
- Real-time progress updates work

### Test 25: Download All Photos
**Steps:**
1. For a completed job with 5 photos
2. Click "Download" on each photo rapidly

**Expected Results:**
- All 5 photos download successfully
- Filenames preserve original names
- No errors or failed downloads

---

## Database Validation

### Test 26: Check Database State
```bash
cd backend
poetry run python -c "
from app.database import SessionLocal
from app.models.user import User
from app.models.generation import GenerationJob

db = SessionLocal()

# Check user
user = db.query(User).filter(User.email == 'YOUR_EMAIL').first()
print(f'has_used_free_tier: {user.has_used_free_tier}')
print(f'has_purchased_premium: {user.has_purchased_premium}')
print(f'premium_generations_used: {user.premium_generations_used}')

# Check jobs
free_jobs = db.query(GenerationJob).filter(
    GenerationJob.user_id == user.id,
    GenerationJob.tier == 'free'
).count()
premium_jobs = db.query(GenerationJob).filter(
    GenerationJob.user_id == user.id,
    GenerationJob.tier == 'premium'
).count()

print(f'Free tier jobs: {free_jobs}')
print(f'Premium jobs: {premium_jobs}')
"
```

---

## Performance Tests

### Test 27: Dashboard Load Time
**Steps:**
1. Open browser DevTools Network tab
2. Navigate to `/dashboard`

**Expected Results:**
- Page loads in < 3 seconds
- Photos load progressively
- No memory leaks (check Memory tab)

### Test 28: Image Loading Efficiency
**Steps:**
1. Check Network tab while viewing 5 photos

**Expected Results:**
- 10 total image requests (5 original + 5 generated)
- Images load in parallel
- Blob URLs properly revoked after unmount (no memory leak)

---

## Regression Tests

### Test 29: Existing Jobs Still Visible
**Steps:**
1. Check dashboard for jobs created before account reset

**Expected Results:**
- All previous jobs still visible
- Old watermarked photos still accessible
- Old premium photos (if any) still downloadable

### Test 30: Referral System (If Implemented)
**Steps:**
1. Check `/dashboard` or `/referrals` page
2. View referral code and link

**Expected Results:**
- Referral code displayed
- Referral link copyable
- Stats show total referrals

---

## Summary Checklist

After account reset, test in this order:

- [ ] **Phase 1: Free Tier**
  - [ ] Test 1-4: Free tier status, generation, exhausted state, photo display

- [ ] **Phase 2: Premium Purchase**
  - [ ] Test 5-7: Pricing, promo codes, Stripe checkout

- [ ] **Phase 3: Premium Usage**
  - [ ] Test 8-14: Premium generations, status updates, exhaustion

- [ ] **Phase 4: Mobile**
  - [ ] Test 15-16: Mobile navbar, responsive grid

- [ ] **Phase 5: Auth & Photos**
  - [ ] Test 17-20: Login, OAuth, original photo display

- [ ] **Phase 6: API & Edge Cases**
  - [ ] Test 21-28: API validation, edge cases, performance

---

## Test Results Template

Copy this for reporting:

```
## Test Results - [Date]

### Free Tier Tests
- Test 1 (Free Status): ✅ PASS / ❌ FAIL - [notes]
- Test 2 (Free Generation): ✅ PASS / ❌ FAIL - [notes]
- Test 3 (Free Exhausted): ✅ PASS / ❌ FAIL - [notes]
- Test 4 (Photo Display): ✅ PASS / ❌ FAIL - [notes]

### Premium Tests
- Test 8 (Premium Status): ✅ PASS / ❌ FAIL - [notes]
- Test 9 (1st Generation): ✅ PASS / ❌ FAIL - [notes]
- Test 10 (Status Update): ✅ PASS / ❌ FAIL - [notes]
- Test 11 (2nd Generation): ✅ PASS / ❌ FAIL - [notes]
- Test 12 (Exhausted): ✅ PASS / ❌ FAIL - [notes]

### Mobile Tests
- Test 15 (Navbar): ✅ PASS / ❌ FAIL - [notes]
- Test 16 (Grid): ✅ PASS / ❌ FAIL - [notes]

### Issues Found
1. [Issue description]
2. [Issue description]

### Notes
- [Any additional observations]
```
