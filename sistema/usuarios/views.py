from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


class InicioSesionView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard_inicio(request):
    from django.db.models import F
    from django.utils import timezone

    from productos.models import Producto

    perfil = getattr(request.user, "perfil", None)

    inicio_mes = timezone.now().replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    total_productos = Producto.objects.filter(estado=True).count()

    productos_stock_bajo = Producto.objects.filter(
        estado=True,
        stock_actual__lte=F("stock_minimo"),
    ).count()

    contexto = {
        "perfil": perfil,
        "rol": perfil.get_rol_display() if perfil else "Sin rol asignado",
        "total_productos": total_productos,
        "productos_stock_bajo": productos_stock_bajo,
        "entradas_mes": 0,
        "salidas_mes": 0,
        "inicio_mes": inicio_mes,
    }

    return render(request, "dashboard/inicio.html", contexto)


@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect("login")