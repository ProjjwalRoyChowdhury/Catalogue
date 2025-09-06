from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils.text import slugify
from django.utils import timezone
from django.http import HttpResponseRedirect
from datetime import timedelta

from products.models import Product, Category, ProductImage
from orders.models import Order, OrderItem
from .forms import ProductForm, OrderStatusForm, OrderNoteForm

# Helper function to check if user is staff
def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def dashboard_home(request):
    # Get counts for dashboard overview
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    recent_orders = Order.objects.order_by('-created')[:5]
    
    # Get orders from the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_orders_count = Order.objects.filter(created__gte=thirty_days_ago).count()
    
    # Get pending orders
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Get low stock products (less than 5 items)
    low_stock_products = Product.objects.filter(stock__lt=5).count()
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'recent_orders_count': recent_orders_count,
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
    }
    
    return render(request, 'dashboard/dashboard_home.html', context)

@login_required
@user_passes_test(is_staff)
def product_management(request):
    products = Product.objects.all().order_by('-created')
    categories = Category.objects.all()
    
    # Filter by category if requested
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/product_management.html', context)

@login_required
@user_passes_test(is_staff)
def product_add(request):
    if request.method == 'POST':
        form = request.POST
        product = Product()
        product.name = form.get('name')
        product.category_id = form.get('category')
        product.description = form.get('description')
        product.price = form.get('price')
        product.stock = form.get('stock')
        product.available = form.get('available') == 'on'
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        
        product.save()
        messages.success(request, f'Product "{product.name}" has been added successfully.')
        return redirect('dashboard:product_management')
    
    categories = Category.objects.all()
    return render(request, 'dashboard/product_form.html', {
        'categories': categories,
        'title': 'Add Product'
    })

@login_required
@user_passes_test(is_staff)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = request.POST
        product.name = form.get('name')
        product.category_id = form.get('category')
        product.description = form.get('description')
        product.price = form.get('price')
        product.stock = form.get('stock')
        product.available = form.get('available') == 'on'
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        
        product.save()
        messages.success(request, f'Product "{product.name}" has been updated successfully.')
        return redirect('dashboard:product_management')
    
    categories = Category.objects.all()
    return render(request, 'dashboard/product_form.html', {
        'product': product,
        'categories': categories,
        'title': 'Edit Product'
    })

@login_required
@user_passes_test(is_staff)
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" has been deleted successfully.')
        return redirect('dashboard:product_management')
    
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})

@login_required
@user_passes_test(is_staff)
def order_management(request):
    orders = Order.objects.all().order_by('-created')
    
    # Filter by status if requested
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by payment status if requested
    payment = request.GET.get('payment')
    if payment:
        paid = payment == 'paid'
        orders = orders.filter(paid=paid)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            id__icontains=search_query
        ) | orders.filter(
            user__username__icontains=search_query
        ) | orders.filter(
            email__icontains=search_query
        ) | orders.filter(
            first_name__icontains=search_query
        ) | orders.filter(
            last_name__icontains=search_query
        )
    
    context = {
        'orders': orders,
        'selected_status': status,
        'selected_payment': payment,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/order_management.html', context)

@login_required
@user_passes_test(is_staff)
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    return render(request, 'dashboard/order_detail.html', {'order': order})

@login_required
@user_passes_test(is_staff)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        paid = request.POST.get('paid') == 'True'
        
        if status:
            order.status = status
        
        order.paid = paid
        order.save()
        
        messages.success(request, f'Order #{order.id} has been updated successfully.')
        return redirect('dashboard:order_detail', order_id=order.id)
    
    return redirect('dashboard:order_detail', order_id=order.id)

@login_required
@user_passes_test(is_staff)
def add_order_note(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderNoteForm(request.POST)
        if form.is_valid():
            note = form.cleaned_data['note']
            # Here you would save the note to your database
            # For now, just show a success message
            messages.success(request, 'Note added successfully.')
            
    return redirect('dashboard:order_detail', order_id=order.id)
