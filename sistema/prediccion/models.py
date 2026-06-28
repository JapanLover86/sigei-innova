from django.db import models

from productos.models import Producto


class PrediccionDemanda(models.Model):
    id_prediccion = models.AutoField(primary_key=True)

    producto = models.ForeignKey(
        Producto,
        db_column="id_producto",
        on_delete=models.DO_NOTHING,
        related_name="predicciones_demanda",
    )

    fecha_prediccion = models.DateTimeField(auto_now_add=True)
    periodo = models.CharField(max_length=50)

    demanda_predicha = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    metodo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    observacion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "predicciones_demanda"

    def __str__(self):
        return f"{self.producto.nombre} - {self.fecha_prediccion:%d/%m/%Y}"