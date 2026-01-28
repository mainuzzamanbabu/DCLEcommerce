import requests
import logging
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)

class SSLCommerzProvider:
    def __init__(self):
        self.store_id = getattr(settings, 'SSLCOMMERZ_STORE_ID', '')
        self.store_pass = getattr(settings, 'SSLCOMMERZ_STORE_PASS', '')
        self.sandbox = getattr(settings, 'SSLCOMMERZ_SANDBOX', True)
        
        if self.sandbox:
            self.base_url = "https://sandbox.sslcommerz.com"
        else:
            self.base_url = "https://securepay.sslcommerz.com"
            
    def init_payment(self, order, transaction_id, request):
        """
        Initialize payment session and return GatewayPageURL.
        """
        url = f"{self.base_url}/gwprocess/v4/api.php"
        
        # Build success/fail/cancel URLs
        base_url = f"{request.scheme}://{request.get_host()}"
        
        post_data = {
            'store_id': self.store_id,
            'store_passwd': self.store_pass,
            'total_amount': str(order.total),
            'currency': 'BDT',
            'tran_id': str(transaction_id),
            'success_url': f"{base_url}{reverse('payments:sslcommerz_success')}",
            'fail_url': f"{base_url}{reverse('payments:sslcommerz_fail')}",
            'cancel_url': f"{base_url}{reverse('payments:sslcommerz_cancel')}",
            'ipn_url': f"{base_url}{reverse('payments:sslcommerz_ipn')}",
            
            # Customer Info
            'cus_name': order.shipping_address.get('full_name', 'Guest'),
            'cus_email': order.get_email() or 'guest@example.com',
            'cus_add1': order.shipping_address.get('address_line1', 'N/A'),
            'cus_city': order.shipping_address.get('city', 'Dhaka'),
            'cus_postcode': order.shipping_address.get('postal_code', '1000'),
            'cus_country': order.shipping_address.get('country', 'Bangladesh'),
            'cus_phone': order.guest_phone or order.shipping_address.get('phone', '01700000000'),
            
            # Shipping Info
            'shipping_method': order.shipping_method_name or 'Courier',
            'num_of_item': order.items.count(),
            'product_name': f"Order {order.order_number}",
            'product_category': 'Electronic',
            'product_profile': 'general',
        }
        
        try:
            response = requests.post(url, data=post_data)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'SUCCESS':
                return data.get('GatewayPageURL')
            else:
                logger.error(f"SSLCommerz Init Error: {data.get('failedreason')}")
                return None
        except Exception as e:
            logger.exception("SSLCommerz Request Exception")
            return None

    def validate_transaction(self, val_id):
        """
        Validate a transaction using val_id.
        """
        url = f"{self.base_url}/validator/api/validationserverAPI.php"
        params = {
            'val_id': val_id,
            'store_id': self.store_id,
            'store_passwd': self.store_pass,
            'format': 'json',
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception("SSLCommerz Validation Exception")
            return None
