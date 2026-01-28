"""
Production settings for DCL Ecommerce project.
"""

import dj_database_url
from .base import *  # noqa: F401, F403

DEBUG = False

# Database - PostgreSQL for production
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://user:password@localhost:5432/dcl_ecommerce',
        conn_max_age=600,
    )
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS in production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
