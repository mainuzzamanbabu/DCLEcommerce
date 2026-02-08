from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Product, Category, ProductVariant, Brand
from decimal import Decimal
import json

class CartAjaxTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Test Category", slug="test-cat")
        self.product = Product.objects.create(
            name="Test Product", 
            slug="test-prod", 
            category=self.category,
            is_active=True
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TEST-SKU",
            is_active=True
        )
        # Assuming price is a related model or handled via signals/defaults
        # For this test, let's assume the variant needs a price object if the model expects it
        from apps.pricing.models import ProductPrice
        ProductPrice.objects.create(
            variant=self.variant,
            list_price=Decimal('100.00')
        )

    def test_cart_add_ajax(self):
        url = reverse('cart:cart_add')
        response = self.client.post(url, {
            'variant_id': self.variant.id,
            'quantity': 1
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['cart_count'], 1)
        
    def test_cart_add_invalid_variant(self):
        url = reverse('cart:cart_add')
        response = self.client.post(url, {
            'variant_id': 9999,
            'quantity': 1
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 404)
