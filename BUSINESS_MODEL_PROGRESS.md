# Business Model Implementation Progress

## ✅ Completed (Phase 1: Database & Core Services)

### 1. Database Schema Design ✓

**New Models Created:**
- **PromoCode** (`app/models/promo_code.py`)
  - Support for fixed and percentage discounts
  - Usage limits and expiry dates
  - Validation methods (`is_valid()`, `calculate_discount()`)

- **Referral** (`app/models/referral.py`)
  - Track referrer and referred user
  - Status tracking (pending, completed, rewarded)
  - Fraud detection fields (IP, user agent)

**Updated Models:**
- **User** model:
  - `has_used_free_tier`: Tracks if user has generated 5 free photos
  - `has_purchased_premium`: Tracks premium purchase
  - `referral_discount_eligible`: True after 3 successful referrals
  - `referral_code`: User's personal referral link code

- **Payment** model:
  - Changed currency from USD to GBP
  - Added `original_price`, `discount_applied`, `discount_source`
  - Added `promo_code_used` for tracking
  - Added `generation_job_id` to link payment to generation

- **GenerationJob** model:
  - `tier`: "free" or "premium"
  - `is_watermarked`: Boolean flag
  - `prompts_used`: JSON list of prompt IDs (for random premium selection)
  - `payment_id`: Link to payment if premium tier

**Migration Script:**
- Created `app/db/migration_business_model.py`
- Run with: `python -m app.db.migration_business_model`
- Safely adds columns with IF NOT EXISTS
- Creates indexes for performance

---

### 2. Watermark Service ✓

**File:** `app/services/watermark_service.py`

**Features:**
- Adds "GradGen.AI" watermark to free tier photos
- Configurable opacity (default 30%)
- Multiple position options (bottom_right, bottom_left, center, etc.)
- Font size scales with image dimensions (5% of height)
- Graceful fallback if watermarking fails
- Uses PIL (Pillow) for image processing

**Usage:**
```python
from app.services.watermark_service import add_watermark_to_image

# Automatically watermarks if tier is "free"
watermarked_bytes = add_watermark_to_image(
    image_bytes=original_image,
    tier="free",  # or "premium"
    position="bottom_right"
)
```

---

### 3. Prompt System ✓

**File:** `app/core/prompts.py`

**Free Tier Prompts (5 Fixed):**
1. P0_Apple_Studio - High-end studio portrait
2. P2_Grad_Parametric - University-specific regalia
3. P5_Editorial_Soft - Soft editorial style
4. P6_HighKey_WhiteBG - White background
5. P7_LowKey_BlackBG - Black background

**Premium Tier Prompt Bank (15 Total):**
- Classic_UK_Graduation
- American_College_Style
- Vintage_Academic
- Golden_Hour_Outdoor
- Corporate_Professional
- Candid_Celebration
- Formal_Yearbook
- Artistic_Portrait
- Family_Heirloom
- Modern_Minimal
- Dramatic_Chiaroscuro
- Soft_Natural_Light
- Urban_Contemporary
- Heritage_Tradition
- Joyful_Candid

**Helper Functions:**
```python
from app.core.prompts import (
    get_free_tier_prompts,
    get_random_premium_prompts,
    get_prompt_by_id,
    format_prompt
)

# Get free tier prompts
free_prompts = get_free_tier_prompts()

# Get 5 random premium prompts
premium_prompts = get_random_premium_prompts(count=5)

# Format prompt with university details
formatted = format_prompt(
    prompt_template=prompt["prompt"],
    university="Loughborough University",
    degree_level="Bachelors"
)
```

---

## 🚧 Next Steps (Phase 2: API Implementation)

### 4. Promo Code API (In Progress)

**Need to create:**
- `app/schemas/promo_code.py` - Pydantic schemas
- `app/api/endpoints/promo_codes.py` - API endpoints
  - `POST /api/promo-codes/validate` - Validate code and calculate discount
  - `POST /api/admin/promo-codes` - Create new code (admin only)
  - `GET /api/admin/promo-codes` - List all codes (admin only)
  - `PUT /api/admin/promo-codes/{id}` - Update code (admin only)
  - `DELETE /api/admin/promo-codes/{id}` - Deactivate code (admin only)

