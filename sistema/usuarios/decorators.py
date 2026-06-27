from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def rol_requerido(*roles_permitidos):
    def decorador(vista):
        @login_required
        @wraps(vista)
        def vista_protegida(request, *args, **kwargs):
            perfil = getattr(request.user, "perfil", None)

            if not perfil:
                return HttpResponseForbidden(
                    "No tiene un perfil asignado para acceder a esta sección."
                )

            if perfil.rol not in roles_permitidos:
                return HttpResponseForbidden(
                    "No tiene permisos para acceder a esta sección."
                )

            return vista(request, *args, **kwargs)

        return vista_protegida

    return decorador