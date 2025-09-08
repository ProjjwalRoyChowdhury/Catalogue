from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart

@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')
        
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                        product=item['product'],
                                        price=item['price'],
                                        quantity=item['quantity'])
            # Clear the cart
            cart.clear()
            # Set the order in the session
            request.session['order_id'] = order.id
            # Redirect for payment
            return redirect(reverse('payment:process'))
    else:
        # Pre-fill the form with user information
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        # If user has a profile with address information, use it
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            if profile.address:
                initial_data['address'] = profile.address
            if profile.postal_code:
                initial_data['postal_code'] = profile.postal_code
            if profile.city:
                initial_data['city'] = profile.city
                
        form = OrderCreateForm(initial=initial_data)
    return render(request, 'orders/create.html', {'cart': cart, 'form': form})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})
