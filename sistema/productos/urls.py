from django.urls import path

from .views import producto_crear, producto_lista

urlpatterns = [
    path("", producto_lista, name="producto_lista"),
    path("nuevo/", producto_crear, name="producto_crear"),
]