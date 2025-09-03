from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from threading import Thread
from django.conf import settings
from datetime import datetime
from .utils import send_otp_via_email

User=get_user_model()

def genaret_msg(instance):
  return f'''
Wellcome, {instance.first_name} {instance.last_name}!

Thank you for join in OrderUk. We're excited to have you on board.
Your account has been successfully created and ready to use.
We provide a wide range of delicious food options from various cuisines.
See Menu: {settings.FRONTEND_URL}/menu
Use This coupon code in your first Order: {"WellcomeorderUK20"} — and claim {'20%'+" "+'discount'}!

Help?: {settings.EMAIL_HOST_USER}
© {datetime.now().strftime('%Y')} OrderUk | Privacy: {settings.FRONTEND_URL}/privacy | Terms: {settings.FRONTEND_URL}/terms

'''

def send_welcome_email(instance,created):
  if created:
    send_mail(subject="Wellcome to OrderUK",from_email="OrderUK <chowdhurymostakin02@gmail.com>",message=genaret_msg(instance),recipient_list=[instance.email,],fail_silently=False)

@receiver(post_save, sender=User)
def create_account_email(sender, instance, created, **kwargs):
    if instance.is_verified:
        Thread(target=send_welcome_email, args=[instance,created]).start()

@receiver(post_save, sender=User)
def send_otp_on_user_creation(sender, instance, created, **kwargs):
    if created and not instance.is_verified:
        Thread(target=send_otp_via_email, args=[instance]).start()

