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
    path('manage_orders/', views.manage_orders, name='manage_orders'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/cash/', views.cash_payment_view, name='checkout_cash'),
    path('checkout/cash/process/', views.process_cash_payment, name='process_cash_payment'),
    path('email/', views.send_email, name='email'),
]