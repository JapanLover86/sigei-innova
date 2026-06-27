from django.contrib import admin

from .models import Categoria, Marca, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id_categoria", "nombre", "estado")
    search_fields = ("nombre",)
    list_filter = ("estado",)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("id_marca", "nombre", "estado")
    search_fields = ("nombre",)
    list_filter = ("estado",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "categoria",
        "marca",
        "stock_actual",
        "stock_minimo",
        "precio_venta",
        "estado",
    )

    search_fields = ("codigo", "nombre")
    list_filter = ("categoria", "marca", "estado")