
from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='products'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    # ... URLs de carrito, checkout, etc.
]