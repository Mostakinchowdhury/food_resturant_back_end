
import random
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from datetime import datetime,timedelta

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
                <div class="footer">
                &copy; {2025} OrderUK. All rights reserved and developed by Mostakin chowdhury.
            </div>
            </div>
        </body>
    </html>
    """
def send_otp_via_email(user):
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = timezone.now() + timedelta(minutes=5)
    user.save()
    subject = "Email Verification OTP"
    message = f"Your OTP msg It is valid for 5 minutes."
    send_mail(subject=subject,message=message, html_message=generate_html_otp_message(otp), from_email="OrderUK <chowdhurymostakin02@gmail.com>", recipient_list=[user.email])



# genaret wellcome html msg
def generate_msg_html(instance):
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #ff6600;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            p {{
                font-size: 16px;
                line-height: 1.5;
                margin: 10px 0;
            }}
            a.button {{
                display: inline-block;
                padding: 10px 20px;
                margin: 15px 0;
                background-color: #ff6600;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                margin-top: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome, {instance.first_name} {instance.last_name}!</h1>
            <p>Thank you for joining <strong>OrderUK</strong>. We're excited to have you on board.</p>
            <p>Your account has been successfully created and is ready to use.</p>
            <p>We provide a wide range of delicious food options from various cuisines.</p>
            <p><a class="button" href="{settings.FRONTEND_URL}/menu">See Menu</a></p>
            <p>Use this coupon code on your first order: <strong>WellcomeorderUK20</strong> — and claim <strong>20% discount</strong>!</p>
            <p>Need help? Contact us: <a href="mailto:{settings.EMAIL_HOST_USER}">{settings.EMAIL_HOST_USER}</a></p>
            <div class="footer">
                &copy; {datetime.now().strftime('%Y')} OrderUK | 
                <a href="{settings.FRONTEND_URL}/privacy">Privacy Policy</a> | 
                <a href="{settings.FRONTEND_URL}/terms">Terms & Conditions</a>
            </div>
            <div class="footer">
                &copy; {2025} OrderUK. All rights reserved and developed by Mostakin chowdhury.
            </div>
        </div>
    </body>
    </html>
    """

def send_welcome_email(instance):
    myemail=settings.EMAIL_HOST_USER
    send_mail(
        subject="Welcome to OrderUK",
        from_email=f"OrderUK <{myemail or "chowdhurymostakin02@gmail.com"}>",
        message="Welcome to {instance.first_name} {instance.last_name}!",
        html_message=generate_msg_html(instance),
        recipient_list=[instance.email],
    )



# password reset mail

def password_reset_email(link):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Password Reset</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f6f8;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background: #ffffff;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }}
            h2 {{
                color: #333;
                text-align: center;
            }}
            p {{
                color: #555;
                font-size: 15px;
                line-height: 1.6;
            }}
            .btn {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
                color: #fff;
                background: #007BFF;
                text-decoration: none;
                border-radius: 6px;
                transition: background 0.3s ease;
            }}
            .btn:hover {{
                background: #0056b3;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 13px;
                color: #888;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Password Reset Request</h2>
            <p>Hello,</p>
            <p>We received a request to reset your password. Click the button below to reset it:</p>
            <p style="text-align:center;">
                <a href="{link}" class="btn">Reset Password</a>
            </p>
            <p>If you did not request this, please ignore this email. This link will expire in 30 minutes for your security.</p>
            <div class="footer">
                &copy; {2025} OrderUK. All rights reserved and developed by Mostakin chowdhury.
            </div>
        </div>
    </body>
    </html>
    """
