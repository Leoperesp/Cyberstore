
from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='products'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contact/escribenos/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    
    # ... URLs de carrito, checkout, etc.
]