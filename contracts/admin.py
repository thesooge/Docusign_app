from django.contrib import admin
from .models import Contract, DocusignProfile
from django.contrib.auth.admin import UserAdmin

# Register your models here.


admin.site.register(Contract)
admin.site.register(DocusignProfile)