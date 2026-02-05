from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from decimal import Decimal
import uuid

from apps.cart.cart import SessionCart
from apps.accounts.models import Address
from apps.orders.models import Order, OrderItem
from apps.payments.models import PaymentTransaction
from apps.payments.utils import SSLCommerzProvider
from .models import ShippingMethod, CheckoutSession


def get_or_create_checkout_session(request):
    """Get or create a checkout session for the current user/guest."""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    if request.user.is_authenticated:
        session, created = CheckoutSession.objects.get_or_create(
            user=request.user,
            defaults={'session_key': session_key}
        )
    else:
        session, created = CheckoutSession.objects.get_or_create(
            session_key=session_key,
            user=None
        )
    
    return session


def checkout(request):
    """Main checkout view - redirects to first incomplete step."""
    if not request.user.is_authenticated:
        messages.info(request, 'Please login or create an account to complete your purchase.')
        return redirect(f'/accounts/login/?next=/checkout/')
    
    cart = SessionCart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    session = get_or_create_checkout_session(request)
    
    # Determine next step
    if not session.shipping_address and not session.guest_shipping_address:
        return redirect('checkout:address')
    elif not session.shipping_method:
        return redirect('checkout:shipping')
    elif not session.payment_method:
        return redirect('checkout:payment')
    else:
        return redirect('checkout:review')


@login_required
def checkout_address(request):

    """Step 1: Address selection/entry."""
    cart = SessionCart(request)
    
    if len(cart) == 0:
        return redirect('cart:cart_detail')
    
    session = get_or_create_checkout_session(request)
    
    if request.method == 'POST':
        # 1. Try to get a saved address (only for authenticated users)
        address_id = request.POST.get('shipping_address')
        if request.user.is_authenticated and address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
            session.shipping_address = address
            
            # Handle billing address
            same_as_shipping = request.POST.get('same_as_shipping') == 'on'
            session.same_as_shipping = same_as_shipping
            if same_as_shipping:
                session.billing_address = address
            else:
                billing_id = request.POST.get('billing_address')
                if billing_id:
                    session.billing_address = get_object_or_404(Address, id=billing_id, user=request.user)
            
            session.guest_shipping_address = {} # Clear guest info if saved address used
            session.current_step = 'shipping'
            session.save()
            return redirect('checkout:shipping')
            
        # 2. Otherwise, handle manual address entry (Guest style)
        else:
            guest_address = {
                'full_name': request.POST.get('full_name', ''),
                'phone': request.POST.get('phone', ''),
                'email': request.POST.get('email', ''),
                'address_line1': request.POST.get('address_line1', ''),
                'address_line2': request.POST.get('address_line2', ''),
                'city': request.POST.get('city', ''),
                'area': request.POST.get('area', ''),
                'postal_code': request.POST.get('postal_code', ''),
                'country': request.POST.get('country', 'Bangladesh'),
            }
            
            # Simple validation to ensure it's not "nothing happened" because of missing data
            if not guest_address['full_name'] or not guest_address['address_line1']:
                messages.error(request, 'Please fill in all required fields.')
            else:
                session.guest_email = guest_address['email']
                session.guest_phone = guest_address['phone']
                session.guest_shipping_address = guest_address
                session.same_as_shipping = request.POST.get('same_as_shipping') == 'on'
                
                # Clear saved address if manual entry used
                session.shipping_address = None
                
                if session.same_as_shipping:
                    session.guest_billing_address = guest_address
                else:
                    session.guest_billing_address = {
                        'full_name': request.POST.get('billing_full_name', ''),
                        'phone': request.POST.get('billing_phone', ''),
                        'address_line1': request.POST.get('billing_address_line1', ''),
                        'address_line2': request.POST.get('billing_address_line2', ''),
                        'city': request.POST.get('billing_city', ''),
                        'area': request.POST.get('billing_area', ''),
                        'postal_code': request.POST.get('billing_postal_code', ''),
                        'country': request.POST.get('billing_country', 'Bangladesh'),
                    }
                
                session.current_step = 'shipping'
                session.save()
                return redirect('checkout:shipping')

    
    # Get user's saved addresses
    addresses = []
    if request.user.is_authenticated:
        addresses = request.user.addresses.all()
    
    context = {
        'cart': cart,
        'session': session,
        'addresses': addresses,
        'step': 'address',
    }
    return render(request, 'checkout/checkout_address.html', context)


