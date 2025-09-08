from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid',
                    'created', 'updated', 'status']
    list_filter = ['paid', 'created', 'updated', 'status']
    search_fields = ['first_name', 'last_name', 'email', 'address']
    inlines = [OrderItemInline]
    list_editable = ['paid', 'status']
