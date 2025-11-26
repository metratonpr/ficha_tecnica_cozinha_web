from django.urls import path
from . import views

app_name = "eventos"

urlpatterns = [
    # Página principal — lista todos os eventos
    path("", views.EventoListView.as_view(), name="lista_eventos"),

    # Detalhe de um evento específico
    path("<int:pk>/", views.EventoDetailView.as_view(), name="detalhe_evento"),
]
