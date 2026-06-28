from django import forms

from .models import Categoria, Marca, Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto

        fields = [
            "categoria",
            "marca",
            "codigo",
            "nombre",
            "descripcion",
            "unidad",
            "precio_compra",
            "precio_venta",
            "stock_minimo",
            "stock_actual",
            "estado",
        ]

        widgets = {
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)

        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-control"

        self.fields["categoria"].widget.attrs["class"] = "form-select"
        self.fields["marca"].widget.attrs["class"] = "form-select"
        self.fields["estado"].widget.attrs["class"] = "form-check-input"

        # Solo el Administrador puede modificar el estado.
        if usuario and hasattr(usuario, "perfil"):
            if usuario.perfil.rol != "ADMIN":
                self.fields.pop("estado")


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria

        fields = [
            "nombre",
            "descripcion",
            "estado",
        ]

        widgets = {
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)

        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-control"

        self.fields["estado"].widget.attrs["class"] = "form-check-input"

        # El almacenero crea/edita, pero no activa o desactiva.
        if usuario and hasattr(usuario, "perfil"):
            if usuario.perfil.rol != "ADMIN":
                self.fields.pop("estado")


class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca

        fields = [
            "nombre",
            "descripcion",
            "estado",
        ]

        widgets = {
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)

        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-control"

        self.fields["estado"].widget.attrs["class"] = "form-check-input"

        # El almacenero crea/edita, pero no activa o desactiva.
        if usuario and hasattr(usuario, "perfil"):
            if usuario.perfil.rol != "ADMIN":
                self.fields.pop("estado")