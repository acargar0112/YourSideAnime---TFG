from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para registrar usuarios.
    """
    class Meta:
        model = CustomUser
        # Campos que se mostrarán en el formulario de registro.
        fields = ["username", "email", "password1", "password2" ,"avatar", "bio"]
