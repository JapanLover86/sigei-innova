from django.urls import path

from .views import (
    producto_crear,
    producto_desactivar,
    producto_editar,
    producto_lista,
)

urlpatterns = [
    path("", producto_lista, name="producto_lista"),
    path("nuevo/", producto_crear, name="producto_crear"),
    path("<int:id_producto>/editar/", producto_editar, name="producto_editar"),
    path(
        "<int:id_producto>/desactivar/",
        producto_desactivar,
        name="producto_desactivar",
    ),
]