from django.db import models
from django.conf import settings
from apps.catalog.models import ProductVariant


class Cart(models.Model):
    """Shopping cart for authenticated users."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='user'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'shopping cart'
        verbose_name_plural = 'shopping carts'
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def total_quantity(self):
        """Total number of items in the cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Total price of all items in the cart."""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Items within a database cart."""
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='cart'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='product variant'
    )
    quantity = models.PositiveIntegerField('quantity', default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'cart item'
        verbose_name_plural = 'cart items'
        unique_together = ('cart', 'variant')
    
    def __str__(self):
        return f"{self.quantity} x {self.variant}"
    
    @property
    def unit_price(self):
        """Effective unit price from variant."""
        if hasattr(self.variant, 'price'):
            return self.variant.price.effective_price
        return 0
    
    @property
    def total_price(self):
        """Total price for this line item."""
        return self.unit_price * self.quantity
