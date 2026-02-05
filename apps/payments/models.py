from django.db import models
from django.conf import settings
from apps.orders.models import Order
import uuid

class PaymentMethod(models.Model):
    """Configuration for available payment methods."""
    
    name = models.CharField('name', max_length=100)
    code = models.CharField('code', max_length=50, unique=True, help_text='Internal code e.g., sslcommerz, cod')
    description = models.TextField('description', blank=True)
    instruction = models.TextField('payment instruction', blank=True, help_text='Instruction shown to customer')
    
    logo = models.ImageField('logo', upload_to='payment_logos/', blank=True, null=True)
    
    is_active = models.BooleanField('active', default=True)
    is_test_mode = models.BooleanField('test mode', default=True)
    
    # Provider-specific settings (could be stored as JSON for flexibility)
    settings = models.JSONField('payment settings', default=dict, blank=True, help_text='API keys, store IDs, etc.')
    
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'payment method'
        verbose_name_plural = 'payment methods'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

class PaymentTransaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    transaction_id = models.CharField('transaction id', max_length=100, unique=True, default=uuid.uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name='order')
    amount = models.DecimalField('amount', max_digits=12, decimal_places=2)
    currency = models.CharField('currency', max_length=10, default='BDT')
    payment_method = models.CharField('payment method', max_length=50) # 'sslcommerz', 'cod'
    provider_reference = models.CharField('provider reference', max_length=255, blank=True) # SSLCommerz val_id or bank_tran_id
    status = models.CharField('status', max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Store provider response for audit
    provider_response = models.JSONField('provider response', default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.order.order_number} ({self.status})"

class WebhookEvent(models.Model):
    provider = models.CharField('provider', max_length=50) # 'sslcommerz'
    event_type = models.CharField('event type', max_length=100, blank=True)
    payload = models.JSONField('payload')
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook {self.provider} - {self.created_at}"
