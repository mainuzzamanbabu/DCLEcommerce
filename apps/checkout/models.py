from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
import uuid


class ShippingMethod(models.Model):
    """Available shipping methods."""
    
    name = models.CharField('name', max_length=100)
    description = models.TextField('description', blank=True)
    price = models.DecimalField('price', max_digits=10, decimal_places=2)
    
    # Delivery time
    min_delivery_days = models.PositiveIntegerField('min delivery days', default=1)
    max_delivery_days = models.PositiveIntegerField('max delivery days', default=3)
    
    # Conditions
    is_active = models.BooleanField('active', default=True)
    free_above = models.DecimalField(
        'free above amount',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Free shipping for orders above this amount'
    )
    
    # Ordering
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'shipping method'
        verbose_name_plural = 'shipping methods'
        ordering = ['sort_order', 'price']
    
    def __str__(self):
        return f"{self.name} - ৳{self.price}"
    
    def get_delivery_estimate(self):
        """Return delivery estimate string."""
        if self.min_delivery_days == self.max_delivery_days:
            return f"{self.min_delivery_days} day(s)"
        return f"{self.min_delivery_days}-{self.max_delivery_days} days"
    
    def get_price_for_amount(self, order_subtotal):
        """Calculate shipping price based on order subtotal."""
        if self.free_above and order_subtotal >= self.free_above:
            return 0
        return self.price


class CheckoutSession(models.Model):
    """Temporary storage for checkout data."""
    
    CHECKOUT_STEP_CHOICES = [
        ('address', 'Address'),
        ('shipping', 'Shipping'),
        ('payment', 'Payment'),
        ('review', 'Review'),
    ]
    
    session_key = models.CharField('session key', max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='checkout_sessions',
        verbose_name='user'
    )
    
    # Current step
    current_step = models.CharField(
        'current step',
        max_length=20,
        choices=CHECKOUT_STEP_CHOICES,
        default='address'
    )
    
    # Selected address
    shipping_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipping_checkout_sessions',
        verbose_name='shipping address'
    )
    billing_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_checkout_sessions',
        verbose_name='billing address'
    )
    
    # Guest checkout info
    guest_email = models.EmailField('guest email', blank=True)
    guest_phone = models.CharField('guest phone', max_length=20, blank=True)
    
    # Guest address (JSON snapshot)
    guest_shipping_address = models.JSONField('guest shipping address', default=dict, blank=True)
    guest_billing_address = models.JSONField('guest billing address', default=dict, blank=True)
    same_as_shipping = models.BooleanField('billing same as shipping', default=True)
    
    # Shipping
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkout_sessions',
        verbose_name='shipping method'
    )
    
    # Promo code
    promo_code = models.CharField('promo code', max_length=50, blank=True)
    
    # Notes
    customer_note = models.TextField('customer note', blank=True)
    
    # Payment
    payment_method = models.CharField('payment method', max_length=50, blank=True) # 'sslcommerz', 'cod'
    
    # Cart data snapshot
    cart_data = models.JSONField('cart data', default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField('expires at', null=True, blank=True)
    
    class Meta:
        verbose_name = 'checkout session'
        verbose_name_plural = 'checkout sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Checkout for {self.user.email}"
        return f"Guest checkout {self.session_key[:8]}..."
    
    def is_complete(self):
        """Check if all checkout steps are complete."""
        has_address = bool(self.shipping_address or self.guest_shipping_address)
        has_shipping = bool(self.shipping_method)
        has_payment = bool(self.payment_method)
        return has_address and has_shipping and has_payment
