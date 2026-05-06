from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from animes.utils import obtener_estadisticas
from .models import CustomUser
from .forms import CustomUserCreationForm
from django.contrib import messages
from animes.models import Anime


def register(request):
    """
    Vista de registro

    Si el metodo es un POST, proces el formulario del form.py.
    Si hay errores lanza un mensaje de error.
    Si el metodo es un GET, muestra el formulario vacio.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Tu cuenta ha sido creada correctamente.")
            return redirect("animes:home")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    """
    Vista del perfil con estadisticas

    Obtiene estadisticas del usuario mediante el utils.py (app) para poder pasarlas al html y utilizarlas.
    Obtiene los ultimos 6 animes vistos con la fecha de fin para poder usarlo en el html.
    Renderiza el profile.html con todos los parametros pasados.
    """
    user = request.user

    stats = obtener_estadisticas(user)

    recientes = Anime.objects.filter(
        user=user,
        estado="visto",
        fecha_fin__isnull=False
    ).order_by("-fecha_fin")[:6]

    return render(request, "users/profile.html", {
        "user": user,
        "recientes": recientes,
        **stats,
    })


@login_required
def profile_edit(request):
    """
    Vista para editar el perfil del usuario

    Permite modificar unicamente username, email, bio y avatar
    Validacion por si el email esta vacio y tambien ejecutamos validaciones del modelo
    Si hay errores los muestra mediantes mensajes
    """
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        bio = request.POST.get("bio")
        avatar = request.FILES.get("avatar")

        if not email:
            messages.error(request, "El email no puede estar vacío.")
            return redirect("users:profile_edit")

        user.username = username
        user.email = email
        user.bio = bio

        if avatar:
            user.avatar = avatar

        try:
            user.full_clean()
            user.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("users:profile")

        except ValidationError as e:
            for field, msgs in e.message_dict.items():
                for msg in msgs:
                    messages.error(request, msg)
            return redirect("users:profile_edit")

    return render(request, "users/profile_edit.html", {"user": user})