@login_required
def checkout_shipping(request):
    """Step 2: Shipping method selection."""
    cart = SessionCart(request)
    
    if len(cart) == 0:
        return redirect('cart:cart_detail')
    
    session = get_or_create_checkout_session(request)
    
    # Check prerequisite
    if not session.shipping_address and not session.guest_shipping_address:
        return redirect('checkout:address')
    
    if request.method == 'POST':
        shipping_id = request.POST.get('shipping_method')
        if shipping_id:
            shipping_method = get_object_or_404(ShippingMethod, id=shipping_id, is_active=True)
            session.shipping_method = shipping_method
            session.customer_note = request.POST.get('customer_note', '')
            session.current_step = 'review'
            session.save()
            return redirect('checkout:review')
    
    # Get shipping methods
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    cart_total = cart.get_total_price()
    
    # Calculate prices for each method
    methods_with_prices = []
    for method in shipping_methods:
        price = method.get_price_for_amount(cart_total)
        methods_with_prices.append({
            'method': method,
            'price': price,
            'is_free': price == 0,
        })
    
    context = {
        'cart': cart,
        'session': session,
        'shipping_methods': methods_with_prices,
        'step': 'shipping',
    }
    return render(request, 'checkout/checkout_shipping.html', context)


@login_required
def checkout_payment(request):
    """Step 3: Payment method selection."""
    cart = SessionCart(request)
    
    if len(cart) == 0:
        return redirect('cart:cart_detail')
    
    session = get_or_create_checkout_session(request)
    
    # Check prerequisites
    if not session.shipping_address and not session.guest_shipping_address:
        return redirect('checkout:address')
    if not session.shipping_method:
        return redirect('checkout:shipping')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method in ['sslcommerz', 'cod']:
            session.payment_method = payment_method
            session.current_step = 'review'
            session.save()
            return redirect('checkout:review')
            
    context = {
        'cart': cart,
        'session': session,
        'step': 'payment',
    }
    return render(request, 'checkout/checkout_payment.html', context)


@login_required
def checkout_review(request):
    """Step 3: Review order and place it."""
    cart = SessionCart(request)
    
    if len(cart) == 0:
        return redirect('cart:cart_detail')
    
    session = get_or_create_checkout_session(request)
    
    # Check prerequisites
    if not session.shipping_address and not session.guest_shipping_address:
        return redirect('checkout:address')
    if not session.shipping_method:
        return redirect('checkout:shipping')
    if not session.payment_method:
        return redirect('checkout:payment')
    
    # Calculate totals
    subtotal = cart.get_total_price()
    shipping_cost = session.shipping_method.get_price_for_amount(subtotal)
    total = subtotal + Decimal(str(shipping_cost))
    
    # Get address display
    if session.shipping_address:
        shipping_display = session.shipping_address.get_full_address()
        shipping_data = {
            'full_name': session.shipping_address.full_name,
            'phone': session.shipping_address.phone,
            'address_line1': session.shipping_address.address_line1,
            'address_line2': session.shipping_address.address_line2,
            'city': session.shipping_address.city,
            'area': session.shipping_address.area,
            'postal_code': session.shipping_address.postal_code,
            'country': session.shipping_address.country,
        }
    else:
        addr = session.guest_shipping_address
        shipping_display = f"{addr.get('full_name')}\n{addr.get('address_line1')}\n{addr.get('city')}, {addr.get('postal_code')}\n{addr.get('country')}"
        shipping_data = addr
    
    context = {
        'cart': cart,
        'session': session,
        'shipping_display': shipping_display,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
        'step': 'review',
    }
    return render(request, 'checkout/checkout_review.html', context)


