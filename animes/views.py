from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Anime
from deep_translator import GoogleTranslator
import requests


@login_required
def home(request):
    user = request.user

    animes_list = Anime.objects.filter(user=user).order_by("-creado")
    paginator = Paginator(animes_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    total_vistos = Anime.objects.filter(user=user, estado="visto").count()
    total_viendo = Anime.objects.filter(user=user, estado="viendo").count()
    total_whitelist = Anime.objects.filter(user=user, estado="whitelist").count()
    total_dropeados = Anime.objects.filter(user=user, estado="dropeados").count()

    ranking = Anime.objects.filter(user=user, estado="visto", rating__gt=0).order_by("-rating")[:4]

    return render(request, "animes/home.html", {
        "page_obj": page_obj,
        "total_vistos": total_vistos,
        "total_viendo": total_viendo,
        "total_whitelist": total_whitelist,
        "total_dropeados": total_dropeados,
        "ranking": ranking,
    })

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

        return redirect("animes:home")

@login_required
def buscar_anime(request):
    query = request.GET.get("q", "")

    resultados = []

    if query:
        url = f"https://api.jikan.moe/v4/anime?q={query}&limit=20"
        response = requests.get(url).json()

        for item in response.get("data", []):
            resultados.append({
                "api_id": item.get("mal_id"),
                "titulo": item.get("title"),
                "imagen": item["images"]["jpg"]["image_url"],
                "episodios": item.get("episodes") or 0,
            })

    return render(request, "animes/buscar.html", {
        "query": query,
        "resultados": resultados
    })

@login_required
def anime_edit(request, pk):
    anime = get_object_or_404(Anime, pk=pk, user=request.user)

    if request.method == "POST":
        anime.titulo = request.POST.get("titulo")
        anime.imagen_url = request.POST.get("imagen_url")
        anime.estado = request.POST.get("estado")
        anime.rating = request.POST.get("rating", 0)
        anime.episodios_totales = request.POST.get("episodios_totales", 0)
        anime.episodios_vistos = request.POST.get("episodios_vistos", 0)
        anime.fecha_inicio = request.POST.get("fecha_inicio") or None
        anime.fecha_fin = request.POST.get("fecha_fin") or None

        anime.save()

        return redirect(request.POST.get("return_url", "animes:home"))

def api_ficha(request, api_id):
    response = requests.get(f"https://api.jikan.moe/v4/anime/{api_id}")

    if response.status_code != 200:
        return render(request, "animes/ficha.html", {"error": "No se pudo cargar la información."})

    data = response.json().get("data", {})

    sinopsis_en = data.get("synopsis") or ""
    try:
        sinopsis_es = GoogleTranslator(source="auto", target="es").translate(sinopsis_en)
    except:
        sinopsis_es = sinopsis_en

    anime = {
        "mal_id": data.get("mal_id"),
        "titulo": data.get("title"),
        "titulo_jp": data.get("title_japanese"),
        "imagen_url": data.get("images", {}).get("jpg", {}).get("large_image_url"),
        "sinopsis": sinopsis_es,
        "episodios": data.get("episodes"),
        "year": data.get("year"),
        "status": data.get("status"),
        "genres": [g["name"] for g in data.get("genres", [])],
        "score": data.get("score"),
        "trailer": data.get("trailer", {}).get("embed_url"),
    }

    anime_guardado = None
    if request.user.is_authenticated:
        anime_guardado = Anime.objects.filter(user=request.user, api_id=api_id).first()

    return render(request, "animes/ficha.html", {
        "anime": anime,
        "api_data": anime,
        "anime_guardado": anime_guardado,
    })




@login_required
def anime_delete(request, pk):
    anime = get_object_or_404(Anime, pk=pk, user=request.user)

    if request.method == "POST":
        return_url = request.POST.get("return_url", "animes:home")
        anime.delete()
        return redirect(return_url)
