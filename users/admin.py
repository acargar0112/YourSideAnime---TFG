from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "date_joined")
    search_fields = ("username", "email")
    fieldsets = (
        ("Credenciales", {
            "fields": ("username", "password")
        }),
        ("Información personal", {
            "fields": ("first_name", "last_name", "email", "bio","avatar")
        }),
    )
