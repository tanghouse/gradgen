# Email Setup Guide - Resend Configuration

This guide will help you configure email verification for GradGen using Resend.

## Why Resend?

- **Free Tier**: 3,000 emails/month, 100 emails/day
- **Easy Setup**: Simple API, no SMTP configuration needed
- **Reliable**: High deliverability rates
- **Developer-Friendly**: Great docs, modern API

---

## Step-by-Step Setup

### 1. Sign Up for Resend (5 minutes)

1. Go to **[resend.com](https://resend.com)**
2. Click **"Sign Up"** or **"Get Started"**
3. Sign up with your email or GitHub account
4. Verify your email if required

### 2. Get Your API Key (2 minutes)

1. Once logged in, go to **[API Keys](https://resend.com/api-keys)**
2. Click **"Create API Key"**
3. Name it: `GradGen Production`
4. **Permissions**: Full Access (or Email Send if available)
5. Click **"Create"**
6. **IMPORTANT**: Copy the API key immediately (starts with `re_`)
   - Example: `re_123456789abcdefghijklmnop`
   - You won't be able to see it again!

### 3. Add API Key to Railway (3 minutes)

1. Go to **[Railway Dashboard](https://railway.app/dashboard)**
2. Select your **GradGen project**
3. Click on your **backend service**
4. Go to **Variables** tab
5. Click **"+ New Variable"**
6. Add these variables:

```
RESEND_API_KEY=re_your_actual_api_key_here
RESEND_FROM_EMAIL=noreply@gradgen.ai
```

7. Click **"Add"** or **"Save"**
8. Railway will automatically redeploy your backend

### 4. Domain Verification (Optional but Recommended)

**For Testing:** You can skip this step and use Resend's test domain for now.

**For Production:** Verify your domain to send emails from `@gradgen.ai`

#### How to Verify Your Domain

1. In Resend dashboard, go to **[Domains](https://resend.com/domains)**
2. Click **"Add Domain"**
3. Enter: `gradgen.ai`
4. Resend will show DNS records you need to add
5. Go to **Cloudflare** (or your DNS provider)
6. Add these DNS records:
   - **TXT** record for verification
   - **MX** records for receiving bounces (optional)
   - **DKIM** records for authentication

Example DNS records from Resend:
```
Type    Name                        Value
TXT     resend._domainkey          [provided by Resend]
MX      gradgen.ai                 feedback-smtp.resend.com (priority 10)
```

7. Return to Resend and click **"Verify"**
8. Wait 5-10 minutes for DNS propagation
9. Check verification status in Resend dashboard

### 5. Re-enable Email Verification in Code (2 minutes)

Once Resend is configured, re-enable email verification:

1. Edit `backend/app/api/endpoints/auth.py`
2. Find this section (around line 82):

```python
# Check if email is verified (REQUIRED)
# TODO: Re-enable after Resend is configured
# if not user.email_verified:
#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Email not verified. Please check your email for the verification link."
#     )
```

3. **Uncomment** the email verification check:

```python
# Check if email is verified (REQUIRED)
if not user.email_verified:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Email not verified. Please check your email for the verification link."
    )
```

4. Commit and push:

```bash
git add backend/app/api/endpoints/auth.py
git commit -m "Re-enable email verification - Resend configured"
git push origin main
```

### 6. Test Email Sending (5 minutes)

#### Test 1: Registration Email

1. Go to your app: `https://gradgen-production.up.railway.app/register`
2. Register with a **real email** you have access to
3. Check your inbox for verification email
4. Click the verification link
5. Verify you can login

#### Test 2: Resend Verification Email

1. Try logging in with unverified account
2. You should see "Email not verified" message
3. Use the "Resend verification" button
4. Check inbox for new verification email

#### Test 3: Check Resend Dashboard

1. Go to **[Resend Logs](https://resend.com/logs)**
2. You should see your sent emails
3. Check delivery status
4. View email content

---

## Email Templates

GradGen sends these emails:

### 1. **Verification Email** (auth.py line 52)
- **When**: User registers
- **Subject**: "Verify your GradGen.AI email address"
- **Content**: Button to verify email, 24-hour expiry

### 2. **Welcome Email** (auth.py line 107)
- **When**: Email is verified
- **Subject**: "Welcome to GradGen.AI - Get started now!"
- **Content**: Welcome message, free credits info

---

## Troubleshooting

### Email Not Arriving

**Check 1: Spam Folder**
- Verification emails sometimes go to spam
- Add `noreply@gradgen.ai` to contacts

**Check 2: Resend Dashboard**
- Go to [Resend Logs](https://resend.com/logs)
- Check if email was sent
- Look for delivery errors

**Check 3: API Key**
- Verify `RESEND_API_KEY` is set in Railway
- Check it starts with `re_`
- Ensure no extra spaces

**Check 4: From Email**
- If domain is NOT verified, use: `onboarding@resend.dev`
- Update Railway variable: `RESEND_FROM_EMAIL=onboarding@resend.dev`

**Check 5: Backend Logs**
- Check Railway logs for email sending errors
- Look for "Failed to send verification email"

### Domain Verification Failed

**DNS Propagation**
- Wait 10-30 minutes for DNS to propagate
- Use [DNS Checker](https://dnschecker.org) to verify records

**Incorrect Records**
- Double-check TXT, MX, DKIM records
- Ensure no typos in Cloudflare

**Cloudflare Proxy**
- For TXT/DKIM records, **disable** Cloudflare proxy (grey cloud icon)
- MX records don't need proxying

### Emails Going to Spam

**Without Domain Verification:**
- Emails from `onboarding@resend.dev` may go to spam
- Solution: Verify your domain

**With Domain Verification:**
- Ensure DKIM records are correct
- Check SPF record exists
- Consider adding DMARC record

---

## Resend Limits

### Free Tier
- **3,000 emails/month**
- **100 emails/day**
- Perfect for testing and small apps

### Pro Tier ($20/month)
- **50,000 emails/month**
- **1,000 emails/day**
- Better deliverability
- Priority support

### Enterprise
- Custom limits
- Dedicated IPs
- Contact Resend for pricing

---

## Testing Without Resend (Alternative)

If you don't want to set up Resend right now:

### Option 1: Keep Email Verification Disabled
- Already done in current deployment
- Users can register and login immediately
- **Not recommended for production**

### Option 2: Manual Verification via Database
```sql
UPDATE users SET email_verified = TRUE WHERE email = 'user@example.com';
```

### Option 3: Use Mailtrap for Testing
1. Sign up at [mailtrap.io](https://mailtrap.io)
2. Get SMTP credentials
3. Update email service to use SMTP instead of Resend
4. All emails go to Mailtrap inbox (not real users)

---

## Production Checklist

Before going live, ensure:

- [ ] Resend account created
- [ ] API key added to Railway
- [ ] Domain verified in Resend
- [ ] DNS records configured in Cloudflare
- [ ] Test emails sent successfully
- [ ] Emails not going to spam
- [ ] Email verification re-enabled in code
- [ ] `RESEND_FROM_EMAIL` uses your domain (`noreply@gradgen.ai`)
- [ ] Monitored Resend dashboard for first week

---

## Cost Estimation

**Startup (0-100 users/month):**
- Resend: **FREE**
- ~50-200 emails/month

**Growth (100-500 users/month):**
- Resend: **FREE** (within 3,000/month limit)
- ~500-1,500 emails/month

**Scale (500+ users/month):**
- Resend Pro: **$20/month**
- Up to 50,000 emails/month

---

## Quick Reference

| Setting | Development | Production |
|---------|------------|------------|
| **RESEND_API_KEY** | `re_test_xxxxx` | `re_prod_xxxxx` |
| **RESEND_FROM_EMAIL** | `onboarding@resend.dev` | `noreply@gradgen.ai` |
| **Domain Verification** | Optional | Required |
| **Email Verification** | Can disable | Must enable |

---

## Support

- **Resend Docs**: https://resend.com/docs
- **Resend Support**: support@resend.com
- **GradGen Issues**: See main README for support channels

---

**Created**: November 2025
**Last Updated**: November 2025
