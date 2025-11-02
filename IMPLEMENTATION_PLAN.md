# GradGen.AI - New Business Model Implementation Plan

## 🎯 Overview

Transform GradGen from a credit-based system to a prompt-based preview model with watermarks and selective download purchases.

---

## 📊 New Business Model

### Current Model (Old)
- User registers → Gets 5 free credits
- 1 credit = 1 photo generation
- Purchase more credits to generate more photos
- All photos downloadable immediately

### New Model (Target)
**Free Tier:**
- User registers → Gets 5 free prompt runs (fixed styles)
- 1 prompt run = 1 photo with 1 style
- Uses 5 predefined styles: Apple Studio, University-specific Regalia, Editorial Soft, High-Key White BG, Low-Key Black BG
- All 5 photos have watermarks
- Can view but cannot download unwatermarked versions

**Paid Tier:**
- **Base Price:** £39.99
- **Discounted Price:** £19.99 (with 3 referrals OR promo code)
- **What You Get:**
  - 5 additional prompt runs with **random styles** from prompt bank (10 total photos)
  - All 10 photos unwatermarked
  - Can download all 10 photos in high resolution

**Referral System:**
- Each user gets unique referral code
- When 3 friends sign up using your code → You unlock £19.99 discount
- Friends who sign up also get credit towards their own discount

**Promo Code System:**
- Admin can create promo codes (e.g., "LAUNCH50", "GRAD2025")
- Applying valid code → Price drops to £19.99

---

## 🎨 Prompt Strategy

### Free Tier - Fixed 5 Prompts (Always Same)
1. **P0_Apple_Studio** - Professional minimalist studio portrait
2. **P2_Grad_Parametric** - University-specific regalia (customized)
3. **P5_Editorial_Soft** - Editorial portrait with soft cinematic grading
4. **P6_HighKey_WhiteBG** - High-key studio portrait with white background
5. **P7_LowKey_BlackBG** - Low-key studio portrait with black background

### Paid Tier - Random 5 from Prompt Bank (Changes Each User)

**Prompt Bank (15+ graduation styles):**

1. **Classic_UK_Graduation** - Traditional black gown, mortarboard, hood
2. **American_College_Style** - US-style graduation with colored sash
3. **Formal_Academic_Regalia** - Full ceremonial academic dress
4. **Modern_Minimalist_Grad** - Contemporary clean graduation look
5. **Heritage_University_Style** - Traditional Oxford/Cambridge style
6. **Outdoor_Campus_Graduation** - Natural campus background setting
7. **Professional_Headshot_Grad** - LinkedIn-ready graduation portrait
8. **Vintage_Academic_Portrait** - Classic film-style graduation photo
9. **Celebratory_Grad_Pose** - Joyful graduation moment capture
10. **Monochrome_Graduation** - Black & white artistic graduation
11. **Golden_Hour_Grad** - Warm sunset lighting graduation portrait
12. **Studio_Flash_Graduation** - High-contrast studio lighting
13. **Soft_Natural_Light_Grad** - Window-lit natural graduation portrait
14. **Bold_Color_Graduation** - Vibrant, saturated graduation colors
15. **Timeless_Classic_Grad** - Elegant, traditional graduation style

**Selection Logic:**
- When user pays, system randomly selects 5 prompts from bank
- Ensures variety and uniqueness for each user
- No duplicates in the 5 selected prompts

---

## 📸 Example Photos for Landing Page

### Source: Unsplash (Commercially Free)
We'll download 4-5 professional portraits from:
- https://unsplash.com/s/photos/professional-headshot
- https://unsplash.com/s/photos/professional-portrait

**Criteria:**
- Diverse representation (gender, ethnicity, age)
- Clear face visibility
- Professional appearance
- Good lighting
- Half-body or headshot composition

**Example URLs to download:**
1. https://unsplash.com/photos/[ID1] - Young professional woman
2. https://unsplash.com/photos/[ID2] - Young professional man
3. https://unsplash.com/photos/[ID3] - Mature professional
4. https://unsplash.com/photos/[ID4] - Professional with glasses

---

## 🏗️ Technical Implementation

### Phase 1: Database Schema Updates

