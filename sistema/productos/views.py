from django.contrib import messages
from django.shortcuts import redirect, render

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
        formulario = ProductoForm(request.POST)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto registrado correctamente.")
            return redirect("producto_lista")
    else:
        formulario = ProductoForm()

    return render(
        request,
        "productos/formulario.html",
        {
            "formulario": formulario,
            "titulo": "Registrar producto",
        },
    )