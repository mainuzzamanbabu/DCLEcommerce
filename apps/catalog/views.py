from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from .models import Category, Brand, Product, ProductVariant


class ProductListView(ListView):
    """List all products with filtering and pagination."""
    
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related(
            'images',
            Prefetch(
                'variants',
                queryset=ProductVariant.objects.filter(is_active=True).select_related('price', 'inventory')
            )
        )
        
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            # Include child categories
            category_ids = [category.id] + [c.id for c in category.get_all_children()]
            queryset = queryset.filter(category_id__in=category_ids)
        
        # Filter by brand
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Search query
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price or max_price:
            variant_filter = Q()
            if min_price:
                variant_filter &= Q(variants__price__list_price__gte=min_price)
            if max_price:
                variant_filter &= Q(variants__price__list_price__lte=max_price)
            queryset = queryset.filter(variant_filter).distinct()
        
        # Featured only
        if self.request.GET.get('featured'):
            queryset = queryset.filter(is_featured=True)
        
        # In stock only
        if self.request.GET.get('in_stock'):
            queryset = queryset.filter(
                variants__is_active=True,
                variants__inventory__stock_qty__gt=0
            ).distinct()
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = {
            'name': 'name',
            '-name': '-name',
            'price': 'variants__price__list_price',
            '-price': '-variants__price__list_price',
            '-created_at': '-created_at',
            'created_at': 'created_at',
        }
        if sort_by in valid_sorts:
            queryset = queryset.order_by(valid_sorts[sort_by])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Current category if filtered
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(
                Category, slug=category_slug, is_active=True
            )
        
        # All categories for sidebar
        context['categories'] = Category.objects.filter(
            is_active=True, parent__isnull=True
        ).prefetch_related('children')
        
        # All brands for filter
        context['brands'] = Brand.objects.filter(is_active=True)
        
        # Current filters for template
        context['current_filters'] = {
            'brand': self.request.GET.get('brand', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
            'q': self.request.GET.get('q', ''),
            'featured': self.request.GET.get('featured', ''),
            'in_stock': self.request.GET.get('in_stock', ''),
        }
        
        return context


class ProductDetailView(DetailView):
    """Product detail page."""
    
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related(
            'images',
            Prefetch(
                'variants',
                queryset=ProductVariant.objects.filter(is_active=True).select_related('price', 'inventory')
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Get variants with pricing
        context['variants'] = product.variants.filter(is_active=True).select_related(
            'price', 'inventory'
        )
        
        # Default variant
        context['default_variant'] = product.get_default_variant()
        
        # Related products (same category)
        if product.category:
            context['related_products'] = Product.objects.filter(
                is_active=True,
                category=product.category
            ).exclude(id=product.id).prefetch_related('images', 'variants')[:4]
        
        # Breadcrumbs
        breadcrumbs = []
        if product.category:
            for ancestor in product.category.get_ancestors():
                breadcrumbs.append({
                    'name': ancestor.name,
                    'url': ancestor.get_absolute_url()
                })
            breadcrumbs.append({
                'name': product.category.name,
                'url': product.category.get_absolute_url()
            })
        context['breadcrumbs'] = breadcrumbs
        
        return context


class CategoryListView(ListView):
    """List all categories."""
    
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(
            is_active=True, parent__isnull=True
        ).prefetch_related('children', 'products')


class CategoryDetailView(DetailView):
    """Category detail - shows products in category."""
    
    model = Category
    template_name = 'catalog/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        
        # Get products in this category and child categories
        category_ids = [category.id] + [c.id for c in category.get_all_children()]
        context['products'] = Product.objects.filter(
            is_active=True,
            category_id__in=category_ids
        ).prefetch_related('images', 'variants')[:12]
        
        # Child categories
        context['child_categories'] = category.children.filter(is_active=True)
        
        # Breadcrumbs
        context['breadcrumbs'] = [
            {'name': ancestor.name, 'url': ancestor.get_absolute_url()}
            for ancestor in category.get_ancestors()
        ]
        
        return context


class BrandListView(ListView):
    """List all brands."""
    
    model = Brand
    template_name = 'catalog/brand_list.html'
    context_object_name = 'brands'
    
    def get_queryset(self):
        return Brand.objects.filter(is_active=True).prefetch_related('products')


class BrandDetailView(DetailView):
    """Brand detail - shows brand info and products."""
    
    model = Brand
    template_name = 'catalog/brand_detail.html'
    context_object_name = 'brand'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Brand.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(
            is_active=True,
            brand=self.object
        ).prefetch_related('images', 'variants')[:12]
        return context


class SearchView(ProductListView):
    """Search results view."""
    
    template_name = 'catalog/search_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
