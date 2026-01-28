from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the unique identifier."""
    
    email = models.EmailField('email address', unique=True)
    username = models.CharField('username', max_length=150, blank=True, null=True)
    phone = models.CharField('phone number', max_length=20, blank=True, null=True)
    
    is_verified_email = models.BooleanField('email verified', default=False)
    is_verified_phone = models.BooleanField('phone verified', default=False)
    
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active.',
    )
    
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name from profile or email."""
        if hasattr(self, 'profile') and self.profile.full_name:
            return self.profile.full_name
        return self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.email.split('@')[0]


class CustomerProfile(models.Model):
    """Extended profile for customers."""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    full_name = models.CharField('full name', max_length=255, blank=True)
    avatar = models.ImageField(
        'avatar', 
        upload_to='avatars/', 
        blank=True, 
        null=True
    )
    marketing_opt_in = models.BooleanField(
        'marketing emails',
        default=False,
        help_text='User has opted in to receive marketing emails.'
    )
    default_shipping_address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_shipping_for'
    )
    default_billing_address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_billing_for'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'customer profile'
        verbose_name_plural = 'customer profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"


class Address(models.Model):
    """Customer addresses for shipping and billing."""
    
    LABEL_CHOICES = [
        ('home', 'Home'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses'
    )
    label = models.CharField(
        'label', 
        max_length=20, 
        choices=LABEL_CHOICES, 
        default='home'
    )
    full_name = models.CharField('full name', max_length=255)
    phone = models.CharField('phone number', max_length=20)
    
    country = models.CharField('country', max_length=100, default='Bangladesh')
    city = models.CharField('city', max_length=100)
    area = models.CharField('area', max_length=255, blank=True)
    address_line1 = models.CharField('address line 1', max_length=255)
    address_line2 = models.CharField('address line 2', max_length=255, blank=True)
    postal_code = models.CharField('postal code', max_length=20, blank=True)
    
    is_default_shipping = models.BooleanField('default shipping', default=False)
    is_default_billing = models.BooleanField('default billing', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'address'
        verbose_name_plural = 'addresses'
        ordering = ['-is_default_shipping', '-created_at']
    
    def __str__(self):
        return f"{self.label.title()} - {self.address_line1}, {self.city}"
    
    def save(self, *args, **kwargs):
        """Ensure only one default shipping/billing address per user."""
        if self.is_default_shipping:
            Address.objects.filter(
                user=self.user, 
                is_default_shipping=True
            ).exclude(pk=self.pk).update(is_default_shipping=False)
        
        if self.is_default_billing:
            Address.objects.filter(
                user=self.user, 
                is_default_billing=True
            ).exclude(pk=self.pk).update(is_default_billing=False)
        
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        """Return formatted full address."""
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        if self.area:
            parts.append(self.area)
        parts.append(self.city)
        if self.postal_code:
            parts.append(self.postal_code)
        parts.append(self.country)
        return ', '.join(parts)
