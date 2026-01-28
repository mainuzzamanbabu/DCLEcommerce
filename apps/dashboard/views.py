from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from apps.orders.models import Order, OrderStatusHistory
from apps.catalog.models import Category, Brand, Product, ProductImage
from apps.accounts.models import User
from django.utils import timezone
from datetime import timedelta
from .forms import CategoryForm, BrandForm, ProductForm, ProductImageForm


@staff_member_required
def dashboard_home(request):
    """Staff dashboard home - overview of store stats."""
    today = timezone.now().date()
    
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(Sum('total'))['total__sum'] or 0
    total_customers = User.objects.filter(is_staff=False).count()
    total_products = Product.objects.count()
    
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'title': 'Staff Dashboard Overview',
    }
    return render(request, 'dashboard/index.html', context)


# ==================== ORDER MANAGEMENT ====================

@staff_member_required
def order_list(request):
    """List all orders with filtering."""
    orders = Order.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    payment_status = request.GET.get('payment_status')
    if payment_status:
        orders = orders.filter(payment_status=payment_status)
    
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'title': 'Order Management',
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
        'current_status': status,
        'current_payment_status': payment_status,
    }
    return render(request, 'dashboard/orders/order_list.html', context)


@staff_member_required
def order_detail(request, order_number):
    """View and update a single order."""
    order = get_object_or_404(Order, order_number=order_number)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')
        
        if new_status and new_status != order.status:
            old_status = order.status
            order.status = new_status
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                note=note,
                created_by=request.user
            )
            
            messages.success(request, f'Order status updated from {old_status} to {new_status}.')
            return redirect('dashboard:order_detail', order_number=order_number)
    
    context = {
        'order': order,
        'title': f'Order #{order.order_number}',
        'status_choices': Order.ORDER_STATUS_CHOICES,
    }
    return render(request, 'dashboard/orders/order_detail.html', context)


# ==================== CATEGORY MANAGEMENT ====================

@staff_member_required
def category_list(request):
    """List all categories."""
    categories = Category.objects.all().order_by('sort_order', 'name')
    
    context = {
        'categories': categories,
        'title': 'Category Management',
    }
    return render(request, 'dashboard/categories/category_list.html', context)


@staff_member_required
def category_create(request):
    """Create a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add New Category',
    }
    return render(request, 'dashboard/categories/category_form.html', context)


@staff_member_required
def category_edit(request, pk):
    """Edit an existing category."""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f'Edit Category: {category.name}',
    }
    return render(request, 'dashboard/categories/category_form.html', context)


@staff_member_required
def category_delete(request, pk):
    """Delete a category."""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('dashboard:category_list')
    
    context = {
        'category': category,
        'title': f'Delete Category: {category.name}',
    }
    return render(request, 'dashboard/categories/category_confirm_delete.html', context)


# ==================== BRAND MANAGEMENT ====================

@staff_member_required
def brand_list(request):
    """List all brands."""
    brands = Brand.objects.all().order_by('name')
    
    context = {
        'brands': brands,
        'title': 'Brand Management',
    }
    return render(request, 'dashboard/brands/brand_list.html', context)


@staff_member_required
def brand_create(request):
    """Create a new brand."""
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            brand = form.save()
            messages.success(request, f'Brand "{brand.name}" created successfully!')
            return redirect('dashboard:brand_list')
    else:
        form = BrandForm()
    
    context = {
        'form': form,
        'title': 'Add New Brand',
    }
    return render(request, 'dashboard/brands/brand_form.html', context)


@staff_member_required
def brand_edit(request, pk):
    """Edit an existing brand."""
    brand = get_object_or_404(Brand, pk=pk)
    
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, f'Brand "{brand.name}" updated successfully!')
            return redirect('dashboard:brand_list')
    else:
        form = BrandForm(instance=brand)
    
    context = {
        'form': form,
        'brand': brand,
        'title': f'Edit Brand: {brand.name}',
    }
    return render(request, 'dashboard/brands/brand_form.html', context)


@staff_member_required
def brand_delete(request, pk):
    """Delete a brand."""
    brand = get_object_or_404(Brand, pk=pk)
    
    if request.method == 'POST':
        name = brand.name
        brand.delete()
        messages.success(request, f'Brand "{name}" deleted successfully!')
        return redirect('dashboard:brand_list')
    
    context = {
        'brand': brand,
        'title': f'Delete Brand: {brand.name}',
    }
    return render(request, 'dashboard/brands/brand_confirm_delete.html', context)


# ==================== PRODUCT MANAGEMENT ====================

@staff_member_required
def product_list(request):
    """List all products with filtering."""
    products = Product.objects.all().order_by('-created_at')
    
    is_active = request.GET.get('is_active')
    if is_active == '1':
        products = products.filter(is_active=True)
    elif is_active == '0':
        products = products.filter(is_active=False)
    
    is_featured = request.GET.get('is_featured')
    if is_featured == '1':
        products = products.filter(is_featured=True)
    
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'title': 'Product Management',
        'current_is_active': is_active,
        'current_is_featured': is_featured,
    }
    return render(request, 'dashboard/products/product_list.html', context)


@staff_member_required
def product_create(request):
    """Create a new product."""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('dashboard:product_edit', pk=product.pk)
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add New Product',
    }
    return render(request, 'dashboard/products/product_form.html', context)


@staff_member_required
def product_edit(request, pk):
    """Edit an existing product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    
    # Handle image uploads separately
    image_form = ProductImageForm()
    
    context = {
        'form': form,
        'image_form': image_form,
        'product': product,
        'title': f'Edit Product: {product.name}',
    }
    return render(request, 'dashboard/products/product_form.html', context)


