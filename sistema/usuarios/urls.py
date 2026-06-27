from django.urls import path

from .views import InicioSesionView, cerrar_sesion, dashboard_inicio

urlpatterns = [
    path("", InicioSesionView.as_view(), name="login"),
    path("dashboard/", dashboard_inicio, name="dashboard_inicio"),
    path("logout/", cerrar_sesion, name="logout"),
]