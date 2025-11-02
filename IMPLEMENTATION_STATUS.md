# Business Model Implementation Status

## ✅ COMPLETED

### 1. Database Schema ✓
- Created `PromoCode` model for discount codes
- Created `Referral` model for tracking referrals
- Updated `User` model with tier tracking fields
- Updated `Payment` model for GBP and discounts
- Updated `GenerationJob` model with watermark tracking
- Created `migrate_business_model.py` script

**To Run Migration on Railway:**
```bash
# SSH into Railway or use Railway CLI
python migrate_business_model.py
```

### 2. Watermark Service ✓
- File: `app/services/watermark_service.py`
- Adds "GradGen.AI" watermark to free tier photos
- 30% opacity, configurable position
- Graceful fallback if PIL fails

### 3. Prompt System ✓
- File: `app/core/prompts.py`
- 5 fixed free tier prompts
- 15 premium tier prompts
- Random selection helper functions

### 4. Referral System ✓
- File: `app/services/referral_service.py`
- Generate unique referral codes
- Track signups and completions
- Check 3-referral discount eligibility
- Get stats and referred users list

### 5. Referral API ✓
- File: `app/api/endpoints/referrals.py`
- `GET /api/referrals/stats` - User statistics
- `GET /api/referrals/link` - Shareable link
- `GET /api/referrals/list` - List referred users
- `POST /api/referrals/track` - Track signup
- `GET /api/referrals/check-eligibility` - Check discount

---

## 🚧 IN PROGRESS / NEXT STEPS

### 6. Generation API Updates (NEXT)

**What Needs to be Done:**

**A. Update Generation Endpoint** (`app/api/endpoints/generation.py`):
1. Check user tier eligibility before generating
2. Select prompts based on tier (free vs premium)
3. Apply watermark for free tier
4. Track tier in generation job

**B. Modify Generation Service** (`app/services/generation_service.py`):
1. Use prompts from `app/core/prompts.py` instead of prompts.json
2. Integrate watermark service for free tier images
3. Support batch generation (5 photos at once)

**C. Update Generation Task** (`app/tasks/generation_tasks.py`):
1. Apply watermarking after generation
2. Store both watermarked and unwatermarked versions
3. Link to payment if premium tier

**Example Flow:**
```python
# In generation endpoint
from app.core.prompts import get_free_tier_prompts, get_random_premium_prompts
from app.services.watermark_service import add_watermark_to_image

# Check tier
if not user.has_used_free_tier:
    # Free tier
    tier = "free"
    prompts = get_free_tier_prompts()
    is_watermarked = True
elif user.has_purchased_premium:
    # Premium tier
    tier = "premium"
    prompts = get_random_premium_prompts(count=5)
    is_watermarked = False
else:
    # Need to purchase
    return {"error": "Please purchase premium tier"}

# Generate for each prompt
for prompt_id, prompt_data in prompts.items():
    image_bytes = generation_service.generate_portrait(...)

    # Watermark if free tier
    if tier == "free":
        image_bytes = add_watermark_to_image(image_bytes, tier="free")

    # Save image
    storage_service.save(image_bytes, ...)

# Mark tier as used
if tier == "free":
    user.has_used_free_tier = True
```

---

### 7. Payment API Updates (NEEDED)

**File:** `app/api/endpoints/payments.py`

**Changes Needed:**
1. Calculate price with discounts:
   - Base: £39.99
   - With referral: £19.99 (if `user.referral_discount_eligible`)
   - With promo code: Calculate from `PromoCode.discount_amount`

2. Create payment with metadata:
   ```python
   payment = Payment(
       amount=final_price,
       original_price=39.99,
       discount_applied=discount,
       discount_source="referral" or "promo_code",
       promo_code_used=code if applicable,
       currency="gbp"
   )
   ```

3. After payment succeeds:
   ```python
   user.has_purchased_premium = True
   ```

---

### 8. Promo Code API (NEEDED)

**Need to Create:**
- `app/schemas/promo_code.py` - Pydantic schemas
- `app/api/endpoints/promo_codes.py` - API endpoints

**Endpoints:**
- `POST /api/promo-codes/validate` - Validate and get discount
- `POST /api/admin/promo-codes` - Create (admin only)
- `GET /api/admin/promo-codes` - List all (admin only)

**Example Validation:**
```python
@router.post("/validate")
def validate_promo_code(code: str, db: Session = Depends(get_db)):
    promo = db.query(PromoCode).filter(PromoCode.code == code).first()

    if not promo:
        raise HTTPException(404, "Code not found")

    if not promo.is_valid():
        raise HTTPException(400, "Code expired or limit reached")

    discount = promo.calculate_discount(39.99)

    return {
        "valid": True,
        "discount_amount": discount,
        "final_price": 39.99 - discount
    }
```

---

### 9. Frontend Updates (NEEDED)

**Files to Create/Update:**

**A. Generation Flow** (`webapp/frontend/app/generate/page.tsx`):
```typescript
// Check user status
const checkTierStatus = async () => {
  const user = await fetch('/api/users/me');

  if (!user.has_used_free_tier) {
    // Show free tier UI
    setTier('free');
    setPromptsAvailable(5);
  } else if (!user.has_purchased_premium) {
    // Show pricing/payment UI
    setShowPricing(true);
  } else {
    // Show premium tier UI
    setTier('premium');
    setPromptsAvailable(5);
  }
};
```

