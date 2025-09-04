from django.shortcuts import render
from .models import Product  # Asegúrate de que este es el nombre de tu modelo de producto

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
