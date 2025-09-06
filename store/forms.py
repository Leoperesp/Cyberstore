from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'image', 'is_available', 'description', 'is_offered', 'offer_price']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'step': '1'}),
            'offer_price': forms.NumberInput(attrs={'step': '0.01'}),
        }