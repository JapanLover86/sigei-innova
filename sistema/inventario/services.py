from decimal import Decimal

from django.db import connection, transaction
from productos.models import Producto

from .models import (
    DetalleEntrada,
    Entrada,
    MovimientoStock,
    Salida,
)

@transaction.atomic
def registrar_stock_inicial(
    *,
    producto_id,
    cantidad,
    id_usuario_sistema,
    observacion="",
):
    producto = Producto.objects.select_for_update().get(
        id_producto=producto_id
    )

    stock_anterior = producto.stock_actual or Decimal("0.00")
    stock_nuevo = Decimal(cantidad)

    producto.stock_actual = stock_nuevo
    producto.save(update_fields=["stock_actual"])

    MovimientoStock.objects.create(
        producto=producto,
        id_usuario=id_usuario_sistema,
        tipo_movimiento="ENTRADA",
        referencia="STOCK INICIAL",
        cantidad=stock_nuevo,
        stock_anterior=stock_anterior,
        stock_actual=stock_nuevo,
        observacion=observacion or "Registro de stock físico inicial.",
    )

    return producto


@transaction.atomic
def registrar_entrada(
    *,
    proveedor,
    producto_id,
    cantidad,
    precio_unitario,
    id_usuario_sistema,
    observacion="",
):
    producto = Producto.objects.select_for_update().get(
        id_producto=producto_id
    )

    stock_anterior = producto.stock_actual or Decimal("0.00")
    cantidad = Decimal(cantidad)
    precio_unitario = Decimal(precio_unitario)

    subtotal = cantidad * precio_unitario
    stock_nuevo = stock_anterior + cantidad

    entrada = Entrada.objects.create(
        proveedor=proveedor,
        id_usuario=id_usuario_sistema,
        tipo="COMPRA",
        observacion=observacion or "Registro de entrada por compra.",
        total=subtotal,
        estado=True,
    )

    # SQL Server calcula subtotal automáticamente.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO detalle_entrada (
                id_entrada,
                id_producto,
                cantidad,
                precio_unitario
            )
            VALUES (%s, %s, %s, %s)
            """,
            [
                entrada.id_entrada,
                producto.id_producto,
                cantidad,
                precio_unitario,
            ],
        )

    producto.stock_actual = stock_nuevo
    producto.precio_compra = precio_unitario
    producto.save(
        update_fields=[
            "stock_actual",
            "precio_compra",
        ]
    )

    MovimientoStock.objects.create(
        producto=producto,
        id_usuario=id_usuario_sistema,
        tipo_movimiento="ENTRADA",
        referencia=f"ENTRADA #{entrada.id_entrada}",
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_actual=stock_nuevo,
        observacion=observacion or "Entrada por compra.",
    )

    return entrada


@transaction.atomic
def registrar_salida(
    *,
    cliente,
    producto_id,
    cantidad,
    precio_unitario,
    id_usuario_sistema,
    observacion="",
):
    producto = Producto.objects.select_for_update().get(
        id_producto=producto_id
    )

    stock_anterior = producto.stock_actual or Decimal("0.00")
    cantidad = Decimal(cantidad)
    precio_unitario = Decimal(precio_unitario)

    if cantidad > stock_anterior:
        raise ValueError(
            f"Stock insuficiente. Disponible: {stock_anterior}."
        )

    subtotal = cantidad * precio_unitario
    stock_nuevo = stock_anterior - cantidad

    salida = Salida.objects.create(
        id_cliente=cliente.id_cliente if cliente else None,
        id_usuario=id_usuario_sistema,
        tipo="VENTA",
        observacion=observacion or "Registro de salida por venta.",
        total=subtotal,
        estado=True,
    )

    # SQL Server calcula subtotal automáticamente.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO detalle_salida (
                id_salida,
                id_producto,
                cantidad,
                precio_unitario
            )
            VALUES (%s, %s, %s, %s)
            """,
            [
                salida.id_salida,
                producto.id_producto,
                cantidad,
                precio_unitario,
            ],
        )

    producto.stock_actual = stock_nuevo
    producto.save(update_fields=["stock_actual"])

    MovimientoStock.objects.create(
        producto=producto,
        id_usuario=id_usuario_sistema,
        tipo_movimiento="SALIDA",
        referencia=f"SALIDA #{salida.id_salida}",
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_actual=stock_nuevo,
        observacion=observacion or "Salida por venta.",
    )

    return salida


@transaction.atomic
def registrar_ajuste_inventario(
    *,
    producto_id,
    stock_fisico,
    id_usuario_sistema,
    motivo,
):
    producto = Producto.objects.select_for_update().get(
        id_producto=producto_id
    )

    stock_anterior = producto.stock_actual or Decimal("0.00")
    stock_fisico = Decimal(stock_fisico)

    diferencia = stock_fisico - stock_anterior

    if diferencia == Decimal("0.00"):
        raise ValueError(
            "El stock físico es igual al stock actual. "
            "No es necesario registrar un ajuste."
        )

    producto.stock_actual = stock_fisico
    producto.save(update_fields=["stock_actual"])

    tipo_ajuste = "AUMENTO" if diferencia > 0 else "DISMINUCIÓN"
    cantidad_ajustada = abs(diferencia)

    MovimientoStock.objects.create(
        producto=producto,
        id_usuario=id_usuario_sistema,
        tipo_movimiento="AJUSTE",
        referencia="AJUSTE DE INVENTARIO",
        cantidad=cantidad_ajustada,
        stock_anterior=stock_anterior,
        stock_actual=stock_fisico,
        observacion=(
            f"{motivo} | Ajuste por {tipo_ajuste}: "
            f"{cantidad_ajustada}"
        ),
    )

    return producto, diferencia


