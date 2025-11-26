from django.urls import path
from . import views

app_name = "fichas"

urlpatterns = [
    path("", views.ReceitaListView.as_view(), name="lista_fichas"),
    path("<int:pk>/", views.ReceitaDetailView.as_view(), name="ficha"),
     path("ingredientes/", views.IngredienteListView.as_view(), name="lista_ingredientes"),
]
