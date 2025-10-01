from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.db import transaction # ⬅️ IMPORTANTE: Importación para transacciones atómicas
from .models import Product, Order, OrderItem
from .forms import ProductForm, ShippingForm
from decimal import Decimal

# ----------------------------------------------------------------------
## FUNCIONES AUXILIARES
# ----------------------------------------------------------------------

def get_cart_total_and_items(request):
    """
    Calcula el precio total y prepara la lista de ítems del carrito
    basándose en los precios y descuentos actuales de la base de datos.
    """
    cart_session = request.session.get('cart', {})
    cart_items = []
    total_price = Decimal(0)

    for product_id_str, item_data in cart_session.items():
        try:
            product = get_object_or_404(Product, pk=product_id_str)
            quantity = item_data['quantity']
            
            # Determina el precio a usar (oferta o regular)
            price_to_use = product.offer_price if product.is_offered and product.offer_price else product.price
            
            item_total = price_to_use * quantity
            total_price += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total,
                'unit_price': price_to_use, 
            })
        except Product.DoesNotExist:
            # Si un producto del carrito ya no existe, lo ignora
            continue
            
    return cart_items, total_price

# ----------------------------------------------------------------------
## VISTAS PÚBLICAS
# ----------------------------------------------------------------------

def home(request):
    offered_products = Product.objects.filter(is_offered=True)
    for product in offered_products:
        if product.price and product.offer_price and product.offer_price > 0:
            discount_percentage = ((product.price - product.offer_price) / product.price) * 100
            product.discount_percentage = round(discount_percentage)
        else:
            product.discount_percentage = 0
    context = {
        'products': offered_products
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    # 1. Obtener todas las opciones de categoría directamente desde el modelo Product
    # Esto te dará una lista de tuplas: [('Procesadores', 'Procesadores'), ('Monitores', 'Monitores'), ...]
    category_choices = Product.category.field.choices
    
    # Transformamos las tuplas en una lista simple de strings (solo la parte legible/slug)
    # Esto resulta en: ['Procesadores', 'Monitores', ...]
    categories = [choice[0] for choice in category_choices]
    
    # ... el resto de la lógica de la vista continúa abajo ...
    
    # 2. Inicialmente, obtenemos todos los productos.
    products = Product.objects.all()
    current_category = None
    
    # 3. Obtener la categoría del parámetro de la URL (query parameter)
    category_filter = request.GET.get('category')
    
    if category_filter:
        # Usamos .filter() directamente en el campo 'category'
        products = products.filter(category=category_filter)
        current_category = category_filter # Guardamos el string de la categoría activa
    
    context = {
        'products': products,
        'categories': categories,         # Pasamos la lista de categorías
        'current_category': current_category, # Pasamos la categoría activa (string)
    }
    
    return render(request, 'store/products.html', context)

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def about(request):
    return render(request, 'store/about.html') 

def contact(request):
    return render(request, 'store/contact.html')

def faq(request):
    return render(request, 'store/faq.html')

# ----------------------------------------------------------------------
## VISTAS DE GESTIÓN DE PRODUCTOS Y ÓRDENES (ADMIN)
# ----------------------------------------------------------------------

def manage_products(request):
    products = Product.objects.all()
    return render(request, 'store/admin/manage_products.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('store:manage_products')
    else:
        form = ProductForm()
    return render(request, 'store/admin/add_product.html', {'form': form})

def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('store:manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/admin/edit_product.html', {'form': form})

def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('store:manage_products')

def manage_orders(request):
    orders = Order.objects.all().order_by('-created_at') # Mostrar órdenes, no productos
    return render(request, 'store/admin/manage_orders.html', {'orders': orders})

def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'shipped':
            order.status = 'shipped'
            order.save()
            messages.success(request, f'El estado de la orden #{order.id} ha sido actualizado a {order.status}.')
            
        elif action == 'canceled':
            return redirect('store:cancel_order_and_return_stock', order_id=order.id)
        
        return redirect('store:manage_orders') # Redirigir a la lista de órdenes
    
    return render(request, 'store/admin/order_detail.html', {'order': order})


@transaction.atomic
def cancel_order_and_return_stock(request, order_id):

    if request.method != 'POST':
        return redirect('store:manage_orders')

    order = get_object_or_404(Order, id=order_id)
    order_id_log = order.id
    
    # 1. Evitar la devolución doble de stock
    if order.status == 'canceled':
        messages.warning(request, f'La orden #{order_id_log} ya estaba cancelada. No se modificó el stock.')
        return redirect('store:manage_orders')

    # 2. Devolver el inventario
    items_to_return = list(order.orderitem_set.all())
    items_returned_count = 0
    for item in items_to_return:
        # ... lógica de stock ...
        product = item.product
        quantity = item.quantity
        product.stock += quantity
        product.save() 
        items_returned_count += 1
        
    # 3. Actualizar el estado de la orden
    order.status = 'canceled'
    order.save()

    messages.success(request, f'La orden **#{order_id_log}** ha sido **CANCELADA** y sus productos ({items_returned_count} items) han regresado al inventario. ✅')
    return redirect('store:manage_orders')

# ----------------------------------------------------------------------
## VISTAS DE CARRITO Y CHECKOUT
# ----------------------------------------------------------------------

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    product_id_str = str(product.id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1 
        
    if quantity <= 0:
         messages.error(request, 'La cantidad debe ser mayor a cero.')
         return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # Comprobar si hay suficiente stock (corrección básica)
    current_quantity_in_cart = cart.get(product_id_str, {}).get('quantity', 0)
    
    if (current_quantity_in_cart + quantity) > product.stock:
        messages.error(request, f'Solo quedan {product.stock} unidades de "{product.name}". No podemos agregar {quantity} unidades más.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))


    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
        messages.success(request, f'Se agregaron {quantity} unidades más de "{product.name}" al carrito.')
    else:
        cart[product_id_str] = {
            'quantity': quantity,
            # Guardamos el precio en la sesión solo como referencia rápida, 
            # pero el precio real se calcula siempre desde la DB en view_cart y checkout
            'price': str(product.price) 
        }
        messages.success(request, f'"{product.name}" fue agregado a tu carrito (Cantidad: {quantity}).')

    request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def view_cart(request):
    cart_items, total_price = get_cart_total_and_items(request)

    context = {
        'cart_items': cart_items,
        'cart_total': total_price,
    }

    return render(request, 'store/cart.html', context)


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        product_name = get_object_or_404(Product, id=product_id).name
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.info(request, f'"{product_name}" ha sido eliminado de tu carrito.')
    return redirect('store:view_cart')

def clear_cart(request):
    request.session['cart'] = {}
    messages.info(request, 'Tu carrito ha sido vaciado.')
    return redirect('store:view_cart')

# Vistas de checkout genéricas (no modificadas)
def checkout(request):
    # La lógica de esta vista es incompleta, pero se mantiene como en tu original
    cart_items, total_price = get_cart_total_and_items(request)
    
    if not cart_items:
        return redirect('store:view_cart')
        
    if request.method == 'POST':
        # Aquí iría la lógica para procesar el pago con tarjeta/pasarela
        messages.success(request, 'Proceso de pago completado (Simulación).')
        request.session['cart'] = {} 
        return redirect('store:home')
    
    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total_price})

def checkout_cash(request):
    # Esta vista es ahora redundante y DEBE USAR cash_payment_view
    return redirect('store:cash_payment_view')

def send_email(request):
    return render(request, 'store/email.html') 

@login_required
def cash_payment_view(request):
    cart_items, total_price = get_cart_total_and_items(request)

    if not cart_items:
        messages.warning(request, 'Tu carrito está vacío. Agrega productos para continuar.')
        return redirect('store:view_cart')

    # --- Lógica de Precarga del Formulario (Autocompletado) ---
    user = request.user
    
    full_name = f"{user.first_name} {user.last_name}".strip()
    
    initial_data = {
        'name': full_name,
        # Asume que estos campos existen en tu modelo CustomUser
        'address': getattr(user, 'address', ''), 
        'phone': getattr(user, 'phone_number', ''),
    }
    
    # Si hay errores de validación de un POST anterior, recarga con esos datos fallidos
    if request.session.get('shipping_form_post_data'):
        form = ShippingForm(request.session.pop('shipping_form_post_data'))
    else:
        # Primera carga (GET), usa los datos iniciales del CustomUser
        form = ShippingForm(initial=initial_data)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    }
    
    return render(request, 'store/checkout_cash.html', context)

# ----------------------------------------------------------------------
## process_cash_payment: Procesa el Formulario de Envío Editado (POST)
# ----------------------------------------------------------------------

@login_required 
@transaction.atomic # ⬅️ APLICACIÓN DE TRANSACCIÓN ATÓMICA
def process_cash_payment(request):
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        cart_session = request.session.get('cart', {})
        
        if not cart_session:
            messages.error(request, 'No hay productos en tu carrito para procesar el pedido.')
            return redirect('store:view_cart')

        if form.is_valid():
            shipping_data = form.cleaned_data
            user = request.user
            
            # 1. Recálculo y validación final del carrito (¡stock crítico!)
            order_items_data, total_price = get_cart_total_and_items(request)
            
            if not order_items_data:
                 messages.error(request, 'El carrito está vacío o los productos ya no existen. Intenta agregar productos de nuevo.')
                 del request.session['cart']
                 return redirect('store:view_cart')
                 
            # 2. Actualiza los datos del usuario 
            user.address = shipping_data['address']
            user.phone_number = shipping_data['phone']
            user.save() 
            
            # 3. Crear la Orden
            order = Order.objects.create(
                user=request.user,
                full_name=shipping_data['name'], 
                shipping_phone=shipping_data['phone'], 
                shipping_address=shipping_data['address'], 
                
                total_amount=total_price,
                payment_method='cash',
                is_paid=False, 
                status='pending',
            )

            # 4. Crear los ítems de la orden y DESCONTAR INVENTARIO ⬅️ CORRECCIÓN CLAVE
            for item_data in order_items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                
                # DOBLE CHECK DE STOCK JUSTO ANTES DE DESCONTAR
                if product.stock < quantity:
                    # Esto solo pasaría si alguien compra justo antes o si se salteó la validación del carrito
                    # La transacción atómica hará un ROLLBACK completo si lanzamos una excepción,
                    # pero aquí simplemente lanzaremos un mensaje de error y limpiaremos.
                    messages.error(request, f'¡Error! El stock del producto "{product.name}" (actual: {product.stock}) no es suficiente para la cantidad solicitada ({quantity}).')
                    
                    # Es crucial lanzar un error para que el @transaction.atomic revierta la Order creada
                    # Puedes usar una excepción específica o lanzar una excepción que revierta la DB.
                    # Aquí forzaremos la redirección y el error.
                    raise Exception("Stock Insuficiente en el momento de la creación de la orden.")
                
                # ⬇️ DESCUENTO DEL INVENTARIO
                product.stock -= quantity
                product.save() 
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=item_data['unit_price'],
                )
            
            # 5. Finalizar la transacción
            del request.session['cart']
            messages.success(request, f'¡Tu pedido **#{order.id}** ha sido confirmado! Recibirás la entrega en la dirección: {order.shipping_address}. Por favor, prepara ${total_price} en efectivo.')
            return redirect('store:home')
        
        else:
            # Si la validación del formulario falla
            request.session['shipping_form_post_data'] = request.POST
            messages.error(request, 'Hubo un error con los datos de envío. Por favor, verifica y reintenta.')
            return redirect('store:cash_payment_view')

    # Si se accede por GET, redirige a la vista principal
    return redirect('store:cash_payment_view')