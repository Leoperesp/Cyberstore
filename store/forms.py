from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'stock', 'image', 'is_available', 'description', 'is_offered', 'offer_price']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'step': '1'}),
            'offer_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class OrderForm(forms.Form):
    model = Product
    fields = ['name', 'document_number', 'shipping_address', 'payment_method', 'is_paid', 'status']
    widgets = {
        'payment_method': forms.Select(choices=[
            ('credit_card', 'Tarjeta de Crédito'),
            ('paypal', 'PayPal'),
            ('cash', 'Efectivo')
        ])
    }
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['document_number'].widget.attrs['readonly'] = True
        self.fields['shipping_address'].widget.attrs['readonly'] = True
        self.fields['payment_method'].widget.attrs['readonly'] = True
        self.fields['is_paid'].widget.attrs['readonly'] = True
        self.fields['status'].widget.attrs['readonly'] = True

