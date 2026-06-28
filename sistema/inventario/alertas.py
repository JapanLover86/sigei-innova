from django.db.models import F
from django.shortcuts import render

from productos.models import Producto
from usuarios.decorators import rol_requerido


@rol_requerido("ADMIN", "ALMACENERO", "GERENTE")
def alertas_stock_lista(request):
    productos_activos = Producto.objects.filter(
        estado=True,
    ).select_related(
        "categoria",
        "marca",
    )

    productos_sin_stock = productos_activos.filter(
        stock_actual__lte=0,
    ).order_by("nombre")

    productos_stock_bajo = productos_activos.filter(
        stock_actual__gt=0,
        stock_actual__lte=F("stock_minimo"),
    ).order_by("stock_actual", "nombre")

    return render(
        request,
        "inventario/alertas_stock.html",
        {
            "productos_sin_stock": productos_sin_stock,
            "productos_stock_bajo": productos_stock_bajo,
        },
    )