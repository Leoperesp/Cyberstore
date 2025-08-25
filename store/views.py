from .models import Product
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    # 1. Obtener la información del carrito del usuario.
    # 2. Procesar el formulario de dirección de envío.
    # 3. Crear el objeto Order en la base de datos.
    # 4. Redirigir a la pasarela de pago.
    # ...
    pass

def home(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'store/home.html', {'products': products})