from django import forms
from apps.catalog.models import Category, Brand, Product, ProductImage


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'parent', 'description', 'image', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category description...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class BrandForm(forms.ModelForm):
    """Form for creating/editing brands."""
    
    class Meta:
        model = Brand
        fields = ['name', 'logo', 'description', 'website', 'is_active', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand Name'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brand description...'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductForm(forms.ModelForm):
    """Form for creating/editing products."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand', 'product_type', 
            'short_description', 'description',
            'is_active', 'is_featured', 'warranty_months'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'product_type': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Short description for product cards...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Full product description...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'warranty_months': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class ProductImageForm(forms.ModelForm):
    """Form for uploading product images."""
    
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image description for accessibility'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Variant and Pricing Forms
from apps.catalog.models import ProductVariant, VariantInventory
from apps.pricing.models import Price


class ProductVariantForm(forms.ModelForm):
    """Form for creating/editing product variants with price and inventory."""
    
    # Price fields (inline)
    list_price = forms.DecimalField(
        label='List Price (MRP)',
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'placeholder': '0.00'})
    )
    sale_price = forms.DecimalField(
        label='Sale Price (Optional)',
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'placeholder': 'Leave blank if not on sale'})
    )
    cost_price = forms.DecimalField(
        label='Cost Price (Internal)',
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'placeholder': 'Your purchase price'})
    )
    
    # Inventory fields (inline)
    stock_qty = forms.IntegerField(
        label='Stock Quantity',
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0})
    )
    low_stock_threshold = forms.IntegerField(
        label='Low Stock Alert Threshold',
        min_value=0,
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0})
    )
    
    class Meta:
        model = ProductVariant
        fields = ['sku', 'variant_name', 'barcode', 'weight_kg', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., LAPTOP-001-16GB'}),
            'variant_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 16GB RAM / 512GB SSD'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Barcode (optional)'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': 0, 'placeholder': 'Weight in kg'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        
        # Pre-populate price fields if editing
        if instance and hasattr(instance, 'price'):
            initial['list_price'] = instance.price.list_price
            initial['sale_price'] = instance.price.sale_price
            initial['cost_price'] = instance.price.cost_price
        
        # Pre-populate inventory fields if editing
        if instance and hasattr(instance, 'inventory'):
            initial['stock_qty'] = instance.inventory.stock_qty
            initial['low_stock_threshold'] = instance.inventory.low_stock_threshold
        
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True, product=None):
        variant = super().save(commit=False)
        
        if product:
            variant.product = product
        
        if commit:
            variant.save()
            
            # Save or update price
            price_data = {
                'list_price': self.cleaned_data['list_price'],
                'sale_price': self.cleaned_data.get('sale_price'),
                'cost_price': self.cleaned_data.get('cost_price'),
            }
            
            if hasattr(variant, 'price'):
                for key, value in price_data.items():
                    setattr(variant.price, key, value)
                variant.price.save()
            else:
                Price.objects.create(variant=variant, **price_data)
            
            # Save or update inventory
            inventory_data = {
                'stock_qty': self.cleaned_data['stock_qty'],
                'low_stock_threshold': self.cleaned_data['low_stock_threshold'],
            }
            
            if hasattr(variant, 'inventory'):
                for key, value in inventory_data.items():
                    setattr(variant.inventory, key, value)
                variant.inventory.save()
            else:
                VariantInventory.objects.create(variant=variant, **inventory_data)
        
        return variant



# CMS Forms
from apps.cms.models import HeroSlide, PromotionalBanner


class HeroSlideForm(forms.ModelForm):
    """Form for creating/editing hero slides."""
    
    class Meta:
        model = HeroSlide
        fields = [
            'title', 'subtitle', 'button_text', 'button_link', 'button_style',
            'background_color', 'background_image', 'icon_class',
            'badge_text', 'badge_style', 'is_active', 'sort_order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Slide Title'}),
            'subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Slide subtitle/description...'}),
            'button_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Shop Now'}),
            'button_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/catalog/'}),
            'button_style': forms.Select(attrs={'class': 'form-select'}),
            'background_color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'linear-gradient(135deg, #003366 0%, #0054A6 100%)'}),
            'background_image': forms.FileInput(attrs={'class': 'form-control'}),
            'icon_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-laptop'}),
            'badge_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., HOT DEAL'}),
            'badge_style': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class PromotionalBannerForm(forms.ModelForm):
    """Form for creating/editing promotional banners."""
    
    class Meta:
        model = PromotionalBanner
        fields = [
            'title', 'description', 'button_text', 'button_link', 'button_style',
            'badge_text', 'badge_style', 'background_style', 'background_image',
            'position', 'is_active', 'sort_order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Banner Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Banner description...'}),
            'button_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Shop Now'}),
            'button_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/catalog/'}),
            'button_style': forms.Select(attrs={'class': 'form-select'}),
            'badge_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Limited Offer'}),
            'badge_style': forms.Select(attrs={'class': 'form-select'}),
            'background_style': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'linear-gradient(135deg, #003366 0%, #0054A6 100%)'}),
            'background_image': forms.FileInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

