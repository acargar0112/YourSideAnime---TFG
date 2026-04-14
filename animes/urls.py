from django.urls import path
from . import views

app_name = "animes"

urlpatterns = [
    path('', views.home, name='home'),
    path("viendo/", views.viendo, name="viendo"),
    path("vistos/", views.vistos, name="vistos"),
    path("dropeados/", views.dropeados, name="dropeados"),
    path("whitelist/", views.whitelist, name="whitelist"),

    path("anime/add/", views.add_anime, name="add"),
    path("anime/<int:pk>/edit/", views.anime_edit, name="edit"),
    path("anime/<int:pk>/delete/", views.anime_delete, name="delete"),
    path("buscar/", views.buscar_anime, name="buscar"),
    path("ficha/<int:api_id>/", views.api_ficha, name="ficha"),

]