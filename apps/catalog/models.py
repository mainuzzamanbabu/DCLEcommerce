from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    """Product category with hierarchical support."""
    
    name = models.CharField('name', max_length=200)
    slug = models.SlugField('slug', max_length=200, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='parent category'
    )
    description = models.TextField('description', blank=True)
    image = models.ImageField(
        'image',
        upload_to='categories/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField('active', default=True)
    
    # SEO fields
    seo_title = models.CharField('SEO title', max_length=200, blank=True)
    seo_description = models.TextField('SEO description', blank=True)
    
    # Ordering
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})
    
    def get_ancestors(self):
        """Get all ancestor categories."""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.insert(0, parent)
            parent = parent.parent
        return ancestors
    
    def get_all_children(self):
        """Get all descendant categories."""
        children = list(self.children.filter(is_active=True))
        for child in self.children.filter(is_active=True):
            children.extend(child.get_all_children())
        return children


class Brand(models.Model):
    """Product brand/manufacturer."""
    
    name = models.CharField('name', max_length=200)
    slug = models.SlugField('slug', max_length=200, unique=True)
    logo = models.ImageField(
        'logo',
        upload_to='brands/',
        blank=True,
        null=True
    )
    description = models.TextField('description', blank=True)
    website = models.URLField('website', blank=True)
    is_active = models.BooleanField('active', default=True)
    is_featured = models.BooleanField('featured', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:brand_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Main product model."""
    
    PRODUCT_TYPE_CHOICES = [
        ('physical', 'Physical'),
        ('digital', 'Digital'),
    ]
    
    name = models.CharField('name', max_length=300)
    slug = models.SlugField('slug', max_length=300, unique=True)
    product_type = models.CharField(
        'product type',
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='physical'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='category'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='brand'
    )
    
    short_description = models.TextField('short description', max_length=500, blank=True)
    description = models.TextField('description', blank=True)
    
    # Status flags
    is_active = models.BooleanField('active', default=True)
    is_featured = models.BooleanField('featured', default=False)
    
    # Additional info
    warranty_months = models.PositiveIntegerField('warranty (months)', default=0)
    
    # SEO
    seo_title = models.CharField('SEO title', max_length=200, blank=True)
    seo_description = models.TextField('SEO description', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})
    
    def get_primary_image(self):
        """Get the primary product image."""
        return self.images.filter(is_primary=True).first() or self.images.first()
    
    def get_default_variant(self):
        """Get the default (first active) variant."""
        return self.variants.filter(is_active=True).first()
    
    def get_price_range(self):
        """Get min and max prices across all variants."""
        variants = self.variants.filter(is_active=True)
        if not variants.exists():
            return None, None
        
        prices = []
        for variant in variants:
            if hasattr(variant, 'price'):
                effective = variant.price.sale_price or variant.price.list_price
                prices.append(effective)
        
        if not prices:
            return None, None
        return min(prices), max(prices)
    
    def is_in_stock(self):
        """Check if any variant is in stock."""
        for variant in self.variants.filter(is_active=True):
            if hasattr(variant, 'inventory') and variant.inventory.available_qty > 0:
                return True
        return False
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        if not hasattr(self, 'reviews'):
            return None
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return None
    
    @property
    def review_count(self):
        """Count approved reviews."""
        if not hasattr(self, 'reviews'):
            return 0
        return self.reviews.filter(is_approved=True).count()



class ProductImage(models.Model):
    """Product images."""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='product'
    )
    image = models.ImageField('image', upload_to='products/')
    alt_text = models.CharField('alt text', max_length=200, blank=True)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    is_primary = models.BooleanField('primary image', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'product image'
        verbose_name_plural = 'product images'
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    """Product attribute definitions (e.g., CPU, RAM, Storage)."""
    
    DATA_TYPE_CHOICES = [
        ('text', 'Text'),
        ('int', 'Integer'),
        ('decimal', 'Decimal'),
        ('bool', 'Boolean'),
        ('choice', 'Choice'),
    ]
    
    name = models.CharField('name', max_length=100)
    slug = models.SlugField('slug', max_length=100, unique=True)
    data_type = models.CharField(
        'data type',
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='text'
    )
    unit = models.CharField('unit', max_length=50, blank=True, help_text='e.g., GB, GHz, inches')
    is_filterable = models.BooleanField('show in filters', default=False)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    class Meta:
        verbose_name = 'product attribute'
        verbose_name_plural = 'product attributes'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """Product variant with specific attributes (e.g., 16GB RAM / 512GB SSD)."""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name='product'
    )
    
    sku = models.CharField('SKU', max_length=100, unique=True)
    variant_name = models.CharField(
        'variant name',
        max_length=200,
        blank=True,
        help_text='e.g., "16GB RAM / 512GB SSD"'
    )
    
    # Attributes stored as JSON for flexibility
    attributes = models.JSONField('attributes', default=dict, blank=True)
    
    barcode = models.CharField('barcode', max_length=100, blank=True)
    weight_kg = models.DecimalField(
        'weight (kg)',
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True
    )
    
    is_active = models.BooleanField('active', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'product variant'
        verbose_name_plural = 'product variants'
        ordering = ['product', 'variant_name']
        indexes = [
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        if self.variant_name:
            return f"{self.product.name} - {self.variant_name}"
        return f"{self.product.name} ({self.sku})"
    
    def get_display_name(self):
        """Get display name for cart/orders."""
        if self.variant_name:
            return f"{self.product.name} - {self.variant_name}"
        return self.product.name
    
    def get_image(self):
        """Get variant image or fall back to product primary image."""
        return self.product.get_primary_image()
    
    def get_effective_price(self):
        """Get the effective selling price."""
        if hasattr(self, 'price'):
            return self.price.sale_price or self.price.list_price
        return None
    
    def is_in_stock(self):
        """Check if variant is in stock."""
        if hasattr(self, 'inventory'):
            return self.inventory.available_qty > 0
        return False


class VariantInventory(models.Model):
    """Inventory tracking per variant."""
    
    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name='variant'
    )
    
    stock_qty = models.PositiveIntegerField('stock quantity', default=0)
    reserved_qty = models.PositiveIntegerField('reserved quantity', default=0)
    low_stock_threshold = models.PositiveIntegerField('low stock threshold', default=5)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'variant inventory'
        verbose_name_plural = 'variant inventories'
    
    def __str__(self):
        return f"Inventory for {self.variant}"
    
    @property
    def available_qty(self):
        """Calculate available quantity (stock - reserved)."""
        return max(0, self.stock_qty - self.reserved_qty)
    
    @property
    def is_low_stock(self):
        """Check if stock is below threshold."""
        return self.available_qty <= self.low_stock_threshold
    
    @property
    def is_out_of_stock(self):
        """Check if completely out of stock."""
        return self.available_qty == 0


class DigitalLicenseKey(models.Model):
    """License keys for digital products."""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='license_keys',
        verbose_name='product'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='license_keys',
        verbose_name='variant'
    )
    
    key = models.TextField('license key')
    is_assigned = models.BooleanField('assigned', default=False)
    assigned_order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',  # No reverse relation to avoid circular dependency
        verbose_name='assigned to order item'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField('assigned at', null=True, blank=True)
    
    class Meta:
        verbose_name = 'digital license key'
        verbose_name_plural = 'digital license keys'
    
    def __str__(self):
        status = "Assigned" if self.is_assigned else "Available"
        return f"Key for {self.product.name} ({status})"
