from django import forms
from .models import CustomerProfile, Address


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
