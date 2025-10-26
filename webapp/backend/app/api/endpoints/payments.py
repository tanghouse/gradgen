from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import stripe

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.models import User, Payment, CreditTransaction, TransactionType, PaymentStatus
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()


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

    # Handle payment intent succeeded
    if event["type"] == "payment_intent.succeeded":
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

            # Add credits to user
            user = db.query(User).filter(User.id == payment.user_id).first()
            if user:
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
