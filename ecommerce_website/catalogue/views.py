# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'catalogue/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'catalogue/product_detail.html', {
        'product': product
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save
            auth_login(request,user)
            return(redirect)
    else:
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form':form})
    
def login(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save
            auth_login(request,user)
            return(redirect)
    else:
        form = UserCreationForm()
        return render(request, 'registration/login.html', {'form':form})