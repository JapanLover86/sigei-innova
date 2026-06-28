from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from inventario.models import DetalleSalida
from productos.models import Producto

from .models import PrediccionDemanda


DIAS_ANALISIS = 30
DIAS_COBERTURA_OBJETIVO = 30
CERO = Decimal("0.00")


def convertir_decimal(valor):
    if valor is None:
        return CERO

    if isinstance(valor, Decimal):
        return valor

    return Decimal(str(valor))


def redondear(valor):
    return convertir_decimal(valor).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def clasificar_riesgo(stock_actual, demanda_diaria):
    if demanda_diaria <= CERO:
        return "SIN DATOS", None

    dias_cobertura = redondear(stock_actual / demanda_diaria)

    if stock_actual <= CERO or dias_cobertura <= Decimal("7"):
        return "CRÍTICO", dias_cobertura

    if dias_cobertura <= Decimal("15"):
        return "MEDIO", dias_cobertura

    return "BAJO", dias_cobertura


@transaction.atomic
def generar_predicciones():
    fecha_inicio = timezone.now() - timedelta(days=DIAS_ANALISIS)

    ventas_por_producto = (
        DetalleSalida.objects.filter(
            salida__estado=True,
            salida__fecha__gte=fecha_inicio,
            producto__estado=True,
        )
        .values("producto_id")
        .annotate(total_vendido=Sum("cantidad"))
    )

    ventas_map = {
        fila["producto_id"]: convertir_decimal(fila["total_vendido"])
        for fila in ventas_por_producto
    }

    productos = Producto.objects.filter(
        estado=True,
    ).order_by("nombre")

    resultados = []

    for producto in productos:
        stock_actual = convertir_decimal(producto.stock_actual)
        total_vendido = ventas_map.get(producto.id_producto, CERO)

        demanda_diaria = redondear(
            total_vendido / Decimal(DIAS_ANALISIS)
        )

        cantidad_sugerida = redondear(
            max(
                CERO,
                (demanda_diaria * Decimal(DIAS_COBERTURA_OBJETIVO))
                - stock_actual,
            )
        )

        riesgo, dias_cobertura = clasificar_riesgo(
            stock_actual,
            demanda_diaria,
        )

        if dias_cobertura is None:
            cobertura_texto = "Sin datos de ventas"
        else:
            cobertura_texto = f"{dias_cobertura} días"

        observacion = (
            f"Ventas 30d: {total_vendido}; "
            f"stock: {stock_actual}; "
            f"cobertura: {cobertura_texto}; "
            f"compra sugerida: {cantidad_sugerida}; "
            f"riesgo: {riesgo}."
        )

        registro = PrediccionDemanda.objects.create(
            producto=producto,
            periodo="Últimos 30 días",
            demanda_predicha=demanda_diaria,
            metodo="Promedio móvil 30 días",
            observacion=observacion,
        )

        resultados.append(
            {
                "registro": registro,
                "stock_actual": stock_actual,
                "total_vendido": total_vendido,
                "demanda_diaria": demanda_diaria,
                "dias_cobertura": dias_cobertura,
                "cantidad_sugerida": cantidad_sugerida,
                "riesgo": riesgo,
            }
        )

    return resultados