**Update User Model:**
```python
class User(Base):
    # Remove: credits field
    # Add:
    free_prompts_remaining = Column(Integer, default=5)  # Free tier (fixed styles)
    paid_prompts_remaining = Column(Integer, default=0)  # After payment (random styles)
    has_purchased = Column(Boolean, default=False)  # Track if user bought package

    # Referral system
    referral_code = Column(String, unique=True)  # User's unique referral code
    referred_by = Column(String, nullable=True)  # Code of person who referred them
    successful_referrals = Column(Integer, default=0)  # Count of users who signed up with their code
    referral_discount_unlocked = Column(Boolean, default=False)  # True when 3+ referrals

    # Pricing
    current_price = Column(Float, default=39.99)  # £39.99 or £19.99 if discounted
```

**Add Promo Code Model:**
```python
class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # e.g., "LAUNCH50"
    discount_amount = Column(Float)  # e.g., 20.00 (£20 off)
    discount_percent = Column(Float, nullable=True)  # e.g., 50 (50% off)
    final_price = Column(Float, nullable=True)  # e.g., 19.99 (overrides calculation)

    active = Column(Boolean, default=True)
    max_uses = Column(Integer, nullable=True)  # Null = unlimited
    current_uses = Column(Integer, default=0)

    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Track who used this code
    used_by_users = Column(JSON, default=[])  # List of user IDs

**Add Referral Tracking Model:**
```python
class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))  # Who shared the code
    referred_id = Column(Integer, ForeignKey("users.id"))  # Who signed up
    referral_code = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_counted = Column(Boolean, default=True)  # For tracking valid referrals
```

**Update Generation Job Model:**
```python
class GenerationJob(Base):
    # Add:
    is_watermarked = Column(Boolean, default=True)  # All free photos watermarked
    is_selected = Column(Boolean, default=False)  # User selected for unwatermark
    prompt_type = Column(String)  # P0, P1, P2, etc.
```

---

### Phase 2: Watermark Implementation

**Backend Changes:**

1. Create watermark overlay image with GradGen.AI logo
2. Add watermark service in `webapp/backend/app/services/watermark.py`:

```python
from PIL import Image, ImageDraw, ImageFont

class WatermarkService:
    @staticmethod
    def add_watermark(image_path: str, output_path: str) -> bool:
        """Add GradGen.AI watermark to image."""
        # Open image
        img = Image.open(image_path)

        # Create watermark overlay
        # Position: Bottom-right corner, semi-transparent
        # Text: "GradGen.AI" or logo

        # Save watermarked version
        img.save(output_path)
        return True

    @staticmethod
    def remove_watermark(watermarked_path: str, original_path: str) -> bool:
        """Return original unwatermarked image."""
        # Simply use the original generated image before watermark
        # Copy original to output location
        return True
```

3. Update generation endpoint to apply watermark after Gemini generation:
   - Generate photo with Gemini
   - Save original (unwatermarked) to `results/original/{job_id}.png`
   - Apply watermark and save to `results/{job_id}.png` (public URL)
   - Store both paths in database

---

### Phase 3: Prompt-Based Generation System

**Prompt Bank Configuration:**

```python
# In app/core/config.py or separate prompts config file

FREE_TIER_PROMPTS = [
    "P0_Apple_Studio",
    "P2_Grad_Parametric",
    "P5_Editorial_Soft",
    "P6_HighKey_WhiteBG",
    "P7_LowKey_BlackBG"
]

PAID_TIER_PROMPT_BANK = [
    "Classic_UK_Graduation",
    "American_College_Style",
    "Formal_Academic_Regalia",
    "Modern_Minimalist_Grad",
    "Heritage_University_Style",
    "Outdoor_Campus_Graduation",
    "Professional_Headshot_Grad",
    "Vintage_Academic_Portrait",
    "Celebratory_Grad_Pose",
    "Monochrome_Graduation",
    "Golden_Hour_Grad",
    "Studio_Flash_Graduation",
    "Soft_Natural_Light_Grad",
    "Bold_Color_Graduation",
    "Timeless_Classic_Grad"
]

# Full prompt definitions
PROMPT_DEFINITIONS = {
    "P0_Apple_Studio": "Transform the photo into a high-end studio portrait...",
    "P2_Grad_Parametric": "Identity-preserving edit. Keep the subject unchanged...",
    # ... (existing prompts)
    "Classic_UK_Graduation": "Traditional UK graduation portrait. Black academic gown, square mortarboard with tassel, colored hood representing degree. Half-body framing, neutral studio background, soft professional lighting. Photo-realistic fabric textures, sharp details.",
    "American_College_Style": "US-style college graduation. Black cap and gown with colored honor sash or stole. Proud, confident expression. Campus-style background with academic architecture. Natural outdoor lighting.",
    # ... (add all 15+ paid tier prompts)
}
```

**Update Generation Endpoint:**

```python
import random

