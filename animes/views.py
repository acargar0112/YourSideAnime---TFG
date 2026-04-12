from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Anime
import requests


@login_required
def home(request):
    animes_list = Anime.objects.filter(user=request.user).order_by("-creado")

    paginator = Paginator(animes_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "animes/home.html", {"page_obj": page_obj})

@login_required
def viendo(request):
    animes = Anime.objects.filter(user=request.user, estado="viendo").order_by("-id")

    context = {
        "animes": animes,
        "active_tab": "viendo",
        "page_title": "Viendo",
    }
    return render(request, "animes/viendo.html", context)


@login_required
def vistos(request):
    animes = Anime.objects.filter(user=request.user, estado="visto").order_by("-id")

    context = {
        "animes": animes,
        "active_tab": "vistos",
        "page_title": "Vistos",
    }

    return render(request, "animes/vistos.html", context)


@login_required
def dropeados(request):
    animes = Anime.objects.filter(user=request.user, estado="dropeado").order_by("-id")

    context = {
        "animes": animes,
        "active_tab": "dropeados",
        "page_title": "Dropeados",
    }

    return render(request, "animes/dropeados.html", context)


@login_required
def whitelist(request):
    animes = Anime.objects.filter(user=request.user, estado="whitelist").order_by("-id")

    context = {
        "animes": animes,
        "active_tab": "whitelist",
        "page_title": "Whitelist",
    }

    return render(request, "animes/whitelist.html", context)


@login_required
def anime_detail(request, pk):
    anime = get_object_or_404(Anime, pk=pk, user=request.user)

    api_data = None

    if anime.api_id:
        try:
            response = requests.get(f"https://api.jikan.moe/v4/anime/{anime.api_id}")
            if response.status_code == 200:
                data = response.json().get("data", {})

                api_data = {
                    "title_jp": data.get("title_japanese"),
                    "episodes": data.get("episodes"),
                    "year": data.get("year"),
                    "status": data.get("status"),
                    "genres": [g["name"] for g in data.get("genres", [])],
                    "score": data.get("score"),
                    "trailer": data.get("trailer", {}).get("url"),
                }
        except Exception:
            api_data = None

    return render(request, "animes/detail.html", {
        "anime": anime,
        "api_data": api_data,
    })

def buscar_anime(request):
    query = request.GET.get("q", "")
    resultados = []

    if query:
        url = f"https://api.jikan.moe/v4/anime?q={query}&limit=12"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json().get("data", [])
            resultados = [
                {
                    "api_id": item["mal_id"],
                    "titulo": item["title"],
                    "imagen": item["images"]["jpg"]["image_url"],
                    "episodios": item.get("episodes", 0),
                }
                for item in data
            ]

    return render(request, "animes/buscar.html", {
        "query": query,
        "resultados": resultados,
    })

@login_required
def add_anime(request):
    if request.method == "POST":
        Anime.objects.create(
            user=request.user,
            titulo = request.POST.get("titulo"),
            imagen_url = request.POST.get("imagen_url"),
            api_id=request.POST.get("api_id"),
            estado = request.POST.get("estado"),
            rating = request.POST.get("rating") or 0,
            fecha_inicio=request.POST.get("fecha_inicio") or None,
            fecha_fin=request.POST.get("fecha_fin") or None,
            episodios_totales = request.POST.get("episodios_totales", 0),
            episodios_vistos=request.POST.get("episodios_vistos") or 0,

        )

        return redirect("animes:buscar")

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
