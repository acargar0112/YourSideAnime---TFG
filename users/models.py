from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator


def validar_tamano_avatar(archivo):
    limite = 2
    if archivo.size > limite * 1024 * 1024:
        raise ValidationError(f"El avatar no puede superar los {limite} MB.")


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default_avatar.jpg", validators=[FileExtensionValidator(["jpg","jpeg","png"]), validar_tamano_avatar])
    bio = models.TextField(blank=True, null=True)

    def clean(self):
        errors = {}

        if self.email:
            email_lower = self.email.lower()

            dominios_permitidos = [
                "@gmail.com",
                "@gmail.es",
                "@hotmail.com",
                "@hotmail.es",
            ]

            if not any(email_lower.endswith(d) for d in dominios_permitidos):
                errors["email"] = "Solo se permiten correos de gmail(.com/.es) o hotmail(.com/.es)."

        if errors:
            raise ValidationError(errors)


    def __str__(self):
        return self.username
