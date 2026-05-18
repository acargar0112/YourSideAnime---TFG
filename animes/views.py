from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Anime, Review
from django.contrib import messages
from django.core.exceptions import ValidationError
from deep_translator import GoogleTranslator
from django.http import JsonResponse
import requests


def home(request):
    """
    Página principal del usuario

    Si el usuario no ha iniciado sesión muestra una versión básica del home.
    Si esta autenticado puede:
    - Anime aleatorio dropeado para recomendar continuar
    - Estadísticas del usuario
    - Menu desplegable para poder navegar por la página
    - Un buscador para poder buscar los animes y añadirlos a tu lista
    """
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
    """
    Retorna página de estado "viendo" (viendo.html), con paginación y título correspondiente.
    """
    animes_list = Anime.objects.filter(user=request.user, estado="viendo").order_by("-id")
    paginator = Paginator(animes_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "animes": page_obj,
        "page_obj": page_obj,
        "active_tab": "viendo",
        "page_title": "Viendo",
    }
    return render(request, "animes/viendo.html", context)


@login_required
def vistos(request):
    """
    Retorna página de estado "vistos" (vistos.html), con paginación y título correspondiente.
    """
    animes_list = Anime.objects.filter(user=request.user, estado="visto").order_by("-id")
    paginator = Paginator(animes_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "animes": page_obj,
        "page_obj": page_obj,
        "active_tab": "vistos",
        "page_title": "Vistos",
    }

    return render(request, "animes/vistos.html", context)


@login_required
def dropeados(request):
    """
    Retorna página de estado "dropeado" (dropeado.html), con paginación y título correspondiente.
    """
    animes_list = Anime.objects.filter(user=request.user, estado="dropeado").order_by("-id")
    paginator = Paginator(animes_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "animes": page_obj,
        "page_obj": page_obj,
        "active_tab": "dropeados",
        "page_title": "Dropeados",
    }

    return render(request, "animes/dropeados.html", context)


@login_required
def whitelist(request):
    """
    Retorna página de estado "whitelist" (whitelist.html), con paginación y título correspondiente.
    """
    animes_list = Anime.objects.filter(user=request.user, estado="whitelist").order_by("-id")
    paginator = Paginator(animes_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "animes": page_obj,
        "page_obj": page_obj,
        "active_tab": "whitelist",
        "page_title": "Whitelist",
    }

    return render(request, "animes/whitelist.html", context)

@login_required
def add_anime(request):
    """
    Añade un anime a la lista del usuario

    Solo acepta metodo POST.
    Crea un objeto Anime con los datos enviados desde el formulario del modal.
    Ejecuta validaciones personalizadas mediante full_clean() y guarda el anime si es válido.

    En caso de error:
    - Muestra mensajes de validación
    - Redirige a la URL indicada en "return_url".

    Retorna a la ficha del anime(ficha.html) o a la home(home.html).
    """
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
    """
    Retorna la pagina de buscar.html

    La búsqueda se realiza desde el cliente mediante un fetch() a la API de AniList.
    """
    return render(request, "animes/buscar.html", {})

