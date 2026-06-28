from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import PerfilUsuario


Usuario = get_user_model()


class UsuarioSistemaForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: almacen_01",
            }
        ),
    )

    first_name = forms.CharField(
        label="Nombres",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: Carlos",
            }
        ),
    )

    last_name = forms.CharField(
        label="Apellidos",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: Pérez Huamán",
            }
        ),
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "correo@empresa.com",
            }
        ),
    )

    rol = forms.ChoiceField(
        label="Rol del sistema",
        choices=PerfilUsuario.ROL_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    telefono = forms.CharField(
        label="Teléfono",
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: 999888777",
            }
        ),
    )

    id_usuario_sistema = forms.IntegerField(
        label="ID de usuario SQL Server",
        required=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Opcional",
            }
        ),
    )

    estado = forms.BooleanField(
        label="Cuenta activa",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Mínimo 8 caracteres",
            }
        ),
    )

    def __init__(self, *args, usuario_obj=None, **kwargs):
        self.usuario_obj = usuario_obj
        super().__init__(*args, **kwargs)

        if usuario_obj:
            perfil = getattr(usuario_obj, "perfil", None)

            self.initial.update(
                {
                    "username": usuario_obj.username,
                    "first_name": usuario_obj.first_name,
                    "last_name": usuario_obj.last_name,
                    "email": usuario_obj.email,
                    "estado": usuario_obj.is_active,
                    "rol": perfil.rol if perfil else "VENDEDOR",
                    "telefono": perfil.telefono if perfil else "",
                    "id_usuario_sistema": (
                        perfil.id_usuario_sistema if perfil else None
                    ),
                }
            )

            self.fields["password"].help_text = (
                "Déjalo vacío para conservar la contraseña actual."
            )
        else:
            self.fields["password"].required = True
            self.fields["password"].help_text = (
                "Usa una contraseña de al menos 8 caracteres."
            )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        usuarios = Usuario.objects.filter(username=username)

        if self.usuario_obj:
            usuarios = usuarios.exclude(pk=self.usuario_obj.pk)

        if usuarios.exists():
            raise ValidationError("Este nombre de usuario ya está registrado.")

        return username

    def clean_password(self):
        password = self.cleaned_data.get("password", "")

        if not self.usuario_obj and len(password) < 8:
            raise ValidationError(
                "La contraseña debe tener al menos 8 caracteres."
            )

        if self.usuario_obj and password and len(password) < 8:
            raise ValidationError(
                "La nueva contraseña debe tener al menos 8 caracteres."
            )

        return password

    def clean_id_usuario_sistema(self):
        id_usuario_sistema = self.cleaned_data.get("id_usuario_sistema")

        if not id_usuario_sistema:
            return None

        perfiles = PerfilUsuario.objects.filter(
            id_usuario_sistema=id_usuario_sistema
        )

        if self.usuario_obj:
            perfiles = perfiles.exclude(usuario=self.usuario_obj)

        if perfiles.exists():
            raise ValidationError(
                "Este ID de usuario SQL Server ya está asociado a otra cuenta."
            )

        return id_usuario_sistema