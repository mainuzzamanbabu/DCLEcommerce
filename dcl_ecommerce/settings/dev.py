"""
Development settings for DCL Ecommerce project.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# Try to add debug toolbar if installed
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
except ImportError:
    pass

# Internal IPs for debug toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable WhiteNoise in development for easier static file debugging
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

