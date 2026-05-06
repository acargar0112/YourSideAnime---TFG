from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

from django.db import models
from django.conf import settings

class Anime(models.Model):
    """
    Representa un anime guardado por un usuario

    Contiene:
    - Titulo
    _ Imagen
    - Sinopsis
    - Estado (viendo, visto, dropeado o whitelist)
    - Episodios vistos
    - Fecha inicio y fin
    - Rating
    - ID del anime (API Anilist)

    Este también tiene validaciones personalizadas que nos garantiza la coherencia de los datos guardados.
    """
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
        """
        Representación en el admin
        """
        return f"{self.titulo} ({self.user.username})"

    def clean(self):
        """
        Validaciones

        - La fecha de inicio no puede ser mayor a la de fin
        - Si el estado elegido es "visto", ambas fechas deben estar rellenadas
        - Si el estado es "viendo":
            - Debe tener al menos 1 episodio visto
            - Los episodios vistos no pueden superar los episodios totales
            - Debe tener fecha de incio
        - Si el estado es "dropeado":
            - Debe tener al menos 1 episodios menos de los totales
            - Los episodios vistos no pueden superar los episodios totales
            - Debe tener fecha de inicio
        - El rating debe estar entre 0 y 5. (Valiendo 0.5)
        """
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
    """
    Representa una reseña por un usuario en un anime en concreto

    Contiene:
    - User (Usuario que la escribio)
    - Anime (Anime en la que se ha escrito)
    - Texto
    - Fecha de creacion de la reseña

    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reviews")
    anime = models.ForeignKey(Anime,on_delete=models.CASCADE,related_name="reviews")
    texto = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Representación en el admin
        """
        return f"Review de {self.user.username} para {self.anime.titulo}"
