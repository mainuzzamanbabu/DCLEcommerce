from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['variant', 'product_name', 'variant_name', 'sku', 'unit_price', 'total_price']
    fields = ['variant', 'product_name', 'variant_name', 'quantity', 'unit_price', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'note', 'created_by', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'guest_email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'guest_email', 'guest_phone', 'status', 'payment_status')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'shipping_method_name', 'shipping_cost', 'estimated_delivery', 'tracking_number')
        }),
        ('Billing', {
            'fields': ('billing_address',)
        }),
        ('Totals', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total', 'promo_code')
        }),
        ('Notes', {
            'fields': ('customer_note', 'admin_note')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_transaction_id', 'paid_at')
        }),
        ('Tracking', {
            'fields': ('shipped_at', 'delivered_at', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    @admin.action(description='Mark selected orders as Confirmed')
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    
    @admin.action(description='Mark selected orders as Processing')
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    
    @admin.action(description='Mark selected orders as Shipped')
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='shipped', shipped_at=timezone.now())
    
    @admin.action(description='Mark selected orders as Delivered')
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='delivered', delivered_at=timezone.now())


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'total_price']
    search_fields = ['order__order_number', 'product_name', 'sku']
