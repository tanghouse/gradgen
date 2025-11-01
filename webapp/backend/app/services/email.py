import resend
from app.core.config import settings
from typing import Optional

# Initialize Resend
resend.api_key = settings.RESEND_API_KEY


class EmailService:
    """Service for sending emails using Resend."""

    @staticmethod
    async def send_verification_email(email: str, token: str, full_name: Optional[str] = None) -> bool:
        """Send email verification email."""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <!-- Header -->
                                <tr>
                                    <td style="background-color: #4F46E5; padding: 30px 40px; text-align: center;">
                                        <h1 style="margin: 0; color: #ffffff; font-size: 28px;">TangHouse</h1>
                                        <p style="margin: 10px 0 0 0; color: #E0E7FF; font-size: 14px;">Graduation Portrait Generator</p>
                                    </td>
                                </tr>

                                <!-- Body -->
                                <tr>
                                    <td style="padding: 40px;">
                                        <h2 style="margin: 0 0 20px 0; color: #1F2937; font-size: 24px;">Verify Your Email Address</h2>
                                        <p style="margin: 0 0 20px 0; color: #4B5563; font-size: 16px; line-height: 1.5;">
                                            {f"Hi {full_name}," if full_name else "Hi there,"}
                                        </p>
                                        <p style="margin: 0 0 20px 0; color: #4B5563; font-size: 16px; line-height: 1.5;">
                                            Thanks for signing up with TangHouse! To complete your registration and start generating beautiful graduation portraits, please verify your email address by clicking the button below.
                                        </p>

                                        <!-- CTA Button -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                            <tr>
                                                <td align="center">
                                                    <a href="{verification_url}" style="display: inline-block; background-color: #4F46E5; color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: 600;">
                                                        Verify Email Address
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>

                                        <p style="margin: 20px 0 0 0; color: #6B7280; font-size: 14px; line-height: 1.5;">
                                            Or copy and paste this link into your browser:
                                        </p>
                                        <p style="margin: 10px 0 0 0; color: #4F46E5; font-size: 14px; word-break: break-all;">
                                            {verification_url}
                                        </p>

                                        <p style="margin: 30px 0 0 0; color: #6B7280; font-size: 14px; line-height: 1.5;">
                                            This link will expire in 24 hours. If you didn't create an account with TangHouse, you can safely ignore this email.
                                        </p>
                                    </td>
                                </tr>

                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #F9FAFB; padding: 30px 40px; text-align: center; border-top: 1px solid #E5E7EB;">
                                        <p style="margin: 0 0 10px 0; color: #6B7280; font-size: 14px;">
                                            TangHouse - Professional Graduation Portraits
                                        </p>
                                        <p style="margin: 0; color: #9CA3AF; font-size: 12px;">
                                            © 2025 TangHouse. All rights reserved.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            params = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [email],
                "subject": "Verify your TangHouse email address",
                "html": html_content,
            }

            resend.Emails.send(params)
            return True

        except Exception as e:
            print(f"Failed to send verification email: {e}")
            return False

    @staticmethod
    async def send_welcome_email(email: str, full_name: Optional[str] = None) -> bool:
        """Send welcome email after email verification."""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0;">
            </head>
            <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <!-- Header -->
                                <tr>
                                    <td style="background-color: #10B981; padding: 30px 40px; text-align: center;">
                                        <h1 style="margin: 0; color: #ffffff; font-size: 28px;">Welcome to TangHouse!</h1>
                                        <p style="margin: 10px 0 0 0; color: #D1FAE5; font-size: 14px;">Your email has been verified</p>
                                    </td>
                                </tr>

                                <!-- Body -->
                                <tr>
                                    <td style="padding: 40px;">
                                        <h2 style="margin: 0 0 20px 0; color: #1F2937; font-size: 24px;">You're all set!</h2>
                                        <p style="margin: 0 0 20px 0; color: #4B5563; font-size: 16px; line-height: 1.5;">
                                            {f"Hi {full_name}," if full_name else "Hi there,"}
                                        </p>
                                        <p style="margin: 0 0 20px 0; color: #4B5563; font-size: 16px; line-height: 1.5;">
                                            Your email has been successfully verified! You can now start creating stunning graduation portraits with TangHouse.
                                        </p>

                                        <div style="background-color: #EEF2FF; border-left: 4px solid #4F46E5; padding: 20px; margin: 30px 0; border-radius: 4px;">
                                            <p style="margin: 0 0 10px 0; color: #1F2937; font-size: 16px; font-weight: 600;">
                                                🎉 You've received 5 free credits!
                                            </p>
                                            <p style="margin: 0; color: #4B5563; font-size: 14px; line-height: 1.5;">
                                                Use your free credits to generate your first graduation portraits.
                                            </p>
                                        </div>

                                        <!-- CTA Button -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                            <tr>
                                                <td align="center">
                                                    <a href="{settings.FRONTEND_URL}/generate" style="display: inline-block; background-color: #4F46E5; color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: 600;">
                                                        Generate Your Portrait
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #F9FAFB; padding: 30px 40px; text-align: center; border-top: 1px solid #E5E7EB;">
                                        <p style="margin: 0 0 10px 0; color: #6B7280; font-size: 14px;">
                                            TangHouse - Professional Graduation Portraits
                                        </p>
                                        <p style="margin: 0; color: #9CA3AF; font-size: 12px;">
                                            © 2025 TangHouse. All rights reserved.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            params = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [email],
                "subject": "Welcome to TangHouse - Get started now!",
                "html": html_content,
            }

            resend.Emails.send(params)
            return True

        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return False