**B. Pricing Component** (new):
```typescript
// webapp/frontend/components/PricingCard.tsx
- Show £39.99 base price
- Check referral eligibility
- Promo code input
- Calculate final price
- Stripe payment button
```

**C. Referral Component** (new):
```typescript
// webapp/frontend/components/ReferralSection.tsx
- Display user's referral link
- Copy to clipboard button
- Share buttons (WhatsApp, Email, Twitter)
- Show referral progress (2/3 friends signed up)
- Show discount status
```

**D. Download Component** (update):
```typescript
// Show watermark warning for free tier
// Allow downloading all 10 photos for premium tier
// Show "Upgrade to remove watermarks" CTA for free users
```

---

## 📋 TESTING CHECKLIST

### Database Migration
- [ ] Run `python migrate_business_model.py` on Railway
- [ ] Verify all tables created
- [ ] Verify all columns added
- [ ] Check indexes created

### Free Tier Flow
- [ ] New user registers
- [ ] Upload photo and generate
- [ ] Verify 5 photos generated
- [ ] Verify watermarks present
- [ ] Verify `has_used_free_tier = True`
- [ ] Try to generate again (should be blocked)

### Referral Flow
- [ ] User gets referral code from `/api/referrals/link`
- [ ] Share link with 3 friends
- [ ] Friends register via link
- [ ] Friends verify email
- [ ] Check `/api/referrals/stats` shows 3 completed
- [ ] Verify `referral_discount_eligible = True`

### Premium Purchase (with referral discount)
- [ ] User with 3 referrals goes to pricing
- [ ] Price shows £19.99 instead of £39.99
- [ ] Complete Stripe payment
- [ ] Verify `has_purchased_premium = True`
- [ ] Generate 5 more photos
- [ ] Verify NO watermarks
- [ ] Download all 10 photos

### Premium Purchase (with promo code)
- [ ] Admin creates promo code via API
- [ ] User enters code at checkout
- [ ] Price updates correctly
- [ ] Payment succeeds
- [ ] Promo code `current_uses` increments

### Edge Cases
- [ ] Try to use free tier twice
- [ ] Apply expired promo code
- [ ] Apply max-uses-exceeded promo code
- [ ] Refer yourself (should prevent)
- [ ] Payment fails (should not mark as purchased)

---

## 🚀 DEPLOYMENT STEPS

### 1. Deploy Backend Changes
```bash
git push origin main
# Railway auto-deploys
```

### 2. Run Database Migration
```bash
# Via Railway dashboard or CLI
railway run python migrate_business_model.py
```

### 3. Generate Referral Codes for Existing Users
```python
# Create script: generate_referral_codes.py
from app.db.database import SessionLocal
from app.models.user import User
from app.services.referral_service import ReferralService

db = SessionLocal()
users = db.query(User).all()

for user in users:
    if not user.referral_code:
        ReferralService.get_or_create_user_referral_code(db, user)
        print(f"Generated code for {user.email}")

db.close()
```

### 4. Create Initial Promo Codes (Optional)
```python
from app.models.promo_code import PromoCode

# Launch promo: £19.99 for first 100 users
promo = PromoCode(
    code="LAUNCH2025",
    discount_amount=20.00,
    discount_type="fixed",
    max_uses=100,
    description="Launch promotion",
    created_by="admin"
)
db.add(promo)
db.commit()
```

### 5. Update Frontend
- Deploy frontend changes to Vercel
- Test generation flow
- Test payment flow
- Test referral sharing

---

## 📊 CURRENT FILE STRUCTURE

```
webapp/backend/app/
├── models/
│   ├── promo_code.py ✅
│   ├── referral.py ✅
│   ├── user.py ✅ (updated)
│   ├── payment.py ✅ (updated)
│   └── generation_job.py ✅ (updated)
├── services/
│   ├── watermark_service.py ✅
│   ├── referral_service.py ✅
│   └── generation_service.py ⏳ (needs update)
├── api/endpoints/
│   ├── referrals.py ✅
│   ├── generation.py ⏳ (needs update)
│   ├── payments.py ⏳ (needs update)
│   └── promo_codes.py ❌ (needs creation)
├── schemas/
│   ├── referral.py ✅
│   └── promo_code.py ❌ (needs creation)
├── core/
│   ├── prompts.py ✅
│   └── config.py ✅ (updated)
└── db/
    └── migration_business_model.py ✅

webapp/backend/
└── migrate_business_model.py ✅ (standalone script)
```

---

## 💰 PRICING SUMMARY

| Tier | Price | Features |
|------|-------|----------|
| Free | £0 | 5 prompts, 5 watermarked photos |
| Premium (full price) | £39.99 | 5 MORE prompts (10 total), all unwatermarked |
| Premium (referral discount) | £19.99 | Same as above, after 3 referrals |
| Premium (promo code) | £19.99 | Same as above, with valid promo code |

---

## 📞 NEXT IMMEDIATE ACTIONS

1. **Update Generation API** - Integrate tier checking and watermarking
2. **Update Payment API** - Add discount calculation
3. **Create Promo Code API** - Validation and admin management
4. **Run Migration on Railway** - Apply database changes
5. **Test Complete Flow** - End-to-end testing
6. **Update Frontend** - New generation and pricing UI

Let me know which one you'd like to tackle next!
