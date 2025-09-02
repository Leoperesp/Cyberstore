from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    document_number = forms.CharField(max_length=20)
    address = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = CustomUser
        fields = ('username', 'document_number', 'email', 'address', 'phone_number', 'password1', 'password2')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
           
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)
    