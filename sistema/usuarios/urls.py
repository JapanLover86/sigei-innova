from django.urls import path

from .views import (
    InicioSesionView,
    cerrar_sesion,
    dashboard_inicio,
    usuario_cambiar_estado,
    usuario_crear,
    usuario_editar,
    usuario_lista,
)

urlpatterns = [
    path("", InicioSesionView.as_view(), name="login"),
    path("dashboard/", dashboard_inicio, name="dashboard_inicio"),
    path("logout/", cerrar_sesion, name="logout"),

    path("usuarios/", usuario_lista, name="usuario_lista"),
    path("usuarios/nuevo/", usuario_crear, name="usuario_crear"),
    path(
        "usuarios/<int:id_usuario>/editar/",
        usuario_editar,
        name="usuario_editar",
    ),
    path(
        "usuarios/<int:id_usuario>/estado/",
        usuario_cambiar_estado,
        name="usuario_cambiar_estado",
    ),
]