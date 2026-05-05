from .models import Anime

def obtener_estadisticas(user):
    """
    Calcula estadísticas de los animes de un usuario

    Devuelve un diccionario por estado con:
    - total_vistos
    - total_viendo
    - total_whitelist
    - total_dropeados
    - total_animes (suma total)

    Porcentajes por estado (viendo, vistos, whitelist y dropeados)
    - pct_vistos
    - pct_viendo
    - pct_whitelist
    - pct_dropeados

    Return: Diccionario con totales y porcentajes de estado.
    """
    total_vistos = Anime.objects.filter(user=user, estado="visto").count()
    total_viendo = Anime.objects.filter(user=user, estado="viendo").count()
    total_whitelist = Anime.objects.filter(user=user, estado="whitelist").count()
    total_dropeados = Anime.objects.filter(user=user, estado="dropeado").count()

    total_animes = total_vistos + total_viendo + total_whitelist + total_dropeados

    def pct(x):
        return round((x / total_animes) * 100, 1) if total_animes > 0 else 0

    return {
        "total_vistos": total_vistos,
        "total_viendo": total_viendo,
        "total_whitelist": total_whitelist,
        "total_dropeados": total_dropeados,
        "total_animes": total_animes,

        "pct_vistos": pct(total_vistos),
        "pct_viendo": pct(total_viendo),
        "pct_whitelist": pct(total_whitelist),
        "pct_dropeados": pct(total_dropeados),
    }
