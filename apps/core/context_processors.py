"""
Context processors for core app.
"""
from apps.catalog.models import Category


def site_settings(request):
    """
    Add site settings from CMS to template context.
    Makes SiteSettings globally available in all templates.
    """
    from apps.cms.models import SiteSettings
    
    # Get main categories (no parent) for navigation
    main_categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).order_by('sort_order', 'name')[:6]
    
    # Get CMS site settings (singleton)
    try:
        cms_settings = SiteSettings.objects.first()
    except Exception:
        cms_settings = None
    
    # Build context with CMS data or fallback defaults
    context = {
        'nav_categories': main_categories,
        'cms': cms_settings,  # Full settings object for template access
    }
    
    # Add convenience variables (fallback to defaults if no CMS settings)
    if cms_settings:
        context.update({
            'site_name': cms_settings.site_name or 'DCL Ecommerce',
            'site_tagline': cms_settings.tagline or 'Your Trusted IT Partner',
            'site_email': cms_settings.email,
            'site_phone': cms_settings.phone,
            'site_address': cms_settings.address,
            'site_logo': cms_settings.logo,
            'site_favicon': cms_settings.favicon,
            'seo_title': cms_settings.seo_title,
            'seo_description': cms_settings.seo_description,
            'seo_keywords': cms_settings.seo_keywords,
            'facebook_url': cms_settings.facebook_url,
            'instagram_url': cms_settings.instagram_url,
            'twitter_url': cms_settings.twitter_url,
            'youtube_url': cms_settings.youtube_url,
            'linkedin_url': cms_settings.linkedin_url,
            'footer_text': cms_settings.footer_text,
        })
    else:
        # Fallback defaults when no CMS settings exist
        context.update({
            'site_name': 'DCL Ecommerce',
            'site_tagline': 'Your Trusted IT Partner',
            'site_email': '',
            'site_phone': '',
            'site_address': '',
            'site_logo': None,
            'site_favicon': None,
            'seo_title': '',
            'seo_description': '',
            'seo_keywords': '',
            'facebook_url': '',
            'instagram_url': '',
            'twitter_url': '',
            'youtube_url': '',
            'linkedin_url': '',
            'footer_text': '',
        })
    
    return context
