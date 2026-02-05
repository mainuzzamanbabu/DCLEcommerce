from django.shortcuts import render, redirect
from apps.catalog.models import Product, Category, Brand
from apps.cms.models import HeroSlide, PromotionalBanner


def home(request):
    """Homepage view with dynamic content."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')
    
    # Get featured products (limit to 8)
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).prefetch_related('images', 'variants__price').order_by('-created_at')[:8]
    
    # Get active categories
    categories = Category.objects.filter(
        is_active=True
    ).order_by('sort_order', 'name')[:6]

    
    # Get active brands (for brand logos section)
    brands = Brand.objects.filter(is_active=True).order_by('name')[:6]
    
    # Get hero slides
    slides = HeroSlide.objects.filter(is_active=True).order_by('sort_order')
    
    # Get promotional banners
    banners = PromotionalBanner.objects.filter(is_active=True).order_by('sort_order')[:2]
    
    # Get some deal products (products with sale prices - placeholder for now, just get active products)
    deal_products = Product.objects.filter(
        is_active=True
    ).prefetch_related('images', 'variants__price').order_by('?')[:4]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'brands': brands,
        'slides': slides,
        'banners': banners,
        'deal_products': deal_products,
    }
    
    return render(request, 'pages/home.html', context)


def terms(request):
    """Terms and conditions page."""
    return render(request, 'core/terms.html')
