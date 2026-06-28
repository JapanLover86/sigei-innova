from django.urls import path

from .views import (
    categoria_crear,
    categoria_desactivar,
    categoria_editar,
    categoria_lista,
    marca_crear,
    marca_desactivar,
    marca_editar,
    marca_lista,
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

    path("categorias/", categoria_lista, name="categoria_lista"),
    path("categorias/nueva/", categoria_crear, name="categoria_crear"),
    path(
        "categorias/<int:id_categoria>/editar/",
        categoria_editar,
        name="categoria_editar",
    ),
    path(
        "categorias/<int:id_categoria>/desactivar/",
        categoria_desactivar,
        name="categoria_desactivar",
    ),

    path("marcas/", marca_lista, name="marca_lista"),
    path("marcas/nueva/", marca_crear, name="marca_crear"),
    path(
        "marcas/<int:id_marca>/editar/",
        marca_editar,
        name="marca_editar",
    ),
    path(
        "marcas/<int:id_marca>/desactivar/",
        marca_desactivar,
        name="marca_desactivar",
    ),
]