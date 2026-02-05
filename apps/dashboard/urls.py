from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Brands
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_create, name='brand_create'),
    path('brands/<int:pk>/edit/', views.brand_edit, name='brand_edit'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:pk>/images/upload/', views.product_image_upload, name='product_image_upload'),
    path('products/<int:pk>/images/<int:image_pk>/delete/', views.product_image_delete, name='product_image_delete'),
    
    # Product Variants
    path('products/<int:pk>/variants/add/', views.variant_create, name='variant_create'),
    path('products/<int:pk>/variants/<int:variant_pk>/edit/', views.variant_edit, name='variant_edit'),
    path('products/<int:pk>/variants/<int:variant_pk>/delete/', views.variant_delete, name='variant_delete'),

    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    
    # CMS - Hero Slides
    path('slides/', views.slide_list, name='slide_list'),
    path('slides/add/', views.slide_create, name='slide_create'),
    path('slides/<int:pk>/edit/', views.slide_edit, name='slide_edit'),
    path('slides/<int:pk>/delete/', views.slide_delete, name='slide_delete'),
    
    # CMS - Promotional Banners
    path('banners/', views.banner_list, name='banner_list'),
    path('banners/add/', views.banner_create, name='banner_create'),
    path('banners/<int:pk>/edit/', views.banner_edit, name='banner_edit'),
    path('banners/<int:pk>/delete/', views.banner_delete, name='banner_delete'),
    
    # Shipping Methods
    path('shipping-methods/', views.shipping_method_list, name='shipping_method_list'),
    path('shipping-methods/add/', views.shipping_method_create, name='shipping_method_create'),
    path('shipping-methods/<int:pk>/edit/', views.shipping_method_edit, name='shipping_method_edit'),
    path('shipping-methods/<int:pk>/delete/', views.shipping_method_delete, name='shipping_method_delete'),
    
    # Payment Methods
    path('payments/', views.payment_list, name='payment_list'),
    path('payment-methods/', views.payment_method_list, name='payment_method_list'),
    path('payment-methods/add/', views.payment_method_create, name='payment_method_create'),
    path('payment-methods/<int:pk>/edit/', views.payment_method_edit, name='payment_method_edit'),
    path('payment-methods/<int:pk>/delete/', views.payment_method_delete, name='payment_method_delete'),
    
    # Customer Detail
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    
    # CMS - Site Settings
    path('settings/', views.site_settings, name='site_settings'),
    
    # CMS - Testimonials
    path('testimonials/', views.testimonial_list, name='testimonial_list'),
    path('testimonials/add/', views.testimonial_create, name='testimonial_create'),
    path('testimonials/<int:pk>/edit/', views.testimonial_edit, name='testimonial_edit'),
    path('testimonials/<int:pk>/delete/', views.testimonial_delete, name='testimonial_delete'),
    
    # CMS - FAQs
    path('faqs/', views.faq_list, name='faq_list'),
    path('faqs/add/', views.faq_create, name='faq_create'),
    path('faqs/<int:pk>/edit/', views.faq_edit, name='faq_edit'),
    path('faqs/<int:pk>/delete/', views.faq_delete, name='faq_delete'),
]
