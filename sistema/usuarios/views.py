from decimal import Decimal

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import F, Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from inventario.models import MovimientoStock, Salida
from productos.models import Producto


class InicioSesionView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard_inicio(request):
    perfil = getattr(request.user, "perfil", None)

    productos_activos = Producto.objects.filter(estado=True)

    total_productos = productos_activos.count()

    productos_sin_stock = productos_activos.filter(
        stock_actual__lte=0,
    ).order_by("nombre")

    productos_stock_bajo = productos_activos.filter(
        stock_actual__gt=0,
        stock_actual__lte=F("stock_minimo"),
    ).order_by("stock_actual", "nombre")

    total_stock_critico = productos_sin_stock.count()
    total_stock_bajo = productos_stock_bajo.count()

    valor_inventario = sum(
        (
            (producto.stock_actual or Decimal("0.00"))
            * (producto.precio_compra or Decimal("0.00"))
        )
        for producto in productos_activos.only(
            "stock_actual",
            "precio_compra",
        )
    )

    hoy = timezone.localdate()

    ventas_hoy = Salida.objects.filter(
        estado=True,
        fecha__date=hoy,
    ).aggregate(
        total=Sum("total"),
    )["total"] or Decimal("0.00")

    movimientos_recientes = MovimientoStock.objects.select_related(
        "producto",
    ).order_by(
        "-fecha",
        "-id_movimiento",
    )[:8]

    alertas_stock = list(productos_sin_stock) + list(productos_stock_bajo)

    return render(
        request,
        "dashboard/inicio.html",
        {
            "perfil": perfil,
            "rol": perfil.get_rol_display() if perfil else "Sin rol asignado",
            "total_productos": total_productos,
            "total_stock_critico": total_stock_critico,
            "total_stock_bajo": total_stock_bajo,
            "valor_inventario": valor_inventario,
            "ventas_hoy": ventas_hoy,
            "productos_sin_stock": productos_sin_stock,
            "productos_stock_bajo": productos_stock_bajo,
            "alertas_stock": alertas_stock,
            "movimientos_recientes": movimientos_recientes,
        },
    )


@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect("login")