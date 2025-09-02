from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
         name='password_reset'),
    path('edit_account/', views.edit_account, name='edit_account'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('admin_panel/', views.admin_panel, name='admin_panel'), 
]