@login_required
def anime_edit(request, pk):
    """
    Editar un anime existente del usuario.

    Solo acepta metodo POST
    Actualiza los campos del anime con los valores enviados desde el modal.
    Ejecuta validaciones personalizadas mediante full_clean()

    Devuelve mensajes de error y redirige a la url indicada

    Retorna a la url indicada o al home(home.html)
    """
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
    """
    Muestra la ficha detallada de un anime.
    Intenta AniList primero, si falla usa Jikan como respaldo.
    Muestra un badge indicando qué API se está usando.
    """
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

    anime = None
    api_data = None
    source = None

    # Intento 1: AniList
    try:
        response = requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"id": int(api_id)}},
            timeout=10
        )
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}")

        json_data = response.json()
        if not json_data.get("data") or not json_data["data"].get("Media"):
            raise Exception("Respuesta inesperada de AniList")

        data = json_data["data"]["Media"]

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

        source = "anilist"

    except Exception as e:
        print("AniList ficha caída, usando Jikan:", e)

    # Intento 2: Jikan como respaldo
    if anime is None:
        try:
            response = requests.get(
                f"https://api.jikan.moe/v4/anime/{api_id}",
                timeout=10
            )

            # Buscamos por el título guardado del usuario
            if not response.ok:
                anime_guardado = request.user.animes.filter(api_id=api_id).first()
                if anime_guardado:
                    search_resp = requests.get(
                        f"https://api.jikan.moe/v4/anime?q={anime_guardado.titulo}&limit=1",
                        timeout=10
                    )
                    if search_resp.ok:
                        resultados = search_resp.json().get("data", [])
                        if resultados:
                            data = resultados[0]
                        else:
                            raise Exception("No encontrado en Jikan")
                    else:
                        raise Exception("Jikan búsqueda falló")
                else:
                    raise Exception(f"HTTP {response.status_code}")
            else:
                data = response.json().get("data", {})

            descripcion_raw = data.get("synopsis") or ""
            descripcion_es = GoogleTranslator(
                source="auto", target="es"
            ).translate(descripcion_raw)

            anime = {
                "titulo": data.get("title"),
                "imagen_url": data.get("images", {}).get("jpg", {}).get("large_image_url"),
                "sinopsis": descripcion_es,
                "episodios": data.get("episodes"),
                "mal_id": api_id,
            }

            api_data = {
                "title_jp": data.get("title_japanese"),
                "score": data.get("score"),
                "episodes": data.get("episodes"),
                "year": data.get("year"),
                "status": data.get("status"),
                "genres": [g["name"] for g in data.get("genres", [])],
            }

            source = "jikan"

        except Exception as e:
            print("Error también en Jikan ficha:", e)
            anime = None
            api_data = None

    anime_guardado = request.user.animes.filter(api_id=api_id).first()

    return render(request, "animes/ficha.html", {
        "anime": anime,
        "api_data": api_data,
        "anime_guardado": anime_guardado,
        "reviews": Review.objects.filter(anime__api_id=api_id).order_by("-creado"),
        "source": source,
    })

@login_required
def add_review(request, anime_id):
    """
    Añade una reseña a un anime del usuario.

    Solo acepta metodo POST.
    Crea una Review si el texto no está vacío
    Validaciones full_clean del modelo

    Retorna a la ficha del anime.
    """
    anime = get_object_or_404(Anime, id=anime_id, user=request.user)

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()

        if not texto:
            messages.error(request, "La reseña no puede ser publicada vacía.")
            return redirect("animes:ficha", api_id=anime.api_id)

        review = Review(
            user=request.user,
            anime=anime,
            texto=texto
        )

        try:
            review.full_clean()
            review.save()
            messages.success(request, "Reseña publicada correctamente.")

        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)

        return redirect("animes:ficha", api_id=anime.api_id)



@login_required
def anime_delete(request, pk):
    """
    Elimina un anime de la lista del usuario.

    Solo acepta metodo POST.
    Borra el anime y redirige a la URL inficada o al home(home.html)

    Retorna a la URL correspondiente. (return_url)
    """
    anime = get_object_or_404(Anime, pk=pk, user=request.user)

    if request.method == "POST":
        return_url = request.POST.get("return_url", "animes:home")
        anime.delete()
        return redirect(return_url)


@login_required
def delete_review(request, review_id):
    """
    Vista para borrar las reseñas.
    """
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user and not request.user.is_superuser:
        return redirect("animes:home")

    api_id = review.anime.api_id

    if request.method == "POST":
        review.delete()
        messages.success(request, "Reseña eliminada correctamente.")

    return redirect("animes:ficha", api_id=api_id)

