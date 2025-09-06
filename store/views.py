from django.shortcuts import render, redirect
from .models import Product  # Asegúrate de que este es el nombre de tu modelo de producto
from .forms import ProductForm

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
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        if 'image' in request.FILES:
            product.image = request.FILES.get('image') 
        product.is_available = request.POST.get('is_available') == 'on'
        product.description = request.POST.get('description')
        product.is_offered = request.POST.get('is_offered') == 'on'
        product.offer_price = request.POST.get('offer_price') if product.is_offered else None
        product.save()
        return redirect('store:manage_products')
    return render(request, 'store/edit_product.html', {'product': product})

def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('store:manage_products')