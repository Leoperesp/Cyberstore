from django.db import models
from users.models import CustomUser# Para vincular con el usuario

class Product(models.Model):
    category = models.CharField(
        choices=[
            ('Procesadores', 'Procesadores'),
            ('Monitores', 'Monitores'),
            ('Memorias RAM', 'Memorias RAM'),
            ('Memorias de Almacenamiento', 'Memorias de Almacenamiento'),
            ('Placas de video', 'Placas de video'),
            ('Fuentes de energia', 'Fuentes de energia'),
            ('Motherboards', 'Motherboards'),
            ('Refrigeracion', 'Refrigeracion'),
            ('Gabinetes', 'Gabinetes')
        ],
        default='Procesadores')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='products/', blank=True)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    is_offered = models.BooleanField(default=False)
    offer_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    document_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,

    )
    
    full_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(
        choices=[
            ('credit_card', 'Tarjeta de Crédito'),
            ('paypal', 'PayPal'),
            ('cash', 'Efectivo')
        ],
        default='cash'
    )

    shipping_address = models.CharField(
        max_length=255,
        blank=True, 
        null=True 
    )
    
    status = models.CharField(
        choices=[('pending', 'Pendiente'), ('shipped', 'Enviado'), ('delivered', 'Entregado'), ('canceled', 'Cancelado')],
        default='pending'
    )
    observations = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.user:
            # Precargar full_name del usuario (se asume que CustomUser tiene first_name y last_name)
            if not self.full_name:
                self.full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            
            # Asignar document_number
            if not self.document_number and hasattr(self.user, 'document_number'):
                self.document_number = self.user.document_number
            
            # Asignar shipping_address
            if not self.shipping_address and hasattr(self.user, 'address'):
                self.shipping_address = self.user.address
                
            # Asignar shipping_phone
            if not self.shipping_phone and hasattr(self.user, 'phone_number'):
                self.shipping_phone = self.user.phone_number
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username if self.user else 'Guest'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} en orden {self.order.id}'

    def get_total(self):
        return self.price * self.quantity 

    @property
    def subtotal(self):
        return self.price * self.quantity