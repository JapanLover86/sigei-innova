from django import forms

from .models import Cliente, Proveedor
from productos.models import Producto


class StockInicialForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado=True).order_by("nombre"),
        label="Producto",
        empty_label="Seleccione un producto",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    cantidad = forms.DecimalField(
        label="Stock físico inicial",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Ejemplo: 25.00",
            }
        ),
    )

    observacion = forms.CharField(
        label="Observación",
        required=False,
        max_length=255,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ejemplo: Conteo físico inicial del almacén.",
            }
        ),
    )


class EntradaForm(forms.Form):
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(estado=True).order_by("nombre"),
        label="Proveedor",
        empty_label="Seleccione un proveedor",
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado=True).order_by("nombre"),
        label="Producto",
        empty_label="Seleccione un producto",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    cantidad = forms.DecimalField(
        label="Cantidad",
        min_value=0.01,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "Ejemplo: 10.00",
            }
        ),
    )

    precio_unitario = forms.DecimalField(
        label="Precio unitario (S/)",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Ejemplo: 15.50",
            }
        ),
    )

    observacion = forms.CharField(
        label="Observación",
        required=False,
        max_length=255,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ejemplo: Compra de mercadería para almacén.",
            }
        ),
    )


class SalidaForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado=True).order_by("nombre"),
        label="Producto",
        empty_label="Seleccione un producto",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    cantidad = forms.DecimalField(
        label="Cantidad a retirar",
        min_value=0.01,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "Ejemplo: 2.00",
            }
        ),
    )

    precio_unitario = forms.DecimalField(
        label="Precio unitario de venta (S/)",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Ejemplo: 20.00",
            }
        ),
    )

    observacion = forms.CharField(
        label="Observación",
        required=False,
        max_length=255,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ejemplo: Venta de productos al cliente.",
            }
        ),
    )


class KardexFiltroForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado=True).order_by("nombre"),
        required=False,
        empty_label="Todos los productos",
        label="Producto",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    fecha_inicio = forms.DateField(
        required=False,
        label="Desde",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )

    fecha_fin = forms.DateField(
        required=False,
        label="Hasta",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )


class AjusteInventarioForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado=True).order_by("nombre"),
        label="Producto",
        empty_label="Seleccione un producto",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    stock_fisico = forms.DecimalField(
        label="Stock físico contado",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Ejemplo: 30.00",
            }
        ),
    )

    motivo = forms.CharField(
        label="Motivo del ajuste",
        max_length=255,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": (
                    "Ejemplo: Diferencia encontrada durante "
                    "conteo físico de almacén."
                ),
            }
        ),
    )


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor

        fields = [
            "nombre",
            "ruc",
            "telefono",
            "correo",
            "direccion",
            "estado",
        ]

        widgets = {
            "direccion": forms.Textarea(
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

        # Solo el administrador puede activar o desactivar proveedores.
        if usuario and hasattr(usuario, "perfil"):
            if usuario.perfil.rol != "ADMIN":
                self.fields.pop("estado")
            

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente

        fields = [
            "nombre",
            "dni_ruc",
            "telefono",
            "correo",
            "direccion",
            "estado",
        ]

        widgets = {
            "direccion": forms.Textarea(
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

        # Solo Administración puede cambiar el estado.
        if usuario and hasattr(usuario, "perfil"):
            if usuario.perfil.rol != "ADMIN":
                self.fields.pop("estado")