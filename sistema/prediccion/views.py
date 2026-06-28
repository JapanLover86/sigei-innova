from django.contrib import messages
from django.shortcuts import render

from usuarios.decorators import rol_requerido

from .models import PrediccionDemanda
from .services import generar_predicciones


@rol_requerido("ADMIN", "GERENTE")
def prediccion_inicio(request):
    resultados = []

    if request.method == "POST":
        resultados = generar_predicciones()

        messages.success(
            request,
            f"Se generaron {len(resultados)} predicciones de demanda.",
        )

    historial = (
        PrediccionDemanda.objects.select_related("producto")
        .order_by("-fecha_prediccion", "-id_prediccion")[:30]
    )

    return render(
        request,
        "prediccion/inicio.html",
        {
            "resultados": resultados,
            "historial": historial,
        },
    )