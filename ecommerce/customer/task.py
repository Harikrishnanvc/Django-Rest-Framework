from datetime import datetime, date, timedelta

from celery import shared_task
from .models import Product

@shared_task
def check_expiry_date():
    current_day = date.today()
    expiry_date = current_day + timedelta(60)
    check_expiry = Product.objects.filter(end_date__gt=expiry_date)

    if check_expiry:
        check_expiry.update(is_active=False)
        return check_expiry
    return check_expiry
