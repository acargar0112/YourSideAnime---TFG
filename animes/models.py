from django.db import models
from django.core.exceptions import ValidationError

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
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    episodios_totales = models.PositiveIntegerField(default=0)
    episodios_vistos = models.PositiveIntegerField(default=0)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    api_id = models.PositiveIntegerField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} ({self.user.username})"

    def clean(self):
        errors = {}

        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio > self.fecha_fin:
                errors["fecha_inicio"] = "La fecha de inicio no puede ser posterior a la fecha de fin."

        if self.estado == "visto":
            if not self.fecha_inicio or not self.fecha_fin:
                errors["fecha_inicio"] = "Debes rellenar las fechas de inicio y fin"


        if self.estado == "viendo":
            if self.episodios_vistos <= 0:
                errors["estado"] = "No puedes estar viendo un anime con 0 episodios vistos."
            if self.episodios_vistos >= self.episodios_totales:
                errors["estado"] = "Los episodios vistos no pueden ser mayor a los episodios totales."
            if not self.fecha_inicio:
                errors["fecha_inicio"] = "Debes rellenar la fecha de inicio"

        if self.estado == "dropeado":
            if self.episodios_vistos <= 0:
                errors["estado"] = "No puedes dropear un anime sin ver al menos 1 episodio."
            if self.episodios_vistos >= self.episodios_totales:
                errors["estado"] = "Los episodios vistos no pueden ser mayor a los episodios totales."
            if not self.fecha_inicio:
                errors["fecha_inicio"] = "Debes rellenar la fecha de inicio"


        if self.rating < 0 or self.rating > 5:
            errors["rating"] = "El rating tiene que ser entre 0 y 5."


        if errors:
            raise ValidationError(errors)

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reviews")
    anime = models.ForeignKey(Anime,on_delete=models.CASCADE,related_name="reviews")
    texto = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review de {self.user.username} para {self.anime.titulo}"
