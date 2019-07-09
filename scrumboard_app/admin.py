from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ScrumUser

admin.site.register(ScrumUser, UserAdmin)