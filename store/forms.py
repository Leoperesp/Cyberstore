from django import forms
from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'stock', 'image', 'is_available', 'description', 'is_offered', 'offer_price']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'step': '1'}),
            'offer_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class OrderForm(forms.ModelForm): 
    class Meta:
        model = Order 
        fields = ['document_number', 'shipping_address', 'payment_method', 'is_paid', 'status']
        widgets = {
            'payment_method': forms.Select(choices=[
                ('credit_card', 'Tarjeta de Crédito'),
                ('paypal', 'PayPal'),
                ('cash', 'Efectivo')
            ])
        }

class ShippingForm(forms.Form):
    name = forms.CharField(max_length=100, label='Nombre Completo', 
                           widget=forms.TextInput(attrs={'placeholder': 'Nombre Completo'}))
    address = forms.CharField(max_length=255, label='Dirección de Entrega', 
                              widget=forms.TextInput(attrs={'placeholder': 'Dirección de envío'}))
    phone = forms.CharField(max_length=20, label='Número de Teléfono', 
                            widget=forms.TextInput(attrs={'placeholder': 'Número de teléfono'}))
    
