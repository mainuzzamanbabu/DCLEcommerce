from django.db import models


class HeroSlide(models.Model):
    """Hero slider slides for the homepage."""
    
    title = models.CharField('title', max_length=200)
    subtitle = models.TextField('subtitle', max_length=500, blank=True)
    button_text = models.CharField('button text', max_length=50, blank=True)
    button_link = models.CharField('button link', max_length=200, blank=True)
    button_style = models.CharField(
        'button style',
        max_length=20,
        choices=[
            ('primary', 'Primary (Dark Blue)'),
            ('secondary', 'Secondary (Orange)'),
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('outline-light', 'Outline Light'),
        ],
        default='secondary'
    )
    
    # Background styling
    background_color = models.CharField(
        'background color/gradient',
        max_length=200,
        default='linear-gradient(135deg, #003366 0%, #0054A6 100%)',
        help_text='CSS color or gradient value'
    )
    background_image = models.ImageField(
        'background image',
        upload_to='slides/',
        blank=True,
        null=True
    )
    
    # Icon (Bootstrap Icon class name)
    icon_class = models.CharField(
        'icon class',
        max_length=50,
        blank=True,
        help_text='Bootstrap icon class (e.g., bi-laptop)'
    )
    
    # Badge
    badge_text = models.CharField('badge text', max_length=50, blank=True)
    badge_style = models.CharField(
        'badge style',
        max_length=20,
        choices=[
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('success', 'Success'),
            ('danger', 'Danger'),
            ('warning', 'Warning'),
            ('info', 'Info'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ],
        default='secondary',
        blank=True
    )
    
    is_active = models.BooleanField('active', default=True)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'hero slide'
        verbose_name_plural = 'hero slides'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.title


class PromotionalBanner(models.Model):
    """Promotional banners for the homepage."""
    
    POSITION_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
        ('full', 'Full Width'),
    ]
    
    title = models.CharField('title', max_length=200)
    description = models.TextField('description', max_length=500, blank=True)
    button_text = models.CharField('button text', max_length=50, blank=True)
    button_link = models.CharField('button link', max_length=200, blank=True)
    button_style = models.CharField(
        'button style',
        max_length=20,
        choices=[
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ],
        default='light'
    )
    
    # Badge
    badge_text = models.CharField('badge text', max_length=50, blank=True)
    badge_style = models.CharField(
        'badge style',
        max_length=20,
        choices=[
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('success', 'Success'),
            ('danger', 'Danger'),
            ('warning', 'Warning'),
            ('info', 'Info'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ],
        default='secondary'
    )
    
    # Background styling
    background_style = models.CharField(
        'background style',
        max_length=200,
        default='linear-gradient(135deg, #003366 0%, #0054A6 100%)',
        help_text='CSS color or gradient value'
    )
    background_image = models.ImageField(
        'background image',
        upload_to='banners/',
        blank=True,
        null=True
    )
    
    position = models.CharField(
        'position',
        max_length=10,
        choices=POSITION_CHOICES,
        default='left'
    )
    
    is_active = models.BooleanField('active', default=True)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'promotional banner'
        verbose_name_plural = 'promotional banners'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """Singleton model for global site settings."""
    
    site_name = models.CharField('site name', max_length=100, default='DCL Ecommerce')
    tagline = models.CharField('tagline', max_length=200, blank=True)
    logo = models.ImageField('logo', upload_to='site/', blank=True, null=True)
    favicon = models.ImageField('favicon', upload_to='site/', blank=True, null=True)
    
    # SEO
    seo_title = models.CharField('SEO title', max_length=60, blank=True)
    seo_description = models.TextField('SEO description', max_length=160, blank=True)
    seo_keywords = models.CharField('SEO keywords', max_length=255, blank=True)
    
    # Contact Info
    email = models.EmailField('email', blank=True)
    phone = models.CharField('phone', max_length=20, blank=True)
    address = models.TextField('address', blank=True)
    
    # Social Links
    facebook_url = models.URLField('Facebook URL', blank=True)
    instagram_url = models.URLField('Instagram URL', blank=True)
    twitter_url = models.URLField('Twitter/X URL', blank=True)
    youtube_url = models.URLField('YouTube URL', blank=True)
    linkedin_url = models.URLField('LinkedIn URL', blank=True)
    
    # Footer
    footer_text = models.TextField('footer text', blank=True, help_text='Copyright text for footer')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'site settings'
        verbose_name_plural = 'site settings'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class FooterSection(models.Model):
    """Dynamic footer sections with links."""
    
    title = models.CharField('title', max_length=100)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    is_active = models.BooleanField('active', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'footer section'
        verbose_name_plural = 'footer sections'
        ordering = ['sort_order']
    
    def __str__(self):
        return self.title


class FooterLink(models.Model):
    """Links within a footer section."""
    
    section = models.ForeignKey(FooterSection, on_delete=models.CASCADE, related_name='links')
    title = models.CharField('title', max_length=100)
    url = models.CharField('URL', max_length=255)
    open_in_new_tab = models.BooleanField('open in new tab', default=False)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    is_active = models.BooleanField('active', default=True)
    
    class Meta:
        ordering = ['sort_order']
    
    def __str__(self):
        return self.title


class FeaturedSection(models.Model):
    """Featured content blocks for homepage."""
    
    SECTION_TYPES = [
        ('products', 'Featured Products'),
        ('categories', 'Featured Categories'),
        ('brands', 'Featured Brands'),
        ('custom', 'Custom Content'),
    ]
    
    title = models.CharField('title', max_length=200)
    subtitle = models.TextField('subtitle', max_length=500, blank=True)
    section_type = models.CharField('section type', max_length=20, choices=SECTION_TYPES, default='products')
    
    # Background styling
    background_color = models.CharField('background color', max_length=100, blank=True, default='#ffffff')
    text_color = models.CharField('text color', max_length=20, default='dark', choices=[('dark', 'Dark'), ('light', 'Light')])
    
    is_active = models.BooleanField('active', default=True)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'featured section'
        verbose_name_plural = 'featured sections'
        ordering = ['sort_order']
    
    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Customer testimonials."""
    
    customer_name = models.CharField('customer name', max_length=100)
    customer_title = models.CharField('title/location', max_length=100, blank=True)
    customer_image = models.ImageField('customer image', upload_to='testimonials/', blank=True, null=True)
    
    content = models.TextField('testimonial content')
    rating = models.PositiveIntegerField('rating', default=5, choices=[(i, f'{i} Stars') for i in range(1, 6)])
    
    is_active = models.BooleanField('active', default=True)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'testimonial'
        verbose_name_plural = 'testimonials'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"


class FAQItem(models.Model):
    """FAQ entries."""
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('shipping', 'Shipping & Delivery'),
        ('payment', 'Payment'),
        ('returns', 'Returns & Refunds'),
        ('account', 'Account'),
    ]
    
    question = models.CharField('question', max_length=500)
    answer = models.TextField('answer')
    category = models.CharField('category', max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    is_active = models.BooleanField('active', default=True)
    sort_order = models.PositiveIntegerField('sort order', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'FAQ item'
        verbose_name_plural = 'FAQ items'
        ordering = ['category', 'sort_order']
    
    def __str__(self):
        return self.question[:50]
