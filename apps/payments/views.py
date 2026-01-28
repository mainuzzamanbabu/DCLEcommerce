from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from apps.orders.models import Order
from .models import PaymentTransaction, WebhookEvent
from .utils import SSLCommerzProvider
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def sslcommerz_success(request):
    """Handle SSLCommerz success callback."""
    if request.method == 'POST':
        data = request.POST
        val_id = data.get('val_id')
        transaction_id = data.get('tran_id')
        
        # Log webhook
        WebhookEvent.objects.create(
            provider='sslcommerz',
            event_type='success',
            payload=data.dict()
        )
        
        # Validate payment
        ssl = SSLCommerzProvider()
        validation_result = ssl.validate_transaction(val_id)
        
        if validation_result and validation_result.get('status') == 'VALID':
            transaction = get_object_or_404(PaymentTransaction, transaction_id=transaction_id)
            order = transaction.order
            
            # Update transaction
            transaction.status = 'success'
            transaction.provider_reference = val_id
            transaction.provider_response = validation_result
            transaction.save()
            
            # Update order
            order.payment_status = 'paid'
            order.status = 'confirmed' # Or processing
            order.payment_method = 'sslcommerz'
            order.payment_transaction_id = transaction_id
            order.save()
            
            messages.success(request, 'Payment successful! Your order is now confirmed.')
            return redirect('checkout:order_confirmation', order_number=order.order_number)
        else:
            messages.error(request, 'Payment validation failed. Please contact support.')
            return redirect('core:home')
            
    return redirect('core:home')

@csrf_exempt
def sslcommerz_fail(request):
    """Handle SSLCommerz fail callback."""
    if request.method == 'POST':
        data = request.POST
        transaction_id = data.get('tran_id')
        
        # Log webhook
        WebhookEvent.objects.create(
            provider='sslcommerz',
            event_type='failed',
            payload=data.dict()
        )
        
        transaction = get_object_or_404(PaymentTransaction, transaction_id=transaction_id)
        transaction.status = 'failed'
        transaction.provider_response = data.dict()
        transaction.save()
        
        messages.error(request, 'Payment failed. Please try again.')
        return redirect('checkout:review')
        
    return redirect('core:home')

@csrf_exempt
def sslcommerz_cancel(request):
    """Handle SSLCommerz cancel callback."""
    if request.method == 'POST':
        data = request.POST
        transaction_id = data.get('tran_id')
        
        # Log webhook
        WebhookEvent.objects.create(
            provider='sslcommerz',
            event_type='cancelled',
            payload=data.dict()
        )
        
        transaction = get_object_or_404(PaymentTransaction, transaction_id=transaction_id)
        transaction.status = 'cancelled'
        transaction.provider_response = data.dict()
        transaction.save()
        
        messages.warning(request, 'Payment cancelled.')
        return redirect('checkout:review')
        
    return redirect('core:home')

@csrf_exempt
def sslcommerz_ipn(request):
    """Handle SSLCommerz IPN (Instant Payment Notification)."""
    if request.method == 'POST':
        data = request.POST
        val_id = data.get('val_id')
        transaction_id = data.get('tran_id')
        
        # Log webhook
        WebhookEvent.objects.create(
            provider='sslcommerz',
            event_type='ipn',
            payload=data.dict()
        )
        
        # IPN logic similar to success but background
        # Usually handled via a task queue ideally
        ssl = SSLCommerzProvider()
        validation_result = ssl.validate_transaction(val_id)
        
        if validation_result and validation_result.get('status') == 'VALID':
            try:
                transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
                if transaction.status != 'success':
                    order = transaction.order
                    
                    transaction.status = 'success'
                    transaction.provider_reference = val_id
                    transaction.provider_response = validation_result
                    transaction.save()
                    
                    order.payment_status = 'paid'
                    order.status = 'confirmed'
                    order.payment_method = 'sslcommerz'
                    order.payment_transaction_id = transaction_id
                    order.save()
                    
                    logger.info(f"IPN: Order {order.order_number} marked as PAID via IPN.")
            except PaymentTransaction.DoesNotExist:
                logger.error(f"IPN: Transaction {transaction_id} not found.")
                
    return render(request, 'core/base.html') # Return 200 OK
