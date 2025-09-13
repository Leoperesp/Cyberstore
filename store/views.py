from django.shortcuts import render, redirect
from .models import Product  # Asegúrate de que este es el nombre de tu modelo de producto
from .forms import ProductForm
from .models import Order

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

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
    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {'name': product.name, 'price': str(product.price), 'quantity': 1}
    request.session['cart'] = cart
    return redirect('store:product_list')

def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    return render(request, 'store/cart.html', {'cart': cart, 'total': total})

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