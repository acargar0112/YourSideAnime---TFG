from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Anime, Review
from django.contrib import messages
from django.core.exceptions import ValidationError
from deep_translator import GoogleTranslator
import requests


def home(request):

    if not request.user.is_authenticated:
        return render(request, "animes/home.html", {
            "page_obj": [],
            "ranking": [],
            "seguir_dropeado": None
        })

    user = request.user

    ultimo_id = request.session.get("ultimo_dropeado")

    qs = Anime.objects.filter(user=user, estado="dropeado")

    if ultimo_id:
        qs = qs.exclude(id=ultimo_id)

    seguir_dropeado = qs.order_by("?").first()

    if not seguir_dropeado:
        seguir_dropeado = Anime.objects.filter(user=user, estado="dropeado").order_by("?").first()

    if seguir_dropeado:
        request.session["ultimo_dropeado"] = seguir_dropeado.id

    animes_list = Anime.objects.filter(user=user).order_by("-creado")
    paginator = Paginator(animes_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    ranking = Anime.objects.filter(user=user, estado="visto", rating__gt=0).order_by("-rating")[:6]

    return render(request, "animes/home.html", {
        "page_obj": page_obj,
        "ranking": ranking,
        "seguir_dropeado": seguir_dropeado,
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
        anime = Anime(
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

        try:
            anime.full_clean()
            anime.save()
            messages.success(request, "Añadido correctamente.")
            return redirect("animes:ficha", api_id=anime.api_id)

        except ValidationError as e:
            for field, msgs in e.message_dict.items():
                for msg in msgs:
                    messages.error(request, msg)

            return redirect(request.POST.get("return_url", "animes:home"))

    return redirect("animes:home")

@login_required
def buscar_anime(request):
    query = request.GET.get("q", "")
    resultados = []

    if query:
        query_graphql = """
        query ($search: String) {
          Page(perPage: 20) {
            media(search: $search, type: ANIME) {
              id
              title {
                romaji
              }
              episodes
              coverImage {
                large
              }
            }
          }
        }
        """

        variables = {"search": query}

        try:
            response = requests.post(
                "https://graphql.anilist.co",
                json={"query": query_graphql, "variables": variables},
                timeout=10
            ).json()

            media = response["data"]["Page"]["media"]

            for item in media:
                resultados.append({
                    "api_id": item["id"],
                    "titulo": item["title"]["romaji"],
                    "imagen": item["coverImage"]["large"],
                    "episodios": item["episodes"] or 0,
                })

        except Exception as e:
            print("Error AniList:", e)

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

        try:
            anime.full_clean()
            anime.save()
            messages.success(request, "Actualizado correctamente.")
            return redirect(request.POST.get("return_url", "animes:home"))

        except ValidationError as e:
            for field, msgs in e.message_dict.items():
                for msg in msgs:
                    messages.error(request, msg)

            return redirect(request.POST.get("return_url", "animes:home"))

    return redirect("animes:home")

@login_required
def api_ficha(request, api_id):

    query = """
    query ($id: Int) {
      Media(id: $id, type: ANIME) {
        id
        title { romaji english native }
        description(asHtml: false)
        episodes
        seasonYear
        status
        averageScore
        genres
        coverImage { large }
      }
    }
    """

    try:
        data = requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"id": int(api_id)}},
            timeout=10
        ).json()["data"]["Media"]

        descripcion_es = GoogleTranslator(
            source="auto", target="es"
        ).translate(data["description"] or "")

        anime = {
            "titulo": data["title"]["romaji"] or data["title"]["english"],
            "imagen_url": data["coverImage"]["large"],
            "sinopsis": descripcion_es,
            "episodios": data["episodes"],
            "mal_id": data["id"],
        }

        api_data = {
            "title_jp": data["title"]["native"],
            "score": data["averageScore"],
            "episodes": data["episodes"],
            "year": data["seasonYear"],
            "status": data["status"],
            "genres": data["genres"],
        }

    except Exception as e:
        print("Error AniList ficha:", e)
        anime = None
        api_data = None

    anime_guardado = request.user.animes.filter(api_id=api_id).first()

    return render(request, "animes/ficha.html", {
        "anime": anime,
        "api_data": api_data,
        "anime_guardado": anime_guardado,
        "reviews": Review.objects.filter(anime__api_id=api_id).order_by("-creado"),
    })

@login_required
def add_review(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id, user=request.user)

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()

        if texto:
            Review.objects.create(
                user=request.user,
                anime=anime,
                texto=texto
            )

        return redirect("animes:ficha", api_id=anime.api_id)



@login_required
def anime_delete(request, pk):
    anime = get_object_or_404(Anime, pk=pk, user=request.user)

    if request.method == "POST":
        return_url = request.POST.get("return_url", "animes:home")
        anime.delete()
        return redirect(return_url)
