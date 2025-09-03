import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_resturant_back_end.settings')

app = Celery('food_resturant_back_end')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