@staff_member_required
def product_delete(request, pk):
    """Delete a product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully!')
        return redirect('dashboard:product_list')
    
    context = {
        'product': product,
        'title': f'Delete Product: {product.name}',
    }
    return render(request, 'dashboard/products/product_confirm_delete.html', context)


@staff_member_required
def product_image_upload(request, pk):
    """Upload an image to a product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.product = product
            image.save()
            messages.success(request, 'Image uploaded successfully!')
    
    return redirect('dashboard:product_edit', pk=pk)


@staff_member_required
def product_image_delete(request, pk, image_pk):
    """Delete a product image."""
    product = get_object_or_404(Product, pk=pk)
    image = get_object_or_404(ProductImage, pk=image_pk, product=product)
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully!')
    
    return redirect('dashboard:product_edit', pk=pk)


# ==================== VARIANT MANAGEMENT ====================
from apps.catalog.models import ProductVariant
from .forms import ProductVariantForm


@staff_member_required
def variant_create(request, pk):
    """Add a variant to a product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(product=product)
            messages.success(request, f'Variant "{variant.sku}" created successfully!')
            return redirect('dashboard:product_edit', pk=pk)
    else:
        # Generate a default SKU
        import uuid
        default_sku = f"{product.slug[:10].upper()}-{str(uuid.uuid4())[:4].upper()}"
        form = ProductVariantForm(initial={'sku': default_sku, 'stock_qty': 10, 'low_stock_threshold': 5})
    
    context = {
        'form': form,
        'product': product,
        'title': f'Add Variant to: {product.name}',
    }
    return render(request, 'dashboard/products/variant_form.html', context)


@staff_member_required
def variant_edit(request, pk, variant_pk):
    """Edit a product variant."""
    product = get_object_or_404(Product, pk=pk)
    variant = get_object_or_404(ProductVariant, pk=variant_pk, product=product)
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, instance=variant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Variant "{variant.sku}" updated successfully!')
            return redirect('dashboard:product_edit', pk=pk)
    else:
        form = ProductVariantForm(instance=variant)
    
    context = {
        'form': form,
        'product': product,
        'variant': variant,
        'title': f'Edit Variant: {variant.sku}',
    }
    return render(request, 'dashboard/products/variant_form.html', context)


@staff_member_required
def variant_delete(request, pk, variant_pk):
    """Delete a product variant."""
    product = get_object_or_404(Product, pk=pk)
    variant = get_object_or_404(ProductVariant, pk=variant_pk, product=product)
    
    if request.method == 'POST':
        sku = variant.sku
        variant.delete()
        messages.success(request, f'Variant "{sku}" deleted successfully!')
        return redirect('dashboard:product_edit', pk=pk)
    
    context = {
        'product': product,
        'variant': variant,
        'title': f'Delete Variant: {variant.sku}',
    }
    return render(request, 'dashboard/products/variant_confirm_delete.html', context)



@staff_member_required
def customer_list(request):
    """List all customers."""
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    paginator = Paginator(customers, 20)
    page = request.GET.get('page')
    customers = paginator.get_page(page)
    
    context = {
        'customers': customers,
        'title': 'Customer Management',
    }
    return render(request, 'dashboard/customers/customer_list.html', context)


# ==================== CMS MANAGEMENT ====================
from apps.cms.models import HeroSlide, PromotionalBanner
from .forms import HeroSlideForm, PromotionalBannerForm


# ----- Hero Slides -----

@staff_member_required
def slide_list(request):
    """List all hero slides."""
    slides = HeroSlide.objects.all().order_by('sort_order', '-created_at')
    context = {
        'slides': slides,
        'title': 'Hero Slides Management',
    }
    return render(request, 'dashboard/slides/slide_list.html', context)


@staff_member_required
def slide_create(request):
    """Create a new hero slide."""
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES)
        if form.is_valid():
            slide = form.save()
            messages.success(request, f'Slide "{slide.title}" created successfully!')
            return redirect('dashboard:slide_list')
    else:
        form = HeroSlideForm()
    
    context = {
        'form': form,
        'title': 'Add New Slide',
    }
    return render(request, 'dashboard/slides/slide_form.html', context)


@staff_member_required
def slide_edit(request, pk):
    """Edit a hero slide."""
    slide = get_object_or_404(HeroSlide, pk=pk)
    
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, f'Slide "{slide.title}" updated successfully!')
            return redirect('dashboard:slide_list')
    else:
        form = HeroSlideForm(instance=slide)
    
    context = {
        'form': form,
        'slide': slide,
        'title': f'Edit Slide: {slide.title}',
    }
    return render(request, 'dashboard/slides/slide_form.html', context)


@staff_member_required
def slide_delete(request, pk):
    """Delete a hero slide."""
    slide = get_object_or_404(HeroSlide, pk=pk)
    
    if request.method == 'POST':
        title = slide.title
        slide.delete()
        messages.success(request, f'Slide "{title}" deleted successfully!')
        return redirect('dashboard:slide_list')
    
    context = {
        'slide': slide,
        'title': f'Delete Slide: {slide.title}',
    }
    return render(request, 'dashboard/slides/slide_confirm_delete.html', context)


# ----- Promotional Banners -----

@staff_member_required
def banner_list(request):
    """List all promotional banners."""
    banners = PromotionalBanner.objects.all().order_by('sort_order', '-created_at')
    context = {
        'banners': banners,
        'title': 'Promotional Banners Management',
    }
    return render(request, 'dashboard/banners/banner_list.html', context)


@staff_member_required
def banner_create(request):
    """Create a new promotional banner."""
    if request.method == 'POST':
        form = PromotionalBannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save()
            messages.success(request, f'Banner "{banner.title}" created successfully!')
            return redirect('dashboard:banner_list')
    else:
        form = PromotionalBannerForm()
    
    context = {
        'form': form,
        'title': 'Add New Banner',
    }
    return render(request, 'dashboard/banners/banner_form.html', context)


@staff_member_required
def banner_edit(request, pk):
    """Edit a promotional banner."""
    banner = get_object_or_404(PromotionalBanner, pk=pk)
    
    if request.method == 'POST':
        form = PromotionalBannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, f'Banner "{banner.title}" updated successfully!')
            return redirect('dashboard:banner_list')
    else:
        form = PromotionalBannerForm(instance=banner)
    
    context = {
        'form': form,
        'banner': banner,
        'title': f'Edit Banner: {banner.title}',
    }
    return render(request, 'dashboard/banners/banner_form.html', context)


@staff_member_required
def banner_delete(request, pk):
    """Delete a promotional banner."""
    banner = get_object_or_404(PromotionalBanner, pk=pk)
    
    if request.method == 'POST':
        title = banner.title
        banner.delete()
        messages.success(request, f'Banner "{title}" deleted successfully!')
        return redirect('dashboard:banner_list')
    
    context = {
        'banner': banner,
        'title': f'Delete Banner: {banner.title}',
    }
    return render(request, 'dashboard/banners/banner_confirm_delete.html', context)

