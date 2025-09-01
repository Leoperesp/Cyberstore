from django.db import models
from users.models import CustomUser# Para vincular con el usuario

class Category(models.Model):
    name = models.CharField(max_length=100)
    # ... otros campos

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='templates/imgs', blank=True)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    is_offered = models.BooleanField(default=False)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # ... otros campos

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, choices=[('credit_card', 'Tarjeta de Crédito'), ('paypal', 'PayPal'), ('cash', 'Efectivo')]) # Ejemplo de métodos de pago
    shipping_address = models.TextField()
    # ... campos de envío

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)