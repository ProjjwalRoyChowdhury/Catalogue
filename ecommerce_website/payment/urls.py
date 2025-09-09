from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'payment'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('success/', views.payment_success, name='success'),
    path('canceled/', views.payment_canceled, name='canceled'),
    path('webhook/', csrf_exempt(views.stripe_webhook), name='webhook'),
]