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
    path('manage_products/', views.manage_products, name='manage_products'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    # path('cart/', views.cart, name='cart'),  # Implementación futura
    # path('checkout/', views.checkout, name='checkout'),  # Implementación futura
]