@router.post("/generate-batch")
async def generate_graduation_photos(
    file: UploadFile,
    university: str,
    degree_level: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate 5 photos at once (either free tier or paid tier)."""

    # Check if user has any prompts remaining
    free_remaining = current_user.free_prompts_remaining
    paid_remaining = current_user.paid_prompts_remaining

    if free_remaining <= 0 and paid_remaining <= 0:
        raise HTTPException(403, "No prompts remaining. Please purchase the full package.")

    # Determine which prompts to use
    if free_remaining > 0:
        # Use fixed free tier prompts
        prompts_to_use = FREE_TIER_PROMPTS[:5]
        is_free_tier = True
        current_user.free_prompts_remaining = 0  # Use all 5 at once
    else:
        # Use random paid tier prompts
        prompts_to_use = random.sample(PAID_TIER_PROMPT_BANK, 5)
        is_free_tier = False
        current_user.paid_prompts_remaining = 0  # Use all 5 at once

    # Save uploaded image
    image_path = save_uploaded_file(file)

    # Create 5 generation jobs
    jobs = []
    for idx, prompt_type in enumerate(prompts_to_use):
        job = GenerationJob(
            user_id=current_user.id,
            status="pending",
            university=university,
            degree_level=degree_level,
            prompt_type=prompt_type,
            is_watermarked=is_free_tier,  # Free tier = watermarked, paid = not watermarked
            input_image_path=image_path
        )
        db.add(job)
        jobs.append(job)

    db.commit()

    # Queue Celery tasks for each job
    for job in jobs:
        db.refresh(job)
        generate_portrait_task.delay(job.id)

    return {
        "job_ids": [j.id for j in jobs],
        "tier": "free" if is_free_tier else "paid",
        "prompts_used": prompts_to_use
    }

@router.post("/generate-single")
async def generate_single_photo(
    file: UploadFile,
    university: str,
    degree_level: str,
    prompt_type: str,  # Specific prompt for re-generation
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate single photo (for re-tries or specific style)."""

    # Check if user has purchased (only paid users can regenerate specific styles)
    if not current_user.has_purchased:
        raise HTTPException(403, "Purchase required for custom style generation.")

    # Create generation job
    job = GenerationJob(
        user_id=current_user.id,
        status="pending",
        university=university,
        degree_level=degree_level,
        prompt_type=prompt_type,
        is_watermarked=False,  # Paid tier = no watermark
        input_image_path=save_uploaded_file(file)
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue Celery task
    generate_portrait_task.delay(job.id)

    return job
```

---

### Phase 4: Payment System Updates

**New Stripe Products:**
- Product: "GradGen.AI Full Package"
- Price 1: £39.99 (base price)
- Price 2: £19.99 (discounted price)
- Includes: 5 additional random-style prompts + unwatermark all 10 photos

**Dynamic Pricing Endpoint:**

```python
@router.get("/pricing")
async def get_pricing(
    current_user: User = Depends(get_current_user),
    promo_code: str = None,
    db: Session = Depends(get_db)
):
    """Get current price for user based on referrals and promo codes."""
    base_price = 39.99
    final_price = base_price
    discount_reason = None

    # Check referral discount (3+ successful referrals)
    if current_user.successful_referrals >= 3:
        final_price = 19.99
        discount_reason = "referral_discount"
        current_user.referral_discount_unlocked = True

    # Check promo code (overrides referral if better)
    if promo_code:
        promo = db.query(PromoCode).filter(
            PromoCode.code == promo_code.upper(),
            PromoCode.active == True
        ).first()

        if promo:
            # Check if expired
            if promo.expires_at and promo.expires_at < datetime.utcnow():
                raise HTTPException(400, "Promo code expired")

            # Check max uses
            if promo.max_uses and promo.current_uses >= promo.max_uses:
                raise HTTPException(400, "Promo code limit reached")

            # Check if user already used this code
            if current_user.id in promo.used_by_users:
                raise HTTPException(400, "You've already used this promo code")

            # Calculate discount
            if promo.final_price:
                final_price = promo.final_price
            elif promo.discount_percent:
                final_price = base_price * (1 - promo.discount_percent / 100)
            elif promo.discount_amount:
                final_price = max(0, base_price - promo.discount_amount)

            discount_reason = f"promo_{promo_code}"

    # Update user's current price
    current_user.current_price = final_price
    db.commit()

    return {
        "base_price": base_price,
        "final_price": final_price,
        "discount_reason": discount_reason,
        "referrals_count": current_user.successful_referrals,
        "referrals_needed": max(0, 3 - current_user.successful_referrals)
    }

@router.post("/create-checkout-session")
async def create_checkout_session(
    promo_code: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get pricing
    pricing = await get_pricing(current_user, promo_code, db)
    final_price = pricing["final_price"]

    # Determine which Stripe price to use
    if final_price <= 19.99:
        price_id = settings.STRIPE_PRICE_ID_DISCOUNTED  # £19.99
    else:
        price_id = settings.STRIPE_PRICE_ID_BASE  # £39.99

    # Create Stripe checkout
    checkout_session = stripe.checkout.Session.create(
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/dashboard",
        metadata={
            'user_id': current_user.id,
            'promo_code': promo_code or '',
            'final_price': final_price
        }
    )
    return {"url": checkout_session.url}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    # Verify webhook signature
    # ...

    if event.type == 'checkout.session.completed':
        session = event.data.object
        user_id = session.metadata.get('user_id')
        promo_code = session.metadata.get('promo_code')

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Grant paid prompts
            user.has_purchased = True
            user.paid_prompts_remaining = 5

            # Track promo code usage
            if promo_code:
                promo = db.query(PromoCode).filter(
                    PromoCode.code == promo_code.upper()
                ).first()
                if promo:
                    promo.current_uses += 1
                    if user.id not in promo.used_by_users:
                        promo.used_by_users.append(user.id)

            db.commit()

    return {"status": "success"}
```

---

### Phase 4.5: Referral System

**Referral Code Generation:**

```python
import secrets
import string

def generate_referral_code(length=8):
    """Generate unique referral code like 'GRAD2K8X'."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# In auth.py registration endpoint:
@router.post("/register")
async def register(
    user_in: UserCreate,
    referral_code: str = None,  # Optional: code of person who referred them
    db: Session = Depends(get_db)
):
    # Create user
    user = User(
        email=user_in.email,
        # ... other fields ...
        referral_code=generate_referral_code(),  # Generate unique code for this user
        referred_by=referral_code if referral_code else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # If referred by someone, track it
    if referral_code:
        referrer = db.query(User).filter(User.referral_code == referral_code).first()
        if referrer:
            # Create referral record
            referral = Referral(
                referrer_id=referrer.id,
                referred_id=user.id,
                referral_code=referral_code
            )
            db.add(referral)

            # Update referrer's count
            referrer.successful_referrals += 1

            # Check if they unlocked discount (3+ referrals)
            if referrer.successful_referrals >= 3 and not referrer.referral_discount_unlocked:
                referrer.referral_discount_unlocked = True
                referrer.current_price = 19.99

                # Send email notification
                await EmailService.send_referral_discount_email(
                    email=referrer.email,
                    full_name=referrer.full_name
                )

            db.commit()

    return user
```

**Referral Endpoints:**

```python
@router.get("/referrals/my-code")
async def get_my_referral_code(current_user: User = Depends(get_current_user)):
    """Get user's referral code and stats."""
    return {
        "referral_code": current_user.referral_code,
        "successful_referrals": current_user.successful_referrals,
        "discount_unlocked": current_user.referral_discount_unlocked,
        "referrals_needed": max(0, 3 - current_user.successful_referrals),
        "share_url": f"{settings.FRONTEND_URL}/register?ref={current_user.referral_code}"
    }

@router.get("/referrals/list")
async def get_my_referrals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of users who signed up with my code."""
    referrals = db.query(Referral).filter(
        Referral.referrer_id == current_user.id
    ).all()

    referred_users = []
    for ref in referrals:
        user = db.query(User).filter(User.id == ref.referred_id).first()
        if user:
            referred_users.append({
                "email": user.email[:3] + "***",  # Partially hidden for privacy
                "created_at": ref.created_at,
                "is_counted": ref.is_counted
            })

    return {
        "total": len(referred_users),
        "referrals": referred_users
    }
```

**Frontend Referral UI:**

```tsx
// In dashboard or profile page
function ReferralSection() {
  const [referralData, setReferralData] = useState(null);

  useEffect(() => {
    async function loadReferralData() {
      const data = await api.get('/api/referrals/my-code');
      setReferralData(data);
    }
    loadReferralData();
  }, []);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(referralData.share_url);
    toast.success('Referral link copied!');
  };

  return (
    <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white rounded-lg p-6">
      <h3 className="text-2xl font-bold mb-4">Refer Friends, Get 50% Off!</h3>

      {referralData?.discount_unlocked ? (
        <div className="bg-green-500 rounded-lg p-4 mb-4">
          <p className="font-bold text-lg">🎉 Discount Unlocked!</p>
          <p>You've referred 3+ friends. Your price is now £19.99!</p>
        </div>
      ) : (
        <div className="mb-4">
          <p className="text-lg">
            {referralData?.successful_referrals}/3 friends referred
          </p>
          <p className="text-sm opacity-90">
            Refer {referralData?.referrals_needed} more to unlock £19.99 pricing
          </p>
        </div>
      )}

      <div className="bg-white/20 rounded-lg p-4">
        <p className="text-sm mb-2">Your Referral Code:</p>
        <div className="flex gap-2">
          <input
            type="text"
            value={referralData?.referral_code}
            readOnly
            className="flex-1 bg-white text-gray-900 px-4 py-2 rounded-lg font-mono text-lg"
          />
          <button
            onClick={copyToClipboard}
            className="bg-yellow-400 text-primary-900 px-4 py-2 rounded-lg font-bold"
          >
            Copy Link
          </button>
        </div>
      </div>

      <p className="text-sm mt-4 opacity-90">
        Share your link with friends. When 3 sign up, you'll get the full package for £19.99!
      </p>
    </div>
  );
}
```

---

### Phase 5: Download System

**Download Endpoint:**

```python
@router.get("/download/{job_id}")
async def download_photo(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download photo - watermarked for free tier, unwatermarked for paid tier."""
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id,
        GenerationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(404, "Photo not found")

    # Free tier photos are watermarked
    if job.is_watermarked:
        return FileResponse(
            job.watermarked_image_path,
            filename=f"gradgen_{job.id}_preview.jpg",
            media_type="image/jpeg"
        )
    else:
        # Paid tier photos are unwatermarked
        return FileResponse(
            job.original_image_path,
            filename=f"gradgen_{job.id}_final.jpg",
            media_type="image/jpeg"
        )

@router.get("/download-all")
async def download_all_photos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download all unwatermarked photos as ZIP (paid tier only)."""
    if not current_user.has_purchased:
        raise HTTPException(403, "Purchase required to download all photos")

    # Get all unwatermarked photos
    jobs = db.query(GenerationJob).filter(
        GenerationJob.user_id == current_user.id,
        GenerationJob.is_watermarked == False,
        GenerationJob.status == "completed"
    ).all()

    if not jobs:
        raise HTTPException(404, "No completed photos found")

    # Create ZIP file
    import zipfile
    from io import BytesIO

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for job in jobs:
            zip_file.write(
                job.original_image_path,
                f"gradgen_{job.prompt_type}_{job.id}.jpg"
            )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=gradgen_photos.zip"}
    )
```

---

### Phase 6: Frontend Updates

#### Landing Page Redesign (Mobile-First)

**New Homepage (`webapp/frontend/app/page.tsx`):**

```tsx
export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section with Before/After */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-12 md:py-20">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-6xl font-bold text-center mb-4">
            Transform Your Portrait into a Graduation Photo
          </h1>
          <p className="text-xl text-center mb-8">
            AI-Powered. Professional. Instant.
          </p>

          {/* Before/After Slider */}
          <BeforeAfterSlider
            beforeImage="/examples/before-1.jpg"
            afterImage="/examples/after-1.jpg"
          />

          <div className="text-center mt-8">
            <Link href="/register">
              <button className="bg-white text-primary-600 px-8 py-4 rounded-lg text-lg font-bold">
                Try 5 Styles Free →
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Example Gallery */}
      <section className="py-12 md:py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          See the Transformation
        </h2>
        <ExampleGallery examples={EXAMPLES} />
      </section>

      {/* Pricing */}
      <section className="bg-gray-50 py-12 md:py-20">
        <PricingSection />
      </section>
    </div>
  );
}
```

**Pricing Section:**

```tsx
function PricingSection() {
  const [pricing, setPricing] = useState(null);

  useEffect(() => {
    async function loadPricing() {
      const data = await api.get('/api/payments/pricing');
      setPricing(data);
    }
    loadPricing();
  }, []);

  return (
    <div className="container mx-auto px-4">
      <h2 className="text-3xl font-bold text-center mb-12">
        Simple, Transparent Pricing
      </h2>

      <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        {/* Free Tier */}
        <div className="bg-white rounded-lg shadow-lg p-8 border-2 border-gray-200">
          <h3 className="text-2xl font-bold mb-4">Free Trial</h3>
          <div className="text-4xl font-bold mb-6">£0</div>
          <ul className="space-y-3 mb-8">
            <li>✓ 5 AI-generated photos</li>
            <li>✓ Fixed professional styles</li>
            <li>✓ Preview all results</li>
            <li>⚠️ Watermarked photos</li>
          </ul>
          <Link href="/register">
            <button className="w-full bg-gray-200 text-gray-800 py-3 rounded-lg font-semibold">
              Start Free Trial
            </button>
          </Link>
        </div>

        {/* Paid Tier */}
        <div className="bg-primary-600 text-white rounded-lg shadow-lg p-8 border-2 border-primary-700 relative">
          <div className="absolute top-0 right-0 bg-yellow-400 text-primary-900 px-4 py-1 rounded-bl-lg font-bold">
            BEST VALUE
          </div>
          <h3 className="text-2xl font-bold mb-4">Full Package</h3>

          {/* Dynamic Pricing */}
          <div className="mb-4">
            {pricing?.final_price < pricing?.base_price ? (
              <div>
                <div className="text-2xl line-through opacity-75">£{pricing.base_price}</div>
                <div className="text-5xl font-bold">£{pricing.final_price}</div>
                <div className="text-sm mt-2 bg-green-500 inline-block px-3 py-1 rounded">
                  {pricing.discount_reason === 'referral_discount' && '🎉 Referral Discount!'}
                  {pricing.discount_reason?.startsWith('promo_') && '🎁 Promo Code Applied!'}
                </div>
              </div>
            ) : (
              <div className="text-4xl font-bold">£39.99</div>
            )}
          </div>

          <ul className="space-y-3 mb-8">
            <li>✓ Everything in Free</li>
            <li>✓ 5 MORE random unique styles (10 total)</li>
            <li>✓ ALL 10 photos unwatermarked</li>
            <li>✓ High-res downloads</li>
            <li>✓ Download all as ZIP</li>
          </ul>

          {/* Referral Progress */}
          {pricing && !pricing.referral_discount_unlocked && (
            <div className="bg-white/20 rounded-lg p-3 mb-4 text-sm">
              <p>🎁 Refer {pricing.referrals_needed} more friend{pricing.referrals_needed !== 1 && 's'} to get £19.99 pricing!</p>
            </div>
          )}

          <button className="w-full bg-white text-primary-600 py-3 rounded-lg font-semibold">
            Get Full Package
          </button>
        </div>
      </div>

      {/* Promo Code Section */}
      <div className="text-center mt-8">
        <p className="text-gray-600">
          Have a promo code? <Link href="/checkout" className="text-primary-600 underline">Apply at checkout</Link>
        </p>
      </div>
    </div>
  );
}
```

**Dashboard Updates:**

```tsx
function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [selectedPhotos, setSelectedPhotos] = useState<number[]>([]);
  const { user } = useAuth();

  const handleSelectPhoto = (id: number) => {
    if (!user.has_purchased) {
      alert("Purchase required to select photos");
      return;
    }

    if (selectedPhotos.includes(id)) {
      setSelectedPhotos(prev => prev.filter(pid => pid !== id));
    } else if (selectedPhotos.length < 5) {
      setSelectedPhotos(prev => [...prev, id]);
    } else {
      alert("You can only select 5 photos");
    }
  };

  const handleConfirmSelection = async () => {
    await api.post('/api/generation/select-photos', {
      photo_ids: selectedPhotos
    });
    // Refresh jobs to show unwatermarked versions
    loadJobs();
  };

  return (
    <div>
      {/* Status Bar */}
      <div className="bg-white border-b p-4">
        <div className="container mx-auto">
          <p>Free Prompts: {user.free_prompts_remaining} | Paid Prompts: {user.paid_prompts_remaining}</p>
          {user.has_purchased && (
            <p>Selected Photos: {selectedPhotos.length}/5</p>
          )}
        </div>
      </div>

      {/* Photo Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
        {jobs.map(job => (
          <PhotoCard
            key={job.id}
            job={job}
            isSelected={selectedPhotos.includes(job.id)}
            onSelect={() => handleSelectPhoto(job.id)}
            canDownload={job.is_selected && !job.is_watermarked}
          />
        ))}
      </div>

      {/* Confirm Selection Button */}
      {user.has_purchased && selectedPhotos.length === 5 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4">
          <button
            onClick={handleConfirmSelection}
            className="w-full bg-primary-600 text-white py-3 rounded-lg"
          >
            Confirm Selection & Remove Watermarks
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## 🎨 Watermark Design

**Watermark Specs:**
- Position: Bottom-right corner
- Text: "GradGen.AI" in semi-transparent white
- Opacity: 50%
- Font: Bold, 24px
- Background: Semi-transparent dark overlay
- Padding: 10px

**Alternative: Logo Watermark**
- Use GradGen.AI logo SVG
- Position: Bottom-right
- Size: 80x30px
- Opacity: 60%

---

## 📝 Migration Steps

### Step 1: Database Migration
```sql
-- Add new columns to users table
ALTER TABLE users
  DROP COLUMN credits,
  ADD COLUMN free_prompts_remaining INTEGER DEFAULT 5,
  ADD COLUMN paid_prompts_remaining INTEGER DEFAULT 0,
  ADD COLUMN has_purchased BOOLEAN DEFAULT FALSE,
  ADD COLUMN selected_photo_ids JSON DEFAULT '[]';

-- Add new columns to generation_jobs table
ALTER TABLE generation_jobs
  ADD COLUMN is_watermarked BOOLEAN DEFAULT TRUE,
  ADD COLUMN is_selected BOOLEAN DEFAULT FALSE,
  ADD COLUMN prompt_type VARCHAR(50),
  ADD COLUMN original_image_path VARCHAR(500),
  ADD COLUMN watermarked_image_path VARCHAR(500);
```

### Step 2: Create Example Assets
1. Download 4-5 portraits from Unsplash
2. Save to `webapp/frontend/public/examples/before-*.jpg`
3. Generate graduation versions using batch script
4. Save to `webapp/frontend/public/examples/after-*.jpg`

### Step 3: Update Stripe Product
1. Create new product: "GradGen.AI Extended Package"
2. Set price: £19.99 (GBP)
3. Update `STRIPE_PRICE_ID_EXTENDED_PACKAGE` in .env

### Step 4: Deploy
1. Backend changes (database, watermark service, endpoints)
2. Frontend changes (landing page, dashboard, payment flow)
3. Test full flow:
   - Register → Get 5 free prompts
   - Generate 5 watermarked photos
   - Purchase £19.99 package
   - Generate 5 more photos
   - Select 5 favorites
   - Download unwatermarked versions

---

## ✅ Testing Checklist

- [ ] User registration gives 5 free prompts (not credits)
- [ ] Generation deducts prompts correctly
- [ ] All free photos have watermarks
- [ ] Cannot download unwatermarked photos without payment
- [ ] Payment successfully unlocks 5 additional prompts
- [ ] User can select exactly 5 photos (no more, no less)
- [ ] Selected photos have watermarks removed
- [ ] Can download only selected unwatermarked photos
- [ ] Mobile responsive design works on iPhone/Android
- [ ] Before/after slider works smoothly
- [ ] Payment flow completes successfully

---

## 🚀 Next Steps

Which phase would you like me to start implementing first?

1. **Landing Page + Examples** - Download photos, create before/after showcase
2. **Database Schema Changes** - Update User and Job models
3. **Watermark Service** - Implement watermark overlay system
4. **Prompt-Based Generation** - Update generation logic
5. **Payment + Selection System** - £19.99 tier and photo selection

Let me know and I'll start coding! 🎯
