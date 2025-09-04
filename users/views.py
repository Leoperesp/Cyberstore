from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth import authenticate, login

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)  
                return redirect('store:home')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)  
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('store:home')

def admin_panel(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return redirect('users:login')
    return render(request, 'admin/admin_panel.html')

def manage_users(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return redirect('users:login')
    users = CustomUserCreationForm.Meta.model.objects.all()
    return render(request, 'admin/manage_users.html', {'users': users})

def edit_account(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomUserCreationForm(instance=request.user)
    return render(request, 'accounts/edit.html', {'form': form})

def delete_account(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            request.user.delete()
        return redirect('home')
    return render(request, 'accounts/delete_account.html')