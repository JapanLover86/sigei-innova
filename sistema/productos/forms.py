from django import forms

from .models import Producto


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
        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-control"

        self.fields["categoria"].widget.attrs["class"] = "form-select"
        self.fields["marca"].widget.attrs["class"] = "form-select"
        self.fields["estado"].widget.attrs["class"] = "form-check-input"