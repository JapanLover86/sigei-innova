
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from inventario.auditoria import registrar_bitacora
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from usuarios.decorators import rol_requerido

from .forms import UsuarioSistemaForm
from .models import PerfilUsuario

from inventario.models import DetalleSalida, MovimientoStock, Salida
from productos.models import Producto

Usuario = get_user_model()


class InicioSesionView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        respuesta = super().form_valid(form)

        registrar_bitacora(
            self.request,
            accion="Inicio de sesión",
            modulo="Seguridad",
            descripcion=(
                f"El usuario '{self.request.user.username}' "
                f"inició sesión en el sistema."
            ),
        )

        return respuesta

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

    # -----------------------------------------
    # Ventas de los últimos 7 días
    # -----------------------------------------
    fecha_inicio = hoy - timedelta(days=6)

    ventas_ultimos_dias = Salida.objects.filter(
        estado=True,
        fecha__date__gte=fecha_inicio,
    ).values(
        "fecha__date",
    ).annotate(
        total=Sum("total"),
    )

    ventas_por_fecha = {
        item["fecha__date"]: float(item["total"] or 0)
        for item in ventas_ultimos_dias
    }

    etiquetas_ventas = []
    datos_ventas = []

    for indice in range(7):
        fecha = fecha_inicio + timedelta(days=indice)

        etiquetas_ventas.append(
            fecha.strftime("%d/%m")
        )

        datos_ventas.append(
            ventas_por_fecha.get(fecha, 0)
        )

    # -----------------------------------------
    # Productos más vendidos últimos 30 días
    # -----------------------------------------
    fecha_ventas_30 = timezone.now() - timedelta(days=30)

    productos_mas_vendidos = (
        DetalleSalida.objects.filter(
            salida__estado=True,
            salida__fecha__gte=fecha_ventas_30,
        )
        .values(
            "producto__nombre",
        )
        .annotate(
            total_vendido=Sum("cantidad"),
        )
        .order_by("-total_vendido")[:5]
    )

    etiquetas_productos = [
        item["producto__nombre"]
        for item in productos_mas_vendidos
    ]

    datos_productos = [
        float(item["total_vendido"] or 0)
        for item in productos_mas_vendidos
    ]

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
            "etiquetas_ventas": etiquetas_ventas,
            "datos_ventas": datos_ventas,
            "etiquetas_productos": etiquetas_productos,
            "datos_productos": datos_productos,
        },
    )


@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect("login")


@rol_requerido("ADMIN")
def usuario_lista(request):
    usuarios = (
        Usuario.objects.select_related("perfil")
        .order_by("username")
    )

    return render(
        request,
        "usuarios/lista.html",
        {
            "usuarios": usuarios,
        },
    )


@rol_requerido("ADMIN")
def usuario_crear(request):
    if request.method == "POST":
        formulario = UsuarioSistemaForm(request.POST)

        if formulario.is_valid():
            with transaction.atomic():
                usuario = Usuario.objects.create_user(
                    username=formulario.cleaned_data["username"],
                    password=formulario.cleaned_data["password"],
                    first_name=formulario.cleaned_data["first_name"],
                    last_name=formulario.cleaned_data["last_name"],
                    email=formulario.cleaned_data["email"],
                )

                usuario.is_active = formulario.cleaned_data["estado"]
                usuario.save(update_fields=["is_active"])

                perfil, _ = PerfilUsuario.objects.get_or_create(
                    usuario=usuario
                )

                perfil.rol = formulario.cleaned_data["rol"]
                perfil.telefono = formulario.cleaned_data["telefono"]
                perfil.id_usuario_sistema = formulario.cleaned_data[
                    "id_usuario_sistema"
                ]
                perfil.estado = formulario.cleaned_data["estado"]
                perfil.save()

            messages.success(
                request,
                f"El usuario '{usuario.username}' fue creado correctamente.",
            )

            return redirect("usuario_lista")
    else:
        formulario = UsuarioSistemaForm()

    return render(
        request,
        "usuarios/formulario.html",
        {
            "formulario": formulario,
            "titulo": "Registrar usuario",
        },
    )


@rol_requerido("ADMIN")
def usuario_editar(request, id_usuario):
    usuario = get_object_or_404(
        Usuario.objects.select_related("perfil"),
        pk=id_usuario,
    )

    if request.method == "POST":
        formulario = UsuarioSistemaForm(
            request.POST,
            usuario_obj=usuario,
        )

        if formulario.is_valid():
            with transaction.atomic():
                usuario.username = formulario.cleaned_data["username"]
                usuario.first_name = formulario.cleaned_data["first_name"]
                usuario.last_name = formulario.cleaned_data["last_name"]
                usuario.email = formulario.cleaned_data["email"]
                usuario.is_active = formulario.cleaned_data["estado"]

                nueva_password = formulario.cleaned_data["password"]

                if nueva_password:
                    usuario.set_password(nueva_password)

                usuario.save()

                perfil, _ = PerfilUsuario.objects.get_or_create(
                    usuario=usuario
                )

                perfil.rol = formulario.cleaned_data["rol"]
                perfil.telefono = formulario.cleaned_data["telefono"]
                perfil.id_usuario_sistema = formulario.cleaned_data[
                    "id_usuario_sistema"
                ]
                perfil.estado = formulario.cleaned_data["estado"]
                perfil.save()

            messages.success(
                request,
                f"El usuario '{usuario.username}' fue actualizado.",
            )

            return redirect("usuario_lista")
    else:
        formulario = UsuarioSistemaForm(usuario_obj=usuario)

    return render(
        request,
        "usuarios/formulario.html",
        {
            "formulario": formulario,
            "titulo": f"Editar usuario: {usuario.username}",
        },
    )


@rol_requerido("ADMIN")
def usuario_cambiar_estado(request, id_usuario):
    usuario = get_object_or_404(Usuario, pk=id_usuario)

    if request.method == "POST":
        if usuario == request.user:
            messages.error(
                request,
                "No puedes desactivar tu propia cuenta desde esta pantalla.",
            )
            return redirect("usuario_lista")

        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=["is_active"])

        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)
        perfil.estado = usuario.is_active
        perfil.save(update_fields=["estado"])

        estado_texto = "activado" if usuario.is_active else "desactivado"

        messages.success(
            request,
            f"El usuario '{usuario.username}' fue {estado_texto}.",
        )

    return redirect("usuario_lista")