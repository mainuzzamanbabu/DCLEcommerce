from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomerProfile, Address


class CustomerProfileInline(admin.StackedInline):
    """Inline admin for CustomerProfile."""
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class AddressInline(admin.TabularInline):
    """Inline admin for addresses."""
    model = Address
    extra = 0
    fields = ['label', 'full_name', 'phone', 'city', 'address_line1', 'is_default_shipping', 'is_default_billing']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    list_display = ['email', 'get_full_name', 'phone', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'is_verified_email', 'date_joined']
    search_fields = ['email', 'profile__full_name', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'phone')}),
        ('Verification', {'fields': ('is_verified_email', 'is_verified_phone')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    inlines = [CustomerProfileInline, AddressInline]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin for Address model."""
    
    list_display = ['user', 'label', 'full_name', 'city', 'is_default_shipping', 'is_default_billing']
    list_filter = ['label', 'city', 'is_default_shipping', 'is_default_billing']
    search_fields = ['user__email', 'full_name', 'address_line1', 'city']
    raw_id_fields = ['user']
