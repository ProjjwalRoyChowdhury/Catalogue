import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from orders.models import Order

# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_process(request):
    # Get the order ID from the session or query parameters
    order_id = request.GET.get('order_id')
    if not order_id and 'order_id' in request.session:
        order_id = request.session['order_id']
    
    # If no order ID is found, redirect to order history
    if not order_id:
        messages.error(request, 'No order found for payment.')
        return redirect('orders:order_history')
    
    # Get the order object
    order = get_object_or_404(Order, id=order_id)
    
    # Check if the order belongs to the current user
    if order.user != request.user:
        messages.error(request, 'You do not have permission to pay for this order.')
        return redirect('orders:order_history')
    
    # Check if the order is already paid
    if order.paid:
        messages.info(request, 'This order has already been paid.')
        return redirect('orders:order_detail', order_id=order.id)
    
    # Create Stripe checkout session
    if request.method == 'POST':
        try:
            # Create line items for Stripe
            line_items = []
            for item in order.items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                            'images': [request.build_absolute_uri(item.product.image.url)] if item.product.image else [],
                        },
                        'unit_amount': int(item.price * 100),  # Convert to cents
                    },
                    'quantity': item.quantity,
                })
            
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                customer_email=order.email,
                success_url=request.build_absolute_uri(reverse('payment:success')) + f'?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}',
                cancel_url=request.build_absolute_uri(reverse('payment:canceled')),
                metadata={'order_id': order.id}
            )
            
            # Store the session ID in the session
            request.session['stripe_session_id'] = checkout_session.id
            
            # Redirect to Stripe payment form
            return redirect(checkout_session.url, code=303)
        
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('orders:order_detail', order_id=order.id)
    
    # Render the payment form
    return render(request, 'payment/process.html', {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@login_required
def payment_success(request):
    # Get the session ID and order ID from the URL
    session_id = request.GET.get('session_id')
    order_id = request.GET.get('order_id')
    
    if not session_id or not order_id:
        messages.error(request, 'Invalid payment information.')
        return redirect('orders:order_history')
    
    # Get the order
    order = get_object_or_404(Order, id=order_id)
    
    # Check if the order belongs to the current user
    if order.user != request.user:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('orders:order_history')
    
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if the payment was successful
        if session.payment_status == 'paid':
            # Update the order
            order.paid = True
            order.stripe_id = session.payment_intent
            order.status = 'processing'
            order.save()
            
            messages.success(request, 'Payment successful! Your order is now being processed.')
        else:
            messages.warning(request, 'Payment is still pending. Please check your payment status.')
    
    except Exception as e:
        messages.error(request, f'Error verifying payment: {str(e)}')
    
    return render(request, 'payment/success.html', {'order': order})

@login_required
def payment_canceled(request):
    messages.warning(request, 'Payment was canceled.')
    
    # If there's an order ID in the session, redirect to the order detail page
    if 'order_id' in request.session:
        order_id = request.session['order_id']
        return redirect('orders:order_detail', order_id=order_id)
    
    return render(request, 'payment/canceled.html')

# Webhook for Stripe events
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get the order ID from the session metadata
        order_id = session.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.stripe_id = session.payment_intent
                order.status = 'processing'
                order.save()
            except Order.DoesNotExist:
                pass
    
    return HttpResponse(status=200)
