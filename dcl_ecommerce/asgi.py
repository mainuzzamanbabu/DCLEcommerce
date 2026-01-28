"""
ASGI config for DCL Ecommerce project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcl_ecommerce.settings')

application = get_asgi_application()
