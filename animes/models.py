from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings

class Anime(models.Model):

    ESTADOS = [
        ("viendo", "Viendo"),
        ("visto", "Visto"),
        ("dropeado", "Dropeado"),
        ("whitelist", "Whitelist"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="animes")
    titulo = models.CharField(max_length=255)
    imagen_url = models.URLField(blank=True, null=True)
    sinopsis = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="viendo")
    rating = models.PositiveSmallIntegerField(default=0)
    episodios_totales = models.PositiveIntegerField(default=0)
    episodios_vistos = models.PositiveIntegerField(default=0)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    api_id = models.PositiveIntegerField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} ({self.user.username})"

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reviews")
    anime = models.ForeignKey(Anime,on_delete=models.CASCADE,related_name="reviews")
    texto = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review de {self.user.username} para {self.anime.titulo}"
