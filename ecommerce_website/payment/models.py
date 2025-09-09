from django.db import models
from django.conf import settings
from orders.models import Order

# Payment models are not needed as we're using Stripe's API directly
# This file is kept for Django app structure consistency
