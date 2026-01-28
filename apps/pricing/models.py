from django.db import models
from apps.catalog.models import ProductVariant


class TaxClass(models.Model):
    """Tax classification for products."""
    
    name = models.CharField('name', max_length=100)
    rate_percent = models.DecimalField(
        'rate (%)',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    country = models.CharField('country', max_length=100, blank=True, default='Bangladesh')
    is_default = models.BooleanField('default', default=False)
    
    class Meta:
        verbose_name = 'tax class'
        verbose_name_plural = 'tax classes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rate_percent}%)"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            TaxClass.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Price(models.Model):
    """Pricing for product variants."""
    
    CURRENCY_CHOICES = [
        ('BDT', 'Bangladeshi Taka'),
        ('USD', 'US Dollar'),
    ]
    
    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='price',
        verbose_name='variant'
    )
    
    currency = models.CharField(
        'currency',
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='BDT'
    )
    
    list_price = models.DecimalField(
        'list price (MRP)',
        max_digits=12,
        decimal_places=2,
        help_text='Maximum retail price'
    )
    sale_price = models.DecimalField(
        'sale price',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Special sale price (leave blank if not on sale)'
    )
    cost_price = models.DecimalField(
        'cost price',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Purchase/cost price (for internal use)'
    )
    
    tax_class = models.ForeignKey(
        TaxClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prices',
        verbose_name='tax class'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'price'
        verbose_name_plural = 'prices'
    
    def __str__(self):
        effective = self.effective_price
        return f"{self.currency} {effective:,.2f}"
    
    @property
    def effective_price(self):
        """Get the effective selling price."""
        return self.sale_price if self.sale_price else self.list_price
    
    @property
    def is_on_sale(self):
        """Check if product is on sale."""
        return self.sale_price is not None and self.sale_price < self.list_price
    
    @property
    def discount_percent(self):
        """Calculate discount percentage."""
        if not self.is_on_sale:
            return 0
        return int(((self.list_price - self.sale_price) / self.list_price) * 100)
    
    def get_tax_amount(self):
        """Calculate tax amount based on tax class."""
        if self.tax_class:
            return self.effective_price * (self.tax_class.rate_percent / 100)
        return 0
    
    def get_price_with_tax(self):
        """Get price including tax."""
        return self.effective_price + self.get_tax_amount()
