from django.contrib import admin
from .models import Contract
from django.contrib.auth.admin import UserAdmin

# Register your models here.


admin.site.register(Contract)