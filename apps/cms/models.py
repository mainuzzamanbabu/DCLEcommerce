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
