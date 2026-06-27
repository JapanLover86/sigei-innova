from django.conf import settings
from django.db import models

# Create your models here.
class PerfilUsuario(models.Model):
    ROL_CHOICES = [
        ("ADMIN", "Administrador"),
        ("GERENTE", "Gerente"),
        ("ALMACENERO", "Almacenero"),
        ("VENDEDOR", "Vendedor"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="VENDEDOR")
    telefono = models.CharField(max_length=30, blank=True, null=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    usa_google = models.BooleanField(default=False)
    mfa_activo = models.BooleanField(default=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"