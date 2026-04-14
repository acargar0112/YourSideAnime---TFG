from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .forms import CustomUserCreationForm
from django.contrib import messages
from animes.models import Anime


def register(request):
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
    user = request.user

    total_vistos = Anime.objects.filter(user=user, estado="visto").count()
    total_viendo = Anime.objects.filter(user=user, estado="viendo").count()
    total_whitelist = Anime.objects.filter(user=user, estado="whitelist").count()
    total_dropeados = Anime.objects.filter(user=user, estado="dropeado").count()

    recientes = Anime.objects.filter(
        user=user,
        estado="visto",
        fecha_fin__isnull=False
    ).order_by("-fecha_fin")[:4]

    return render(request, "users/profile.html", {
        "user": user,
        "recientes": recientes,
        "total_vistos": total_vistos,
        "total_viendo": total_viendo,
        "total_whitelist": total_whitelist,
        "total_dropeados": total_dropeados,
    })


@login_required
def profile_edit(request):
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

        user.save()

        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("users:profile")

    return render(request, "users/profile_edit.html", {"user": user})
