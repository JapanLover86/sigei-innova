from django.contrib import admin
from .models import PerfilUsuario

# Register your models here.
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol", "telefono", "usa_google", "mfa_activo", "estado")
    list_filter = ("rol", "usa_google", "mfa_activo", "estado")
    search_fields = ("usuario__username", "usuario__email", "telefono")