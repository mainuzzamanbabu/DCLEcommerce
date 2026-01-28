from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductAttribute, ProductVariant, VariantInventory, DigitalLicenseKey
)
from apps.pricing.models import Price


# Inlines
class ProductImageInline(admin.TabularInline):
    """Inline for product images."""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


class PriceInline(admin.StackedInline):
    """Inline for variant pricing."""
    model = Price
    extra = 0
    fields = ['currency', 'list_price', 'sale_price', 'cost_price', 'tax_class']


class VariantInventoryInline(admin.StackedInline):
    """Inline for variant inventory."""
    model = VariantInventory
    extra = 0
    fields = ['stock_qty', 'reserved_qty', 'low_stock_threshold']
    readonly_fields = ['reserved_qty']


class ProductVariantInline(admin.TabularInline):
    """Inline for product variants."""
    model = ProductVariant
    extra = 1
    fields = ['sku', 'variant_name', 'is_active']
    show_change_link = True


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model."""
    
    list_display = ['name', 'parent', 'is_active', 'sort_order', 'product_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'parent', 'description', 'image')
        }),
        ('Status', {
            'fields': ('is_active', 'sort_order')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


# Brand Admin
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin for Brand model."""
    
    list_display = ['name', 'is_active', 'is_featured', 'product_count']
    list_filter = ['is_active', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'logo', 'description', 'website')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product model."""
    
    list_display = [
        'name', 'category', 'brand', 'product_type', 
        'is_active', 'is_featured', 'variant_count', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'product_type', 'category', 'brand']
    search_fields = ['name', 'short_description', 'description']
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'product_type')
        }),
        ('Classification', {
            'fields': ('category', 'brand')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'warranty_months')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_featured', 'remove_featured', 'activate', 'deactivate']
    
    def variant_count(self, obj):
        return obj.variants.count()
    variant_count.short_description = 'Variants'
    
    @admin.action(description='Mark selected products as featured')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    
    @admin.action(description='Remove featured status')
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
    
    @admin.action(description='Activate selected products')
    def activate(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description='Deactivate selected products')
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)


# Product Variant Admin
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin for ProductVariant model."""
    
    list_display = [
        'sku', 'product', 'variant_name', 'get_price', 
        'get_stock', 'is_active'
    ]
    list_filter = ['is_active', 'product__category', 'product__brand']
    search_fields = ['sku', 'variant_name', 'product__name']
    raw_id_fields = ['product']
    
    inlines = [PriceInline, VariantInventoryInline]
    
    fieldsets = (
        (None, {
            'fields': ('product', 'sku', 'variant_name')
        }),
        ('Details', {
            'fields': ('attributes', 'barcode', 'weight_kg')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def get_price(self, obj):
        if hasattr(obj, 'price'):
            return f"৳{obj.price.effective_price:,.2f}"
        return '-'
    get_price.short_description = 'Price'
    
    def get_stock(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.available_qty
        return '-'
    get_stock.short_description = 'Stock'


# Product Attribute Admin
@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """Admin for ProductAttribute model."""
    
    list_display = ['name', 'data_type', 'unit', 'is_filterable', 'sort_order']
    list_filter = ['data_type', 'is_filterable']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']


# Variant Inventory Admin
@admin.register(VariantInventory)
class VariantInventoryAdmin(admin.ModelAdmin):
    """Admin for VariantInventory model."""
    
    list_display = [
        'variant', 'stock_qty', 'reserved_qty', 
        'available_qty', 'is_low_stock', 'updated_at'
    ]
    list_filter = ['updated_at']
    search_fields = ['variant__sku', 'variant__product__name']
    raw_id_fields = ['variant']
    readonly_fields = ['available_qty', 'is_low_stock']
    
    def available_qty(self, obj):
        return obj.available_qty
    available_qty.short_description = 'Available'
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock?'


# Digital License Key Admin
@admin.register(DigitalLicenseKey)
class DigitalLicenseKeyAdmin(admin.ModelAdmin):
    """Admin for DigitalLicenseKey model."""
    
    list_display = ['product', 'variant', 'is_assigned', 'assigned_at', 'created_at']
    list_filter = ['is_assigned', 'product']
    search_fields = ['product__name', 'key']
    raw_id_fields = ['product', 'variant', 'assigned_order_item']
    readonly_fields = ['is_assigned', 'assigned_order_item', 'assigned_at']
