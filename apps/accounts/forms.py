from django import forms
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from .models import CustomerProfile, Address


class CustomSignupForm(SignupForm):
    """Custom signup form with additional fields."""
    
    full_name = forms.CharField(
        max_length=255,
        required=True,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autofocus': 'autofocus',
        })
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=True,
        label='Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
        })
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Conditions',
        error_messages={
            'required': 'You must accept the Terms and Conditions to create an account.'
        }
    )
    
    field_order = ['full_name', 'username', 'email', 'phone', 'password1', 'password2', 'terms_accepted']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Explicitly add username field since allauth may not include it with email auth
        self.fields['username'] = forms.CharField(
            max_length=150,
            required=True,
            label='Username',
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username',
            })
        )
        
        # Reorder fields to ensure our custom fields appear in the right order
        new_order = ['full_name', 'username', 'email', 'phone', 'password1', 'password2', 'terms_accepted']
        ordered_fields = {}
        for field_name in new_order:
            if field_name in self.fields:
                ordered_fields[field_name] = self.fields[field_name]
        # Add any remaining fields
        for field_name, field in self.fields.items():
            if field_name not in ordered_fields:
                ordered_fields[field_name] = field
        self.fields = ordered_fields
    
    def clean_username(self):
        from .models import User
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already taken. Please choose another.')
        return username
    
    def save(self, request):
        # Call parent save to create the user
        user = super().save(request)
        
        # Set additional fields on user
        user.username = self.cleaned_data.get('username')
        user.phone = self.cleaned_data.get('phone')
        user.save()
        
        # Create or update customer profile with full name
        profile, created = CustomerProfile.objects.get_or_create(user=user)
        profile.full_name = self.cleaned_data.get('full_name')
        profile.save()
        
        return user



class ProfileForm(forms.ModelForm):
    """Form for editing customer profile."""
    
    class Meta:
        model = CustomerProfile
        fields = ['full_name', 'avatar', 'marketing_opt_in']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'marketing_opt_in': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class AddressForm(forms.ModelForm):
    """Form for adding/editing addresses."""
    
    class Meta:
        model = Address
        fields = [
            'label', 'full_name', 'phone', 'country', 'city', 
            'area', 'address_line1', 'address_line2', 'postal_code',
            'is_default_shipping', 'is_default_billing'
        ]
        widgets = {
            'label': forms.Select(attrs={'class': 'form-select'}),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Area/District'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, etc. (optional)'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),
            'is_default_shipping': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_default_billing': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
