from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.urls import reverse
import uuid


def generate_order_number():
    """Generate unique order number."""
    return f"DCL-{get_random_string(8).upper()}"


class Order(models.Model):
    """Customer orders with full address and item snapshots."""
    
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(
        'order number',
        max_length=50,
        unique=True,
        default=generate_order_number
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='user'
    )
    
    # Status
    status = models.CharField(
        'status',
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        'payment status',
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Shipping address snapshot (stored as JSON for immutability)
    shipping_address = models.JSONField('shipping address', default=dict)
    billing_address = models.JSONField('billing address', default=dict)
    
    # Shipping method
    shipping_method_name = models.CharField('shipping method', max_length=100, blank=True)
    shipping_cost = models.DecimalField('shipping cost', max_digits=10, decimal_places=2, default=0)
    estimated_delivery = models.CharField('estimated delivery', max_length=100, blank=True)
    
    # Totals
    subtotal = models.DecimalField('subtotal', max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField('tax amount', max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField('discount amount', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('total', max_digits=12, decimal_places=2, default=0)
    
    # Guest info
    guest_email = models.EmailField('guest email', blank=True)
    guest_phone = models.CharField('guest phone', max_length=20, blank=True)
    
    # Promo
    promo_code = models.CharField('promo code', max_length=50, blank=True)
    
    # Notes
    customer_note = models.TextField('customer note', blank=True)
    admin_note = models.TextField('admin note', blank=True)
    
    # Payment info
    payment_method = models.CharField('payment method', max_length=50, blank=True)
    payment_transaction_id = models.CharField('transaction ID', max_length=100, blank=True)
    paid_at = models.DateTimeField('paid at', null=True, blank=True)
    
    # Tracking
    tracking_number = models.CharField('tracking number', max_length=100, blank=True)
    shipped_at = models.DateTimeField('shipped at', null=True, blank=True)
    delivered_at = models.DateTimeField('delivered at', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return self.order_number
    
    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'order_number': self.order_number})
    
    def get_email(self):
        """Get customer email."""
        if self.user:
            return self.user.email
        return self.guest_email
    
    def get_shipping_address_display(self):
        """Format shipping address for display."""
        addr = self.shipping_address
        if not addr:
            return "No address"
        parts = [addr.get('full_name', ''), addr.get('address_line1', '')]
        if addr.get('address_line2'):
            parts.append(addr.get('address_line2'))
        parts.append(f"{addr.get('city', '')}, {addr.get('postal_code', '')}")
        parts.append(addr.get('country', 'Bangladesh'))
        return '\n'.join(filter(None, parts))
    
    def calculate_totals(self):
        """Recalculate order totals from items."""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total = self.subtotal + self.shipping_cost + self.tax_amount - self.discount_amount
        return self.total


class OrderItem(models.Model):
    """Order line item with product snapshots."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='order'
    )
    variant = models.ForeignKey(
        'catalog.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name='product variant'
    )
    
    # Product snapshot (for historical reference)
    product_name = models.CharField('product name', max_length=300)
    variant_name = models.CharField('variant name', max_length=200, blank=True)
    sku = models.CharField('SKU', max_length=100, blank=True)
    product_image = models.URLField('product image URL', blank=True)
    
    # Pricing
    quantity = models.PositiveIntegerField('quantity', default=1)
    unit_price = models.DecimalField('unit price', max_digits=12, decimal_places=2)
    total_price = models.DecimalField('total price', max_digits=12, decimal_places=2)
    
    # Digital products
    is_digital = models.BooleanField('digital product', default=False)
    download_url = models.URLField('download URL', blank=True)
    license_key = models.TextField('license key', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'order item'
        verbose_name_plural = 'order items'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate total price before saving."""
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Track order status changes."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='order'
    )
    status = models.CharField('status', max_length=20, choices=Order.ORDER_STATUS_CHOICES)
    note = models.TextField('note', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='created by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'order status history'
        verbose_name_plural = 'order status histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
