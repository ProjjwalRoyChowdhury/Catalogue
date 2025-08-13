from django.contrib import admin
from catalogue.models import Category, Product

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug' : ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price' , 'available', 'stock']
    list_filter = ['available', 'category']
    prepopulated_fields = { 'slug' : ('name',)}