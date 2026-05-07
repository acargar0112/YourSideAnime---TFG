from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "anime", "creado")
    list_filter = ("creado",)
    search_fields = ("user__username", "anime__titulo", "texto")
    readonly_fields = ("creado",)
    fieldsets = (
        ("Información de la reseña", {
            "fields": ("user", "anime", "texto")
        }),
        ("Metadatos", {
            "fields": ("creado",),
            "classes": ("collapse",),
        }),
    )
