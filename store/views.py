from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from .models import Product, Order, OrderItem
from .forms import ProductForm, ShippingForm
from .models import Order
from decimal import Decimal

def home(request):
    offered_products = Product.objects.filter(is_offered=True)
    for product in offered_products:
        if product.price and product.offer_price > 0:
            discount_percentage = ((product.price - product.offer_price) / product.price) * 100
            product.discount_percentage = round(discount_percentage)
        else:
            product.discount_percentage = 0
    context = {
        'products': offered_products
    }
    
    return render(request, 'store/home.html', context)

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/products.html', {'products': products})

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def about(request):
    return render(request, 'store/about.html') 

def contact(request):
    return render(request, 'store/contact.html')

def faq(request):
    return render(request, 'store/faq.html')

# Vistas para la gestión de productos
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
    products = Product.objects.all()
    return render(request, 'store/admin/manage_orders.html', {'products': products})

def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'shipped':
            order.status = 'shipped'
        elif action == 'canceled':
            order.status = 'canceled'
        order.save()
        return redirect('store:order_detail', order_id=order.id)
    return render(request, 'store/admin/order_detail.html', {'order': order})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    product_id_str = str(product.id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1 

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
        messages.success(request, f'Se agregaron {quantity} unidades más de "{product.name}" al carrito.')
    else:
        cart[product_id_str] = {
            'quantity': quantity,
            'price': str(product.price)
        }
        messages.success(request, f'"{product.name}" fue agregado a tu carrito (Cantidad: {quantity}).')

    request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def view_cart(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = Decimal(0) # Inicia total_price como un Decimal

    for product_id_str, item_data in cart.items():
        try:
            product = get_object_or_404(Product, pk=product_id_str)

            quantity = item_data['quantity']

            item_price = product.price

            if product.is_offered:
                item_total = product.offer_price * quantity
            else:
                 item_total = product.price * quantity

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total,
            })

            total_price += item_total

        except (KeyError, ValueError, Product.DoesNotExist):
            pass 

    context = {
        'cart_items': cart_items,
        'cart_total': total_price,
    }

    return render(request, 'store/cart.html', context)


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('store:view_cart')

def clear_cart(request):
    request.session['cart'] = {}
    return redirect('store:view_cart')

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('store:view_cart')
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    if request.method == 'POST':
        # Aquí iría la lógica para procesar el pago y crear la orden
        request.session['cart'] = {}  # Limpiar el carrito después del checkout
        return redirect('store:home')
    return render(request, 'store/checkout.html', {'cart': cart, 'total': total})

def checkout_cash(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('store:view_cart')
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    if request.method == 'POST':
        # Aquí iría la lógica para crear la orden con pago en efectivo
        request.session['cart'] = {}  # Limpiar el carrito después del checkout
        return redirect('store:home')
    return render(request, 'store/checkout_cash.html', {'cart': cart, 'total': total})

def send_email(request):
    return render(request, 'store/email.html') 

@login_required
def cash_payment_view(request):
    cart_session = request.session.get('cart', {})
    if not cart_session:
        messages.warning(request, 'Tu carrito está vacío. Agrega productos para continuar.')
        return redirect('store:view_cart')

    # Lógica de cálculo del Carrito
    cart_items = []
    total_price = Decimal(0)
    for product_id_str, item_data in cart_session.items():
        try:
            product = get_object_or_404(Product, pk=product_id_str)
            quantity = item_data['quantity']
            
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
            continue

    # --- Lógica de Precarga del Formulario (Autocompletado) ---
    user = request.user
    
    # Prepara el nombre completo, usando .strip() para evitar espacios extra si un nombre falta
    full_name = f"{user.first_name} {user.last_name}".strip()
    
    initial_data = {
        'name': full_name,
        # Obtiene directamente de los campos del CustomUser
        'address': user.address, 
        'phone': user.phone_number,
    }
    
    # Si hay errores de validación de un POST anterior, recarga con esos datos fallidos (mejor UX)
    if request.session.get('shipping_form_post_data'):
        # Recarga con los datos que fallaron la validación
        form = ShippingForm(request.session.pop('shipping_form_post_data'))
    else:
        # Primera carga (GET), usa los datos iniciales del CustomUser
        form = ShippingForm(initial=initial_data)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form, # Pasa el formulario autocompletado/recargado
    }
    
    # NOTA: Asegúrate de que tu template 'store/checkout_cash.html' use el form.
    return render(request, 'store/checkout_cash.html', context)

# ----------------------------------------------------------------------
## 2. process_cash_payment: Procesa el Formulario de Envío Editado (POST)
# ----------------------------------------------------------------------

@login_required 
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
            
            # 1. Actualiza los datos del usuario con los datos del formulario (si fueron editados)
            user.address = shipping_data['address']
            user.phone_number = shipping_data['phone']
            user.save() 
            
            # 2. Recálculo del carrito y preparación de OrderItem
            total_price = Decimal(0)
            order_items_data = [] 
            
            for product_id_str, item_data in cart_session.items():
                try:
                    product = get_object_or_404(Product, pk=product_id_str)
                    quantity = item_data['quantity']
                    
                    price_to_use = product.offer_price if product.is_offered and product.offer_price else product.price
                    item_total = price_to_use * quantity
                    total_price += item_total
                    
                    order_items_data.append({
                        'product': product,
                        'quantity': quantity,
                        'unit_price': price_to_use,
                    })
                except Product.DoesNotExist:
                    continue
            
            # 3. Crear la Orden (usando los datos recién validados/editados)
            order = Order.objects.create(
                user=request.user,
                # Usa los datos validados del formulario:
                full_name=shipping_data['name'], 
                shipping_phone=shipping_data['phone'], 
                shipping_address=shipping_data['address'], 
                
                total_amount=total_price,
                payment_method='cash',
                is_paid=False, 
                status='pending',
            )

            # 4. Crear los ítems de la orden (OrderItem)
            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['unit_price'],
                )
            
            # 5. Finalizar la transacción
            del request.session['cart']
            messages.success(request, f'¡Tu pedido #{order.id} ha sido confirmado! Recibirás la entrega en la dirección: {order.shipping_address}. Por favor, prepara ${total_price} en efectivo.')
            return redirect('store:home')
        
        else:
            # Si la validación falla (ej. campo requerido vacío)
            # Guardamos los datos POST en la sesión para que cash_payment_view los recargue
            request.session['shipping_form_post_data'] = request.POST
            messages.error(request, 'Hubo un error con los datos de envío. Por favor, verifica y reintenta.')
            return redirect('store:cash_payment_view') # Redirige a la vista GET para mostrar el formulario con errores

    # Si se accede por GET, redirige a la vista principal
    return redirect('store:cash_payment_view')