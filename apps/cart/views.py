import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.catalog.models import ProductVariant
from .cart import SessionCart


@require_POST
def cart_add(request):
    """Add a product variant to the cart via AJAX."""
    cart = SessionCart(request)
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    # Check inventory
    if hasattr(variant, 'inventory') and variant.inventory.available_qty < quantity:
        return JsonResponse({
            'status': 'error',
            'message': f'Only {variant.inventory.available_qty} items available in stock.'
        }, status=400)
    
    cart.add(variant=variant, quantity=quantity)
    
    return JsonResponse({
        'status': 'success',
        'message': f'Added {variant.product.name} to cart.',
        'cart_count': len(cart),
        'cart_total': float(cart.get_total_price())
    })


@require_POST
def cart_remove(request):
    """Remove an item from the cart via AJAX."""
    cart = SessionCart(request)
    variant_id = request.POST.get('variant_id')
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    cart.remove(variant)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Item removed from cart.',
        'cart_count': len(cart),
        'cart_total': float(cart.get_total_price())
    })


@require_POST
def cart_update(request):
    """Update item quantity in the cart via AJAX."""
    cart = SessionCart(request)
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity'))
    
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    # Check inventory
    if hasattr(variant, 'inventory') and variant.inventory.available_qty < quantity:
        return JsonResponse({
            'status': 'error',
            'message': f'Only {variant.inventory.available_qty} items available in stock.'
        }, status=400)
    
    cart.add(variant=variant, quantity=quantity, override_quantity=True)
    
    # Calculate item total for front-end update
    unit_price = variant.price.effective_price if hasattr(variant, 'price') else 0
    item_total = float(unit_price * quantity)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Cart updated.',
        'cart_count': len(cart),
        'cart_total': float(cart.get_total_price()),
        'item_total': item_total
    })


def cart_detail(request):
    """Display the cart summary page."""
    cart = SessionCart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})
