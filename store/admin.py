from django.contrib import admin
from .models import Product, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'image', 'is_available', 'description', 'is_offered', 'offer_price')
    search_fields = ('name', 'description')
    list_filter = ('name', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    raw_id_fields = ('user',) 