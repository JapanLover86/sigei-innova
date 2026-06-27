from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


class InicioSesionView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


@login_required
def dashboard_inicio(request):
    perfil = getattr(request.user, "perfil", None)

    contexto = {
        "perfil": perfil,
        "rol": perfil.get_rol_display() if perfil else "Sin rol asignado",
    }

    return render(request, "dashboard/inicio.html", contexto)


@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect("login")