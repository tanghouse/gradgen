from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel
import stripe
from typing import Optional

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.models import User, Payment, CreditTransaction, TransactionType, PaymentStatus
from app.models.promo_code import PromoCode
from app.core.config import settings
from app.schemas.payment import (
    CreatePremiumCheckoutRequest,
    CheckoutSessionResponse,
    PricingInfoResponse,
    PromoCodeValidationRequest,
    PromoCodeValidationResponse,
    PaymentStatusResponse
)
from app.services.referral_service import ReferralService

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()

# Business model constants
BASE_PREMIUM_PRICE = 39.99  # £39.99
DISCOUNTED_PREMIUM_PRICE = 19.99  # £19.99 with discount
REFERRAL_DISCOUNT_AMOUNT = 20.00  # £20 off


@router.get("/pricing-info", response_model=PricingInfoResponse)
async def get_pricing_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get pricing information including available discounts for the current user."""
    # Check referral discount eligibility
    referral_stats = ReferralService.get_referral_stats(db, current_user.id)

    discount_available = current_user.referral_discount_eligible
    discount_source = "referral" if current_user.referral_discount_eligible else None
    discounted_price = DISCOUNTED_PREMIUM_PRICE if discount_available else None

    return PricingInfoResponse(
        base_price=BASE_PREMIUM_PRICE,
        discounted_price=discounted_price,
        discount_available=discount_available,
        discount_source=discount_source,
        referral_discount_eligible=current_user.referral_discount_eligible,
        referrals_completed=referral_stats["completed_referrals"],
        referrals_needed=referral_stats["referrals_needed"]
    )


@router.post("/validate-promo-code", response_model=PromoCodeValidationResponse)
async def validate_promo_code(
    request: PromoCodeValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Validate a promo code and return discount information."""
    promo = db.query(PromoCode).filter(PromoCode.code == request.promo_code.upper()).first()

    if not promo:
        return PromoCodeValidationResponse(
            valid=False,
            message="Promo code not found"
        )

    if not promo.is_valid():
        return PromoCodeValidationResponse(
            valid=False,
            message="Promo code is expired or no longer valid"
        )

    return PromoCodeValidationResponse(
        valid=True,
        discount_amount=promo.discount_amount,
        discount_type=promo.discount_type,
        message=f"Valid! £{promo.discount_amount:.2f} discount applied"
    )


