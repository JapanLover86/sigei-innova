from django.urls import path

from .views import (
    reporte_inicio,
    inventario_pdf,
    inventario_excel,
    kardex_pdf,
    kardex_excel,
)

urlpatterns = [
    path("", reporte_inicio, name="reporte_inicio"),

    path(
        "inventario/pdf/",
        inventario_pdf,
        name="inventario_pdf",
    ),
    path(
        "inventario/excel/",
        inventario_excel,
        name="inventario_excel",
    ),

    path(
        "kardex/pdf/",
        kardex_pdf,
        name="kardex_pdf",
    ),
    path(
        "kardex/excel/",
        kardex_excel,
        name="kardex_excel",
    ),
]