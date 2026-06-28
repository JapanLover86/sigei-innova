from django.urls import path

from .views import prediccion_inicio

urlpatterns = [
    path("", prediccion_inicio, name="prediccion_inicio"),
]