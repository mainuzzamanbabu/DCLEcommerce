from .models import Category

def catalog_context(request):
    """
    Context processor to provide common catalog data to all templates.
    """
    return {
        'nav_categories': Category.objects.filter(parent=None, is_active=True).prefetch_related('children'),
        'all_categories': Category.objects.filter(is_active=True),
    }