### 5. Referral System API

**Need to create:**
- `app/schemas/referral.py` - Pydantic schemas
- `app/api/endpoints/referrals.py` - API endpoints
  - `GET /api/referrals/my-code` - Get user's referral code
  - `GET /api/referrals/stats` - Get referral statistics
  - `POST /api/referrals/track` - Track referral signup
  - `GET /api/referrals/check-eligibility` - Check if eligible for discount

**Helper service:**
- `app/services/referral_service.py`
  - Generate unique referral codes
  - Track referral conversions
  - Check if user has 3 completed referrals
  - Apply discount when threshold reached

### 6. Update Generation API

**Files to modify:**
- `app/api/endpoints/generation.py`
- `app/services/generation_service.py`
- `app/tasks/generation_tasks.py`

**Changes needed:**
1. **Check tier eligibility:**
   - If `has_used_free_tier == False`: Allow free tier generation
   - If `has_purchased_premium == True`: Allow premium tier generation
   - Otherwise: Show pricing/payment prompt

2. **Free tier generation:**
   - Use 5 fixed prompts from `FREE_TIER_PROMPTS`
   - Generate 5 photos
   - Apply watermark to all images
   - Set `has_used_free_tier = True` after completion

3. **Premium tier generation:**
   - Require payment first
   - Select 5 random prompts from `PREMIUM_TIER_PROMPT_BANK`
   - Generate 5 additional photos (10 total with free tier)
   - NO watermark
   - Link to payment record

4. **Prompt selection:**
   ```python
   if tier == "free":
       prompts = get_free_tier_prompts()
   else:  # premium
       prompts = get_random_premium_prompts(count=5)
   ```

5. **Watermarking:**
   ```python
   from app.services.watermark_service import add_watermark_to_image

   # After image generation
   if job.tier == "free":
       image_bytes = add_watermark_to_image(
           image_bytes=generated_image,
           tier="free"
       )
   ```

### 7. Update Payment API

**Files to modify:**
- `app/api/endpoints/payments.py`

**Changes needed:**
1. **Calculate price with discounts:**
   ```python
   base_price = 39.99

   # Check for referral discount
   if user.referral_discount_eligible:
       discount = 20.00
       final_price = 19.99
       discount_source = "referral"

   # Or check for promo code
   elif promo_code:
       promo = get_promo_code(promo_code)
       if promo.is_valid():
           discount = promo.calculate_discount(base_price)
           final_price = base_price - discount
           discount_source = "promo_code"
   else:
       discount = 0.0
       final_price = base_price
       discount_source = None
   ```

2. **Create payment with metadata:**
   ```python
   payment = Payment(
       user_id=user.id,
       amount=final_price,
       original_price=39.99,
       discount_applied=discount,
       discount_source=discount_source,
       promo_code_used=promo_code if promo_code else None,
       currency="gbp"
   )
   ```

3. **After successful payment:**
   ```python
   user.has_purchased_premium = True

   # If promo code was used, increment usage
   if promo_code:
       promo.current_uses += 1
   ```

---

## 📋 Phase 3: Frontend Updates (After API is done)

### 8. Update Frontend Generation Flow

**Files to update:**
- `webapp/frontend/app/generate/page.tsx`
- Create new components for pricing, payment, referrals

**Flow:**
1. **Check user status:**
   ```typescript
   if (!user.has_used_free_tier) {
       // Show free tier UI
       showFreeTierGeneration()
   } else if (!user.has_purchased_premium) {
       // Show pricing/payment UI
       showPricingOptions()
   } else {
       // Show premium tier UI
       showPremiumTierGeneration()
   }
   ```

