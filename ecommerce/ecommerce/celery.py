from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings.py')
app = Celery('ecommerce')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    'Check product expiry': {
        'task': 'customer.task.check_expiry_date',
        'schedule': crontab(hour=13, minute=11)
    }
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')