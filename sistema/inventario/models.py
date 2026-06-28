from django.db import models

from productos.models import Producto


class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    correo = models.CharField(max_length=150, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "proveedores"

    def __str__(self):
        return self.nombre
    

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    dni_ruc = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    correo = models.CharField(max_length=150, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "clientes"

    def __str__(self):
        return self.nombre


class Entrada(models.Model):
    id_entrada = models.AutoField(primary_key=True)

    proveedor = models.ForeignKey(
        Proveedor,
        db_column="id_proveedor",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="entradas",
    )

    id_usuario = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=50, default="COMPRA")
    observacion = models.CharField(max_length=255, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "entradas"

    def __str__(self):
        return f"Entrada #{self.id_entrada}"


class DetalleEntrada(models.Model):
    id_detalle_entrada = models.AutoField(primary_key=True)

    entrada = models.ForeignKey(
        Entrada,
        db_column="id_entrada",
        on_delete=models.DO_NOTHING,
        related_name="detalles",
    )

    producto = models.ForeignKey(
        Producto,
        db_column="id_producto",
        on_delete=models.DO_NOTHING,
        related_name="detalles_entrada",
    )

    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=25, decimal_places=4)

    class Meta:
        managed = False
        db_table = "detalle_entrada"


class Salida(models.Model):
    id_salida = models.AutoField(primary_key=True)

    id_cliente = models.IntegerField(blank=True, null=True)
    id_usuario = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=50, default="VENTA")
    observacion = models.CharField(max_length=255, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "salidas"

    def __str__(self):
        return f"Salida #{self.id_salida}"


class DetalleSalida(models.Model):
    id_detalle_salida = models.AutoField(primary_key=True)

    salida = models.ForeignKey(
        Salida,
        db_column="id_salida",
        on_delete=models.DO_NOTHING,
        related_name="detalles",
    )

    producto = models.ForeignKey(
        Producto,
        db_column="id_producto",
        on_delete=models.DO_NOTHING,
        related_name="detalles_salida",
    )

    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=25, decimal_places=4)

    class Meta:
        managed = False
        db_table = "detalle_salida"


class MovimientoStock(models.Model):
    id_movimiento = models.AutoField(primary_key=True)

    producto = models.ForeignKey(
        Producto,
        db_column="id_producto",
        on_delete=models.DO_NOTHING,
        related_name="movimientos_stock",
    )

    id_usuario = models.IntegerField()
    tipo_movimiento = models.CharField(max_length=30)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    stock_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "movimientos_stock"

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.producto.nombre}"