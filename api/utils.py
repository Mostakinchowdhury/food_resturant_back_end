
import random, datetime
from django.core.mail import send_mail
from django.utils import timezone

def generate_otp():
    return str(random.randint(100000, 999999))

# html templates can also be used for better formatting otp emails
def generate_html_otp_message(otp):
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <div style="padding: 20px; text-align: center; border-bottom: 1px solid #eeeeee;">
                    <h1 style="color: #333333;">Email Verification</h1>
                </div>
                <div style="padding: 20px; text-align: center;">
                    <p style="font-size: 16px; color: #555555;">Your One-Time Password (OTP) is:</p>
                    <p style="font-size: 24px; font-weight: bold; color: #007BFF;">{otp}</p>
                    <p style="font-size: 14px; color: #888888;">This OTP is valid for 5 minutes. Please do not share it with anyone.</p>
                </div>
                <div style="padding: 20px; text-align: center; border-top: 1px solid #eeeeee;">
                    <p style="font-size: 12px; color: #aaaaaa;">If you did not request this email, please ignore it.</p>
                </div>
            </div>
        </body>
    </html>
    """
def send_otp_via_email(user):
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = timezone.now() + datetime.timedelta(minutes=5)
    user.save()
    subject = "Email Verification OTP"
    message = f"Your OTP msg It is valid for 5 minutes."
    send_mail(subject=subject,message=message, html_message=generate_html_otp_message(otp), from_email="OrderUK <chowdhurymostakin02@gmail.com>", recipient_list=[user.email])
