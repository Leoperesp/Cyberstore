from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product 
from .forms import ProductForm
from .models import Order

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
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
        messages.success(request, f'Se agregó una unidad más de "{product.name}" al carrito.')
    else:
        cart[product_id_str] = {
            'quantity': 1,
            'price': str(product.price)
        }
        messages.success(request, f'"{product.name}" fue agregado a tu carrito.')
    request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def view_cart(request):
    cart = request.session.get('cart', {})
    
    cart_items = []
    total_price = 0

    for product_id_str, item_data in cart.items():
        try:
            product = get_object_or_404(Product, pk=product_id_str)

            quantity = item_data['quantity']
            item_price = float(item_data['price'])
            item_total = item_price * quantity

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

def send_email(request):
    return render(request, 'store/email.html') 