from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from threading import Thread
from django.conf import settings

from .models import Setting, Profile
from .utils import send_otp_via_email, send_welcome_email

User = get_user_model()

# pre_save: নতুন temporary attribute set করব old value track করার জন্য
@receiver(pre_save, sender=User)
def track_old_is_verified(sender, instance, **kwargs):
    if instance.pk:
        # DB query করা লাগবে না, old value আগে setattr করি
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_is_verified = old_instance.is_verified
        except sender.DoesNotExist:
            instance._old_is_verified = False
    else:
        instance._old_is_verified = False



@receiver(post_save, sender=User)
def create_account_email(sender, instance, created, **kwargs):
    # শুধু তখনই trigger হবে যখন is_verified True হবে
    send_email = False

    if instance.is_verified:
        if created:
            send_email = True
        elif not getattr(instance, "_old_is_verified", False):
            # update হলে এবং আগে False ছিল
            send_email = True

    if send_email:
        Thread(target=send_welcome_email, args=[instance]).start()
        profile, _ = Profile.objects.get_or_create(user=instance)
        setting, _ = Setting.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def send_otp_on_user_creation(sender, instance, created, **kwargs):
    if created and not instance.is_verified:
        Thread(target=send_otp_via_email, args=[instance]).start()
