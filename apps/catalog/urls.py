from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Product listing and search
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Category views
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('c/<slug:category_slug>/', views.ProductListView.as_view(), name='category_products'),
    
    # Brand views
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('brand/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    
    # Product detail (last to avoid conflicts)
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/quickview/', views.ProductQuickView.as_view(), name='product_quickview'),
]
