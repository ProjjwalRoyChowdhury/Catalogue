from django.shortcuts import render
from products.models import Product, Category

def home(request):
    # Get featured products (for simplicity, we'll just get the latest products)
    featured_products = Product.objects.filter(available=True)[:8]
    
    # Get all categories
    categories = Category.objects.all()
    
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories
    })