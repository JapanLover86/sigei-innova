from django.urls import path
from .alertas import alertas_stock_lista

from .views import (
    ajuste_inventario,
    cliente_crear,
    cliente_desactivar,
    cliente_editar,
    cliente_lista,
    entrada_crear,
    inventario_lista,
    kardex_lista,
    proveedor_crear,
    proveedor_desactivar,
    proveedor_editar,
    proveedor_lista,
    salida_crear,
    stock_inicial,
    bitacora_lista,
)

urlpatterns = [
    path("", inventario_lista, name="inventario_lista"),
    path("stock-inicial/", stock_inicial, name="stock_inicial"),
    path("entradas/nueva/", entrada_crear, name="entrada_crear"),
    path("salidas/nueva/", salida_crear, name="salida_crear"),
    path("ajustes/nuevo/", ajuste_inventario, name="ajuste_inventario"),
    path("kardex/", kardex_lista, name="kardex_lista"),
    path("bitacora/", bitacora_lista, name="bitacora_lista"),
    path("alertas/", alertas_stock_lista, name="alertas_stock_lista"),

    path("proveedores/", proveedor_lista, name="proveedor_lista"),
    path("proveedores/nuevo/", proveedor_crear, name="proveedor_crear"),
    path(
        "proveedores/<int:id_proveedor>/editar/",
        proveedor_editar,
        name="proveedor_editar",
    ),
    path(
        "proveedores/<int:id_proveedor>/desactivar/",
        proveedor_desactivar,
        name="proveedor_desactivar",
    ),

    path("clientes/", cliente_lista, name="cliente_lista"),
    path("clientes/nuevo/", cliente_crear, name="cliente_crear"),
    path(
        "clientes/<int:id_cliente>/editar/",
        cliente_editar,
        name="cliente_editar",
    ),
    path(
        "clientes/<int:id_cliente>/desactivar/",
        cliente_desactivar,
        name="cliente_desactivar",
    ),
]