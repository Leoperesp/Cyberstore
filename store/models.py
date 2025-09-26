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
        # Si el usuario está autenticado, asignar datos automáticamente
        if self.user:
            # Asignar document_number
            if not self.document_number and self.user.document_number:
                self.document_number = self.user.document_number
            
            # Asignar shipping_address
            if not self.shipping_address and self.user.address:
                self.shipping_address = self.user.address
        
        # Guardar la instancia del modelo en la base de datos
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username if self.user else 'Guest'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)