"""
URL configuration for DCL Ecommerce project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Main app URLs
    path('', include('apps.core.urls')),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('apps.accounts.urls')),
    path('catalog/', include('apps.catalog.urls')),
    path('cart/', include('apps.cart.urls')),
    path('checkout/', include('apps.checkout.urls')),
    path('orders/', include('apps.orders.urls')),
    path('payments/', include('apps.payments.urls')),
    path('wishlist/', include('apps.wishlist.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('support/', include('apps.support.urls')),
    path('manage/', include('apps.dashboard.urls')),
    path('pages/', include('apps.cms.urls')),
]

# Debug toolbar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
