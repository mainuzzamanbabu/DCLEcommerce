from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Order


@login_required
def order_list(request):
    """List user's orders."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """View order details."""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Verify access
    if order.user != request.user and not request.user.is_staff:
        raise Http404("Order not found")
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)
