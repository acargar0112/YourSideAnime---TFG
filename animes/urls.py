from django.urls import path
from . import views

app_name = "animes"

urlpatterns = [
    path('', views.home, name='home'),
    path("viendo/", views.viendo, name="viendo"),
    path("vistos/", views.vistos, name="vistos"),
    path("dropeados/", views.dropeados, name="dropeados"),
    path("whitelist/", views.whitelist, name="whitelist"),
    path("anime/<int:pk>/", views.anime_detail, name="detail"),
    path("anime/add/", views.anime_add, name="add"),
    path("anime/<int:pk>/edit/", views.anime_edit, name="edit"),
    path("anime/<int:pk>/delete/", views.anime_delete, name="delete"),
]