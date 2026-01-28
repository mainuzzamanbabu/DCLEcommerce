"""
Context processors for core app.
"""


def site_settings(request):
    """
    Add site settings to template context.
    This will be enhanced when CMS app is implemented.
    """
    return {
        'site_name': 'DCL Ecommerce',
        'site_tagline': 'Your Trusted IT Partner',
        'primary_color': '#003366',
        'secondary_color': '#FF6600',
    }
