from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser

@shared_task
def delete_old_unverified_users(minutes=1):
    cutoff = timezone.now() - timedelta(minutes=minutes)
    qs = CustomUser.objects.filter(is_verified=False, otp_created_at__lt=cutoff).exclude(is_staff=True).exclude(is_superuser=True)
    count = qs.count()
    qs.delete()
    return f"Deleted {count} unverified users older than {minutes} minutes"
