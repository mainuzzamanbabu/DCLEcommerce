from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .cart import SessionCart


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    """Signal receiver to merge session cart into database cart when user logs in."""
    cart = SessionCart(request)
    cart.merge_with_user_cart()
