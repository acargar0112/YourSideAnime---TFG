from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator

def validar_tamano_avatar(archivo):
    """
    Validador personalizado para limitar el tamaño del avatar a 2 MB.
    En caso de que este lo supere se lanzará un ValidationError.
    """
    limite = 2
    if archivo.size > limite * 1024 * 1024:
        raise ValidationError(f"El avatar no puede superar los {limite} MB.")


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extende el AbstractUser, en este caso hemos añadido los campos avatar y bio.
    """
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, validators=[FileExtensionValidator(["jpg","jpeg","png"]), validar_tamano_avatar])
    bio = models.TextField(blank=True, null=True)

    def clean(self):
        """
        Validación para el email introducido para el registro del usuario, si este tiene un fallo lanza un ValidationError.
        """
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
        """
        Representación en el admin
        """
        return self.username
