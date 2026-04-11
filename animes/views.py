from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Anime

@login_required
def home(request):
    animes_list = Anime.objects.filter(user=request.user).order_by("-creado")

    paginator = Paginator(animes_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "animes/home.html", {"page_obj": page_obj})

@login_required
def viendo(request):
    animes = Anime.objects.filter(user=request.user, estado="viendo")
    return render(request, "animes/viendo.html", {"animes": animes})


@login_required
def vistos(request):
    animes = Anime.objects.filter(user=request.user, estado="visto")
    return render(request, "animes/vistos.html", {"animes": animes})


@login_required
def dropeados(request):
    animes = Anime.objects.filter(user=request.user, estado="dropeado")
    return render(request, "animes/dropeados.html", {"animes": animes})


@login_required
def whitelist(request):
    animes = Anime.objects.filter(user=request.user, estado="whitelist")
    return render(request, "animes/whitelist.html", {"animes": animes})


@login_required
def anime_detail(request, pk):
    anime = get_object_or_404(Anime, pk=pk, user=request.user)
    return render(request, "animes/detail.html", {"anime": anime})

@login_required
def anime_add(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        imagen_url = request.POST.get("imagen_url")
        sinopsis = request.POST.get("sinopsis")
        estado = request.POST.get("estado")
        rating = request.POST.get("rating", 0)
        episodios_totales = request.POST.get("episodios_totales", 0)
        episodios_vistos = request.POST.get("episodios_vistos", 0)

        Anime.objects.create(
            user=request.user,
            titulo=titulo,
            imagen_url=imagen_url,
            sinopsis=sinopsis,
            estado=estado,
            rating=rating,
            episodios_totales=episodios_totales,
            episodios_vistos=episodios_vistos,
        )

        return redirect("animes:home")

    return render(request, "animes/add.html")


@login_required
def anime_edit(request, pk):
    anime = get_object_or_404(Anime, pk=pk, user=request.user)

    if request.method == "POST":
        anime.titulo = request.POST.get("titulo")
        anime.imagen_url = request.POST.get("imagen_url")
        anime.sinopsis = request.POST.get("sinopsis")
        anime.estado = request.POST.get("estado")
        anime.rating = request.POST.get("rating", 0)
        anime.episodios_totales = request.POST.get("episodios_totales", 0)
        anime.episodios_vistos = request.POST.get("episodios_vistos", 0)
        anime.save()

        return redirect("animes:detail", pk=anime.pk)

    return render(request, "animes/edit.html", {"anime": anime})


@login_required
def anime_delete(request, pk):
    anime = get_object_or_404(Anime, pk=pk, user=request.user)

    if request.method == "POST":
        anime.delete()
        return redirect("animes:home")

    return render(request, "animes/delete_confirm.html", {"anime": anime})