2. **Free tier UI:**
   - Upload photo
   - Select university and degree level
   - Show "5 styles included" badge
   - Show watermark preview/warning
   - Generate button

3. **Pricing UI:**
   - Show £39.99 base price
   - Show referral discount section (if 3 referrals completed)
   - Promo code input field
   - Live price calculation
   - Payment button (Stripe)

4. **Premium tier UI:**
   - Show "5 more random styles" message
   - Upload photo
   - Select university and degree level
   - Generate button
   - Download all 10 photos (unwatermarked)

5. **Referral UI:**
   - User's referral link
   - Copy button
   - Share buttons (WhatsApp, Email, etc.)
   - Referral progress (e.g., "2/3 friends signed up")

---

## 🧪 Phase 4: Testing & Deployment

### 9. Testing Checklist

**Database Migration:**
- [ ] Run migration script on dev database
- [ ] Verify all tables created
- [ ] Verify all columns added
- [ ] Test rollback if needed

**Free Tier Flow:**
- [ ] New user registers
- [ ] Uploads photo
- [ ] Generates 5 watermarked photos
- [ ] Downloads all 5
- [ ] Verify watermarks present
- [ ] Verify `has_used_free_tier = True`

**Referral Flow:**
- [ ] User gets referral code
- [ ] Share with 3 friends
- [ ] Friends register via link
- [ ] Friends verify email
- [ ] User becomes eligible for discount
- [ ] Verify `referral_discount_eligible = True`

**Promo Code Flow:**
- [ ] Admin creates promo code
- [ ] User applies code at checkout
- [ ] Price updates correctly
- [ ] Payment succeeds
- [ ] Promo code usage increments
- [ ] Cannot reuse single-use codes

**Premium Tier Flow:**
- [ ] User purchases premium (with or without discount)
- [ ] Payment succeeds
- [ ] `has_purchased_premium = True`
- [ ] Generates 5 additional photos
- [ ] Verify NO watermarks
- [ ] Can download all 10 photos

**Edge Cases:**
- [ ] User tries to use free tier twice (should fail)
- [ ] Invalid promo code (should show error)
- [ ] Expired promo code (should show error)
- [ ] Referral to self (should prevent)
- [ ] Payment fails (should not mark as purchased)

---

## 📊 Current Status Summary

| Task | Status | Files |
|------|--------|-------|
| Database schema design | ✅ Complete | `app/models/*.py` |
| Database migration script | ✅ Complete | `app/db/migration_business_model.py` |
| Watermark service | ✅ Complete | `app/services/watermark_service.py` |
| Prompt configuration | ✅ Complete | `app/core/prompts.py` |
| Promo code API | 🚧 Next | Need to create |
| Referral API | ⏳ Pending | Need to create |
| Generation API updates | ⏳ Pending | Need to update |
| Payment API updates | ⏳ Pending | Need to update |
| Frontend generation flow | ⏳ Pending | Need to update |
| Testing & QA | ⏳ Pending | After implementation |

---

## 🚀 How to Proceed

### Option A: Continue with API Implementation (Recommended)
1. Create promo code API endpoints
2. Create referral API endpoints
3. Update generation service to use new prompts and watermarking
4. Update payment service for GBP and discounts
5. Test backend thoroughly

### Option B: Run Database Migration First
1. Backup production database
2. Run `python -m app.db.migration_business_model` on production
3. Verify tables and columns created
4. Then continue with API implementation

### Option C: Frontend Updates First
1. Update generation UI to show free tier / premium tier split
2. Add pricing display
3. Add referral section
4. Mock the API responses for now
5. Connect to real API later

---

## 💡 Recommendations

1. **Start with API implementation** - The backend logic is crucial
2. **Test watermarking locally** - Make sure PIL/Pillow is installed
3. **Create a test promo code** - To verify discount logic works
4. **Generate referral codes for existing users** - Script to backfill
5. **Update Stripe webhook** - Handle GBP instead of USD
6. **Add admin panel** - For creating promo codes easily

Let me know which phase you'd like to tackle next!
