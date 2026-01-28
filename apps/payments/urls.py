from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('sslcommerz/success/', views.sslcommerz_success, name='sslcommerz_success'),
    path('sslcommerz/fail/', views.sslcommerz_fail, name='sslcommerz_fail'),
    path('sslcommerz/cancel/', views.sslcommerz_cancel, name='sslcommerz_cancel'),
    path('sslcommerz/ipn/', views.sslcommerz_ipn, name='sslcommerz_ipn'),
]
