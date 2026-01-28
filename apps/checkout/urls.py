from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('address/', views.checkout_address, name='address'),
    path('shipping/', views.checkout_shipping, name='shipping'),
    path('payment/', views.checkout_payment, name='payment'),
    path('review/', views.checkout_review, name='review'),
    path('place-order/', views.place_order, name='place_order'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
]
