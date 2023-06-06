from datetime import datetime, date, timedelta
import json
from celery import shared_task
from .models import Product

@shared_task
def check_expiry_date():
    current_day = date.today()
    check_expiry = Product.objects.filter(end_date=current_day)
    data = list(check_expiry.values())
    print(data)
    # Serialize the data using JSON
    serialized_data = json.dumps(data)

    if check_expiry:
        check_expiry.update(is_active=False)
        return serialized_data
    return serialized_data
