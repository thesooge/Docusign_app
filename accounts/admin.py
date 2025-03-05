from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .forms import RegisterForm

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = RegisterForm

    list_display = ['username','email']


admin.site.register(CustomUser, CustomUserAdmin)   