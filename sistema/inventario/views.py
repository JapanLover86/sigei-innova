from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Bitacora, Cliente, MovimientoStock, Proveedor
from productos.models import Producto
from usuarios.decorators import rol_requerido
from .auditoria import registrar_bitacora
from django.db.models import Q

from .forms import (
    AjusteInventarioForm,
    ClienteForm,
    EntradaForm,
    KardexFiltroForm,
    ProveedorForm,
    SalidaForm,
    StockInicialForm,
)

from .services import (
    registrar_ajuste_inventario,
    registrar_entrada,
    registrar_salida,
    registrar_stock_inicial,
)

@rol_requerido("ADMIN", "ALMACENERO")
def inventario_lista(request):
    productos = Producto.objects.filter(
        estado=True
    ).select_related(
        "categoria",
        "marca",
    ).order_by(
        "nombre"
    )

    return render(
        request,
        "inventario/lista_stock.html",
        {
            "productos": productos,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def stock_inicial(request):
    perfil = getattr(request.user, "perfil", None)

    if not perfil or not perfil.id_usuario_sistema:
        messages.error(
            request,
            "Tu usuario no está vinculado al usuario operativo de SQL Server.",
        )
        return redirect("inventario_lista")

    if request.method == "POST":
        formulario = StockInicialForm(request.POST)

        if formulario.is_valid():
            producto = formulario.cleaned_data["producto"]
            cantidad = formulario.cleaned_data["cantidad"]
            observacion = formulario.cleaned_data["observacion"]

            registrar_stock_inicial(
                producto_id=producto.id_producto,
                cantidad=cantidad,
                id_usuario_sistema=perfil.id_usuario_sistema,
                observacion=observacion,
            )

            registrar_bitacora(
                request,
                accion="Registro de stock inicial",
                modulo="Inventario",
                descripcion=(
                    f"Producto: {producto.nombre}; "
                    f"stock físico registrado: {cantidad}."
                ),
            )

            messages.success(
                request,
                f"Stock inicial registrado correctamente para "
                f"'{producto.nombre}'.",
            )

            return redirect("inventario_lista")
    else:
        formulario = StockInicialForm()

    return render(
        request,
        "inventario/stock_inicial.html",
        {
            "formulario": formulario,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def entrada_crear(request):
    perfil = getattr(request.user, "perfil", None)

    if not perfil or not perfil.id_usuario_sistema:
        messages.error(
            request,
            "Tu usuario no está vinculado al usuario operativo de SQL Server.",
        )
        return redirect("inventario_lista")

    if request.method == "POST":
        formulario = EntradaForm(request.POST)

        if formulario.is_valid():
            proveedor = formulario.cleaned_data["proveedor"]
            producto = formulario.cleaned_data["producto"]
            cantidad = formulario.cleaned_data["cantidad"]
            precio_unitario = formulario.cleaned_data["precio_unitario"]
            observacion = formulario.cleaned_data["observacion"]

            entrada = registrar_entrada(
                proveedor=proveedor,
                producto_id=producto.id_producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                id_usuario_sistema=perfil.id_usuario_sistema,
                observacion=observacion,
            )

            registrar_bitacora(
                request,
                accion="Registro de entrada",
                modulo="Entradas",
                descripcion=(
                    f"Entrada #{entrada.id_entrada}; "
                    f"producto: {producto.nombre}; "
                    f"cantidad: {cantidad}; "
                    f"precio unitario: S/ {precio_unitario}."
                ),
            )

            messages.success(
                request,
                f"Entrada #{entrada.id_entrada} registrada correctamente.",
            )

            return redirect("inventario_lista")
    else:
        formulario = EntradaForm()

    return render(
        request,
        "inventario/entrada_formulario.html",
        {
            "formulario": formulario,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO", "VENDEDOR")
def salida_crear(request):
    perfil = getattr(request.user, "perfil", None)

    if not perfil or not perfil.id_usuario_sistema:
        messages.error(
            request,
            "Tu usuario no está vinculado al usuario operativo de SQL Server.",
        )
        return redirect("inventario_lista")

    if request.method == "POST":
        formulario = SalidaForm(request.POST)

        if formulario.is_valid():
            cliente = formulario.cleaned_data["cliente"]
            producto = formulario.cleaned_data["producto"]
            cantidad = formulario.cleaned_data["cantidad"]
            precio_unitario = formulario.cleaned_data["precio_unitario"]
            observacion = formulario.cleaned_data["observacion"]

            try:
                salida = registrar_salida(
                    cliente=cliente,
                    producto_id=producto.id_producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    id_usuario_sistema=perfil.id_usuario_sistema,
                    observacion=observacion,
                )

                registrar_bitacora(
                    request,
                    accion="Registro de salida",
                    modulo="Salidas",
                    descripcion=(
                        f"Salida #{salida.id_salida}; "
                        f"producto: {producto.nombre}; "
                        f"cantidad: {cantidad}; "
                        f"precio unitario: S/ {precio_unitario}."
                    ),
                )

                messages.success(
                    request,
                    f"Salida #{salida.id_salida} registrada correctamente.",
                )

                return redirect("inventario_lista")

            except ValueError as error:
                formulario.add_error("cantidad", str(error))
    else:
        formulario = SalidaForm()

    return render(
        request,
        "inventario/salida_formulario.html",
        {
            "formulario": formulario,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO", "GERENTE")
def kardex_lista(request):
    formulario = KardexFiltroForm(request.GET or None)

    movimientos = MovimientoStock.objects.select_related(
        "producto",
    ).all().order_by(
        "-fecha",
        "-id_movimiento",
    )

    if formulario.is_valid():
        producto = formulario.cleaned_data["producto"]
        fecha_inicio = formulario.cleaned_data["fecha_inicio"]
        fecha_fin = formulario.cleaned_data["fecha_fin"]

        if producto:
            movimientos = movimientos.filter(producto=producto)

        if fecha_inicio:
            movimientos = movimientos.filter(fecha__date__gte=fecha_inicio)

        if fecha_fin:
            movimientos = movimientos.filter(fecha__date__lte=fecha_fin)

    return render(
        request,
        "inventario/kardex.html",
        {
            "formulario": formulario,
            "movimientos": movimientos,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def ajuste_inventario(request):
    perfil = getattr(request.user, "perfil", None)

    if not perfil or not perfil.id_usuario_sistema:
        messages.error(
            request,
            "Tu usuario no está vinculado al usuario operativo de SQL Server.",
        )
        return redirect("inventario_lista")

    if request.method == "POST":
        formulario = AjusteInventarioForm(request.POST)

        if formulario.is_valid():
            producto = formulario.cleaned_data["producto"]
            stock_fisico = formulario.cleaned_data["stock_fisico"]
            motivo = formulario.cleaned_data["motivo"]

            try:
                producto_actualizado, diferencia = registrar_ajuste_inventario(
                    producto_id=producto.id_producto,
                    stock_fisico=stock_fisico,
                    id_usuario_sistema=perfil.id_usuario_sistema,
                    motivo=motivo,
                )

                signo = "+" if diferencia > 0 else ""

                registrar_bitacora(
                    request,
                    accion="Ajuste de inventario",
                    modulo="Inventario",
                    descripcion=(
                        f"Producto: {producto_actualizado.nombre}; "
                        f"variación: {diferencia}; "
                        f"nuevo stock: {producto_actualizado.stock_actual}; "
                        f"motivo: {motivo}"
                    ),
                )

                messages.success(
                    request,
                    f"Ajuste registrado para '{producto_actualizado.nombre}'. "
                    f"Variación: {signo}{diferencia}. "
                    f"Stock actual: {producto_actualizado.stock_actual}.",
                )

                return redirect("inventario_lista")

            except ValueError as error:
                formulario.add_error("stock_fisico", str(error))
    else:
        formulario = AjusteInventarioForm()

    return render(
        request,
        "inventario/ajuste_inventario.html",
        {
            "formulario": formulario,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def proveedor_lista(request):
    proveedores = Proveedor.objects.all().order_by("nombre")

    return render(
        request,
        "inventario/proveedores_lista.html",
        {
            "proveedores": proveedores,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def proveedor_crear(request):
    if request.method == "POST":
        formulario = ProveedorForm(
            request.POST,
            usuario=request.user,
        )

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                "Proveedor registrado correctamente.",
            )

            return redirect("proveedor_lista")
    else:
        formulario = ProveedorForm(usuario=request.user)

    return render(
        request,
        "inventario/proveedor_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Registrar proveedor",
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def proveedor_editar(request, id_proveedor):
    proveedor = get_object_or_404(
        Proveedor,
        id_proveedor=id_proveedor,
    )

    if request.method == "POST":
        formulario = ProveedorForm(
            request.POST,
            instance=proveedor,
            usuario=request.user,
        )

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                "Proveedor actualizado correctamente.",
            )

            return redirect("proveedor_lista")
    else:
        formulario = ProveedorForm(
            instance=proveedor,
            usuario=request.user,
        )

    return render(
        request,
        "inventario/proveedor_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Editar proveedor",
        },
    )


@rol_requerido("ADMIN")
def proveedor_desactivar(request, id_proveedor):
    proveedor = get_object_or_404(
        Proveedor,
        id_proveedor=id_proveedor,
    )

    if request.method == "POST":
        proveedor.estado = False
        proveedor.save(update_fields=["estado"])

        messages.success(
            request,
            f"El proveedor '{proveedor.nombre}' fue desactivado.",
        )

    return redirect("proveedor_lista")


@rol_requerido("ADMIN", "ALMACENERO", "VENDEDOR")
def cliente_lista(request):
    clientes = Cliente.objects.all().order_by("nombre")

    return render(
        request,
        "inventario/clientes_lista.html",
        {
            "clientes": clientes,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO", "VENDEDOR")
def cliente_crear(request):
    if request.method == "POST":
        formulario = ClienteForm(
            request.POST,
            usuario=request.user,
        )

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                "Cliente registrado correctamente.",
            )

            return redirect("cliente_lista")
    else:
        formulario = ClienteForm(usuario=request.user)

    return render(
        request,
        "inventario/cliente_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Registrar cliente",
        },
    )


@rol_requerido("ADMIN", "ALMACENERO", "VENDEDOR")
def cliente_editar(request, id_cliente):
    cliente = get_object_or_404(
        Cliente,
        id_cliente=id_cliente,
    )

    if request.method == "POST":
        formulario = ClienteForm(
            request.POST,
            instance=cliente,
            usuario=request.user,
        )

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                "Cliente actualizado correctamente.",
            )

            return redirect("cliente_lista")
    else:
        formulario = ClienteForm(
            instance=cliente,
            usuario=request.user,
        )

    return render(
        request,
        "inventario/cliente_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Editar cliente",
        },
    )


@rol_requerido("ADMIN")
def cliente_desactivar(request, id_cliente):
    cliente = get_object_or_404(
        Cliente,
        id_cliente=id_cliente,
    )

    if request.method == "POST":
        cliente.estado = False
        cliente.save(update_fields=["estado"])

        messages.success(
            request,
            f"El cliente '{cliente.nombre}' fue desactivado.",
        )

    return redirect("cliente_lista")


@rol_requerido("ADMIN")
def bitacora_lista(request):
    busqueda = request.GET.get("q", "").strip()

    registros = Bitacora.objects.all().order_by(
        "-fecha",
        "-id_bitacora",
    )

    if busqueda:
        registros = registros.filter(
            Q(accion__icontains=busqueda)
            | Q(modulo__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(ip_origen__icontains=busqueda)
        )

    return render(
        request,
        "inventario/bitacora.html",
        {
            "registros": registros[:200],
            "busqueda": busqueda,
        },
    )