@login_required
def edit_review(request, review_id):
    """
    Vista para poder editar las reseñas, pasando el usuario para la valiaación.

    Validaciones a la reseña por si esta vacia o no has cambiado su contenido.
    Validaciones del modelo full clean
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()

        if not texto:
            messages.error(request, "La reseña no puede ser publicada vacía.")
            return redirect("animes:ficha", api_id=review.anime.api_id)

        if texto == review.texto:
            messages.error(request, "No has realizado ningún cambio en la reseña.")
            return redirect("animes:ficha", api_id=review.anime.api_id)

        review.texto = texto

        try:
            review.full_clean()
            review.save()
            messages.success(request, "Reseña actualizada correctamente.")

        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)

    return redirect("animes:ficha", api_id=review.anime.api_id)

@login_required
def otra_oportunidad(request):
    """
    Devuelve un anime dropeado aleatorio distinto al último
    """
    user = request.user
    ultimo_id = request.session.get("ultimo_dropeado")

    qs = Anime.objects.filter(user=user, estado="dropeado")
    if ultimo_id:
        qs = qs.exclude(id=ultimo_id)

    seguir_dropeado = qs.order_by("?").first()

    if not seguir_dropeado:
        seguir_dropeado = Anime.objects.filter(user=user, estado="dropeado").order_by("?").first()

    if not seguir_dropeado:
        return JsonResponse({"found": False})

    request.session["ultimo_dropeado"] = seguir_dropeado.id

    return JsonResponse({
        "found": True,
        "titulo": seguir_dropeado.titulo,
        "imagen_url": seguir_dropeado.imagen_url,
        "episodios_vistos": seguir_dropeado.episodios_vistos,
        "episodios_totales": seguir_dropeado.episodios_totales,
        "ficha_url": f"/ficha/{seguir_dropeado.api_id}/",
    })

@login_required
def proxy_buscar(request):
    """
    Proxy para la búsqueda. Intenta AniList primero, si falla usa Jikan (MAL) como respaldo.
    Cuando usa Jikan, busca el ID de AniList equivalente para que la ficha funcione.
    """
    q = request.GET.get("q", "")

    # Intento 1: AniList
    anilist_query = """
    query ($search: String) {
      Page(perPage: 20) {
        media(search: $search, type: ANIME) {
          id
          title { romaji }
          episodes
          coverImage { large }
        }
      }
    }
    """
    try:
        response = requests.post(
            "https://graphql.anilist.co",
            json={"query": anilist_query, "variables": {"search": q}},
            timeout=10
        )
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}")
        data = response.json()
        if not data.get("data") or not data["data"].get("Page"):
            raise Exception("Respuesta inesperada de AniList")
        return JsonResponse(data)

    except Exception as e:
        print("AniList caída, usando Jikan como respaldo:", e)

    # Intento 2: Jikan como respaldo
    try:
        response = requests.get(
            f"https://api.jikan.moe/v4/anime?q={q}&limit=20",
            timeout=10
        )
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}")

        jikan_data = response.json()

        media = []
        for anime in jikan_data.get("data", []):
            titulo = anime["title"]

            # Buscamos el ID de AniList usando el título del anime
            anilist_id = None
            try:
                anilist_resp = requests.post(
                    "https://graphql.anilist.co",
                    json={
                        "query": """
                        query ($search: String) {
                          Media(search: $search, type: ANIME) { id }
                        }
                        """,
                        "variables": {"search": titulo}
                    },
                    timeout=5
                )
                if anilist_resp.ok:
                    anilist_json = anilist_resp.json()
                    anilist_id = anilist_json.get("data", {}).get("Media", {}).get("id")
            except Exception:
                pass

            media.append({
                # Si encontramos ID de AniList lo usamos
                "id": anilist_id if anilist_id else anime["mal_id"],
                "title": {"romaji": titulo},
                "episodes": anime.get("episodes"),
                "coverImage": {"large": anime["images"]["jpg"]["large_image_url"]}
            })

        return JsonResponse({"data": {"Page": {"media": media}}})

    except Exception as e:
        print("Error también en Jikan:", e)
        return JsonResponse({"error": "Ambas APIs no disponibles"}, status=502)