@require_POST
def place_order(request):
    """Place the order and redirect to payment or confirmation."""
    cart = SessionCart(request)
    
    if len(cart) == 0:
        return redirect('cart:cart_detail')
    
    session = get_or_create_checkout_session(request)
    
    # Validate session is complete
    if not session.is_complete():
        messages.error(request, 'Please complete all checkout steps.')
        return redirect('checkout:checkout')
    
    # Calculate totals
    subtotal = cart.get_total_price()
    shipping_cost = session.shipping_method.get_price_for_amount(subtotal)
    total = subtotal + Decimal(str(shipping_cost))
    
    # Prepare address data
    if session.shipping_address:
        shipping_data = {
            'full_name': session.shipping_address.full_name,
            'phone': session.shipping_address.phone,
            'address_line1': session.shipping_address.address_line1,
            'address_line2': session.shipping_address.address_line2,
            'city': session.shipping_address.city,
            'area': session.shipping_address.area,
            'postal_code': session.shipping_address.postal_code,
            'country': session.shipping_address.country,
        }
        billing_data = shipping_data if session.same_as_shipping else {
            'full_name': session.billing_address.full_name if session.billing_address else '',
            'phone': session.billing_address.phone if session.billing_address else '',
            'address_line1': session.billing_address.address_line1 if session.billing_address else '',
            'address_line2': session.billing_address.address_line2 if session.billing_address else '',
            'city': session.billing_address.city if session.billing_address else '',
            'area': session.billing_address.area if session.billing_address else '',
            'postal_code': session.billing_address.postal_code if session.billing_address else '',
            'country': session.billing_address.country if session.billing_address else '',
        }
    else:
        shipping_data = session.guest_shipping_address
        billing_data = shipping_data if session.same_as_shipping else session.guest_billing_address
    
    with transaction.atomic():
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            guest_email=session.guest_email,
            guest_phone=session.guest_phone,
            shipping_address=shipping_data,
            billing_address=billing_data,
            shipping_method_name=session.shipping_method.name,
            shipping_cost=shipping_cost,
            estimated_delivery=session.shipping_method.get_delivery_estimate(),
            subtotal=subtotal,
            total=total,
            customer_note=session.customer_note,
            promo_code=session.promo_code,
        )
        
        # Create order items from cart
        for item in cart:
            variant = item['variant']
            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_name=variant.product.name,
                variant_name=variant.variant_name or '',
                sku=variant.sku,
                product_image=variant.get_image().image.url if variant.get_image() else '',
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['total_price'],
                is_digital=variant.product.product_type == 'digital',
            )
        
        # Clear cart
        cart.clear()
        
        # Store order number in session for confirmation page
        request.session['last_order_number'] = order.order_number
        
        # Create PaymentTransaction
        transaction_id = f"{order.order_number}_{uuid.uuid4().hex[:8]}"
        pmt_transaction = PaymentTransaction.objects.create(
            transaction_id=transaction_id,
            order=order,
            amount=total,
            payment_method=session.payment_method,
            status='pending'
        )
        
        # SSLCommerz Logic
        if session.payment_method == 'sslcommerz':
            ssl = SSLCommerzProvider()
            gateway_url, error_message = ssl.init_payment(order, transaction_id, request)
            
            if gateway_url:
                # Delete checkout session after redirecting to payment
                session.delete()
                return redirect(gateway_url)
            else:
                messages.error(request, f'SSLCommerz Error: {error_message}')
                # Rollback transaction (implicitly handled by atomic)
                raise Exception(f"SSLCommerz initialization failed: {error_message}")

        # COD Logic
        elif session.payment_method == 'cod':
            order.payment_method = 'cod'
            order.save()
            
            # Delete checkout session
            session.delete()
            
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('checkout:order_confirmation', order_number=order.order_number)
            
    # Fallback
    return redirect('checkout:review')


def order_confirmation(request, order_number):
    """Order confirmation page."""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Verify access
    if order.user:
        if not request.user.is_authenticated or request.user != order.user:
            # Check if coming from checkout
            if request.session.get('last_order_number') != order_number:
                messages.error(request, 'You do not have access to this order.')
                return redirect('core:home')
    
    context = {
        'order': order,
    }
    return render(request, 'checkout/order_confirmation.html', context)
