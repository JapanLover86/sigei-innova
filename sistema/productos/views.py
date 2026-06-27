from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from usuarios.decorators import rol_requerido

from .forms import ProductoForm
from .models import Producto


@rol_requerido("ADMIN", "ALMACENERO")
def producto_lista(request):
    productos = Producto.objects.select_related("categoria", "marca").all()

    return render(
        request,
        "productos/lista.html",
        {
            "productos": productos,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def producto_crear(request):
    if request.method == "POST":
        formulario = ProductoForm(request.POST, usuario=request.user)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto registrado correctamente.")
            return redirect("producto_lista")
    else:
        formulario = ProductoForm(usuario=request.user)

    return render(
        request,
        "productos/formulario.html",
        {
            "formulario": formulario,
            "titulo": "Registrar producto",
        },
    )

@rol_requerido("ADMIN", "ALMACENERO")
def producto_editar(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)

    if request.method == "POST":
        formulario = ProductoForm(request.POST, instance=producto, usuario=request.user)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("producto_lista")
    else:
        formulario = ProductoForm(instance=producto, usuario=request.user)

    return render(
        request,
        "productos/formulario.html",
        {
            "formulario": formulario,
            "titulo": "Editar producto",
        },
    )

@rol_requerido("ADMIN")
def producto_desactivar(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)

    if request.method == "POST":
        producto.estado = False
        producto.save(update_fields=["estado"])

        messages.success(
            request,
            f"El producto '{producto.nombre}' fue desactivado correctamente.",
        )

    return redirect("producto_lista")