from django.contrib import admin
from .models import CustomUser 

@admin.register(CustomUser)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'address', 'phone_number')
    search_fields = ('user__username', 'address')