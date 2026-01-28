from django.contrib import admin
from .models import ShippingMethod, CheckoutSession


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'get_delivery_estimate', 'free_above', 'is_active', 'sort_order']
    list_filter = ['is_active']
    list_editable = ['price', 'is_active', 'sort_order']
    search_fields = ['name']
    ordering = ['sort_order', 'price']


@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'user', 'current_step', 'shipping_method', 'created_at']
    list_filter = ['current_step', 'created_at']
    search_fields = ['session_key', 'user__email', 'guest_email']
    readonly_fields = ['created_at', 'updated_at']
