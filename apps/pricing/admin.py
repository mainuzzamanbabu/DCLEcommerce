from django.contrib import admin
from .models import TaxClass, Price


@admin.register(TaxClass)
class TaxClassAdmin(admin.ModelAdmin):
    """Admin for TaxClass model."""
    
    list_display = ['name', 'rate_percent', 'country', 'is_default']
    list_filter = ['country', 'is_default']
    search_fields = ['name']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    """Admin for Price model."""
    
    list_display = [
        'variant', 'currency', 'list_price', 'sale_price', 
        'effective_price', 'discount_percent', 'tax_class'
    ]
    list_filter = ['currency', 'tax_class']
    search_fields = ['variant__sku', 'variant__product__name']
    raw_id_fields = ['variant']
    
    def effective_price(self, obj):
        return f"৳{obj.effective_price:,.2f}"
    effective_price.short_description = 'Effective Price'
    
    def discount_percent(self, obj):
        if obj.discount_percent > 0:
            return f"-{obj.discount_percent}%"
        return '-'
    discount_percent.short_description = 'Discount'
