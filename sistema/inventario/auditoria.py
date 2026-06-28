from .models import Bitacora


def obtener_ip_origen(request):
    ip_reenviada = request.META.get("HTTP_X_FORWARDED_FOR")

    if ip_reenviada:
        return ip_reenviada.split(",")[0].strip()[:50]

    return request.META.get("REMOTE_ADDR", "")[:50]


def obtener_usuario_sql(request):
    if not request.user.is_authenticated:
        return None

    perfil = getattr(request.user, "perfil", None)

    if not perfil:
        return None

    return perfil.id_usuario_sistema or None


def registrar_bitacora(request, accion, modulo="", descripcion=""):
    Bitacora.objects.create(
        id_usuario=obtener_usuario_sql(request),
        accion=accion[:150],
        modulo=modulo[:100] if modulo else None,
        descripcion=descripcion[:255] if descripcion else None,
        ip_origen=obtener_ip_origen(request),
    )