@router.post("/create-premium-checkout", response_model=CheckoutSessionResponse)
async def create_premium_checkout(
    request: CreatePremiumCheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe Checkout session for premium tier purchase.
    Supports referral discounts and promo codes.
    """
    # Check if user already purchased premium
    if current_user.has_purchased_premium:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already purchased premium tier"
        )

    # Calculate pricing
    original_price = BASE_PREMIUM_PRICE
    discount_applied = 0.0
    discount_source = None

    # Check for referral discount first (takes precedence)
    if current_user.referral_discount_eligible:
        discount_applied = REFERRAL_DISCOUNT_AMOUNT
        discount_source = "referral"

    # Check for promo code discount
    elif request.promo_code:
        promo = db.query(PromoCode).filter(
            PromoCode.code == request.promo_code.upper()
        ).first()

        if not promo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid promo code"
            )

        if not promo.is_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code has expired or reached maximum uses"
            )

        # Apply promo code discount
        if promo.discount_type == "fixed":
            discount_applied = promo.discount_amount
        elif promo.discount_type == "percentage":
            discount_applied = original_price * (promo.discount_amount / 100)

        discount_source = "promo_code"

    # Calculate final amount
    final_amount = max(0, original_price - discount_applied)
    amount_pence = int(final_amount * 100)  # Convert to pence for Stripe

    try:
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': 'GradGen Premium Tier',
                        'description': '5 additional premium prompts + unwatermark all 10 photos',
                    },
                    'unit_amount': amount_pence,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{settings.FRONTEND_URL}/generation/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/generation/cancelled",
            metadata={
                'user_id': current_user.id,
                'original_price': original_price,
                'discount_applied': discount_applied,
                'discount_source': discount_source or '',
                'promo_code': request.promo_code.upper() if request.promo_code else ''
            }
        )

        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            stripe_payment_intent_id=checkout_session.payment_intent if checkout_session.payment_intent else checkout_session.id,
            amount=final_amount,
            credits=0,  # Deprecated field
            status=PaymentStatus.PENDING,
            currency="gbp",
            original_price=original_price,
            discount_applied=discount_applied,
            discount_source=discount_source,
            promo_code_used=request.promo_code.upper() if request.promo_code else None
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return CheckoutSessionResponse(
            session_id=checkout_session.id,
            session_url=checkout_session.url,
            amount=final_amount,
            original_price=original_price,
            discount_applied=discount_applied,
            discount_source=discount_source
        )

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )


# Legacy endpoint - keeping for backward compatibility
class CreatePaymentIntentRequest(BaseModel):
    credits: int

class CreatePaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str


@router.post("/create-payment-intent", response_model=CreatePaymentIntentResponse)
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe payment intent for purchasing credits."""
    if request.credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credits must be positive"
        )

    # Calculate amount in cents
    amount_usd = request.credits / settings.CREDITS_PER_DOLLAR
    amount_cents = int(amount_usd * 100)

    try:
        # Create Stripe payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            metadata={
                "user_id": current_user.id,
                "credits": request.credits
            }
        )

        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            stripe_payment_intent_id=payment_intent.id,
            amount=amount_usd,
            credits=request.credits,
            status=PaymentStatus.PENDING,
            currency="usd"
        )
        db.add(payment)
        db.commit()

        return CreatePaymentIntentResponse(
            client_secret=payment_intent.client_secret,
            payment_intent_id=payment_intent.id
        )

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle checkout session completed (new business model)
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]

        # Get metadata
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        promo_code = metadata.get("promo_code")

        if not user_id:
            return {"status": "error", "message": "No user_id in metadata"}

        # Find user
        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            return {"status": "error", "message": "User not found"}

        # Mark user as having purchased premium
        user.has_purchased_premium = True

        # Queue background task to regenerate unwatermarked photos
        from app.tasks.generation_tasks import regenerate_unwatermarked_photos
        regenerate_task = regenerate_unwatermarked_photos.delay(user.id)

        # If referral discount was used, mark it as rewarded
        if user.referral_discount_eligible:
            user.referral_discount_eligible = False  # Reset for future purchases
            # Mark referrals as rewarded
            from app.models.referral import Referral, ReferralStatus
            referrals = db.query(Referral).filter(
                Referral.referrer_id == user.id,
                Referral.status == ReferralStatus.COMPLETED
            ).limit(3).all()

            for ref in referrals:
                ref.status = ReferralStatus.REWARDED
                ref.rewarded_at = func.now()

        # If promo code was used, increment usage
        if promo_code:
            promo = db.query(PromoCode).filter(PromoCode.code == promo_code).first()
            if promo:
                promo.current_uses += 1

        # Update payment record
        payment_intent_id = session.get("payment_intent")
        if payment_intent_id:
            payment = db.query(Payment).filter(
                Payment.stripe_payment_intent_id == payment_intent_id
            ).first()

            if payment:
                payment.status = PaymentStatus.SUCCEEDED

        db.commit()

        return {"status": "success", "message": "Premium tier activated"}

    # Handle payment intent succeeded (legacy support)
    elif event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        # Find payment record
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()

        if payment:
            # Update payment status
            payment.status = PaymentStatus.SUCCEEDED
            db.commit()

            # Legacy: Add credits to user (for old credit-based system)
            user = db.query(User).filter(User.id == payment.user_id).first()
            if user and payment.credits > 0:
                user.credits += payment.credits

                # Record transaction
                transaction = CreditTransaction(
                    user_id=user.id,
                    amount=payment.credits,
                    transaction_type=TransactionType.PURCHASE,
                    description=f"Purchased {payment.credits} credits",
                    reference_id=str(payment.id)
                )
                db.add(transaction)
                db.commit()

    # Handle payment intent failed
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()

        if payment:
            payment.status = PaymentStatus.FAILED
            db.commit()

    return {"status": "success"}


@router.get("/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend."""
    return {"publishable_key": settings.STRIPE_PUBLISHABLE_KEY}
