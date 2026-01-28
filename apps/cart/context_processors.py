from .cart import SessionCart


def cart(request):
    """Context processor to make the cart available in all templates."""
    return {'cart': SessionCart(request)}
