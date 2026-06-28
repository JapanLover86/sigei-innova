from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from usuarios.decorators import rol_requerido

from .forms import CategoriaForm, MarcaForm, ProductoForm
from .models import Categoria, Marca, Producto


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


@rol_requerido("ADMIN", "ALMACENERO")
def categoria_lista(request):
    categorias = Categoria.objects.all().order_by("nombre")

    return render(
        request,
        "productos/categorias_lista.html",
        {
            "categorias": categorias,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def categoria_crear(request):
    if request.method == "POST":
        formulario = CategoriaForm(
            request.POST,
            usuario=request.user,
        )

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Categoría registrada correctamente.")
            return redirect("categoria_lista")
    else:
        formulario = CategoriaForm(usuario=request.user)

    return render(
        request,
        "productos/catalogo_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Registrar categoría",
            "volver_url": "categoria_lista",
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def categoria_editar(request, id_categoria):
    categoria = get_object_or_404(
        Categoria,
        id_categoria=id_categoria,
    )

    if request.method == "POST":
        formulario = CategoriaForm(
            request.POST,
            instance=categoria,
            usuario=request.user,
        )

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Categoría actualizada correctamente.")
            return redirect("categoria_lista")
    else:
        formulario = CategoriaForm(
            instance=categoria,
            usuario=request.user,
        )

    return render(
        request,
        "productos/catalogo_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Editar categoría",
            "volver_url": "categoria_lista",
        },
    )


@rol_requerido("ADMIN")
def categoria_desactivar(request, id_categoria):
    categoria = get_object_or_404(
        Categoria,
        id_categoria=id_categoria,
    )

    if request.method == "POST":
        categoria.estado = False
        categoria.save(update_fields=["estado"])

        messages.success(
            request,
            f"La categoría '{categoria.nombre}' fue desactivada.",
        )

    return redirect("categoria_lista")


@rol_requerido("ADMIN", "ALMACENERO")
def marca_lista(request):
    marcas = Marca.objects.all().order_by("nombre")

    return render(
        request,
        "productos/marcas_lista.html",
        {
            "marcas": marcas,
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def marca_crear(request):
    if request.method == "POST":
        formulario = MarcaForm(
            request.POST,
            usuario=request.user,
        )

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Marca registrada correctamente.")
            return redirect("marca_lista")
    else:
        formulario = MarcaForm(usuario=request.user)

    return render(
        request,
        "productos/catalogo_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Registrar marca",
            "volver_url": "marca_lista",
        },
    )


@rol_requerido("ADMIN", "ALMACENERO")
def marca_editar(request, id_marca):
    marca = get_object_or_404(
        Marca,
        id_marca=id_marca,
    )

    if request.method == "POST":
        formulario = MarcaForm(
            request.POST,
            instance=marca,
            usuario=request.user,
        )

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Marca actualizada correctamente.")
            return redirect("marca_lista")
    else:
        formulario = MarcaForm(
            instance=marca,
            usuario=request.user,
        )

    return render(
        request,
        "productos/catalogo_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Editar marca",
            "volver_url": "marca_lista",
        },
    )


@rol_requerido("ADMIN")
def marca_desactivar(request, id_marca):
    marca = get_object_or_404(
        Marca,
        id_marca=id_marca,
    )

    if request.method == "POST":
        marca.estado = False
        marca.save(update_fields=["estado"])

        messages.success(
            request,
            f"La marca '{marca.nombre}' fue desactivada.",
        )

    return redirect("marca_lista")