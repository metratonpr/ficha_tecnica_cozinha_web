from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("fichas/", include("fichas.urls")),
    path("eventos/", include("eventos.urls")),  # 👈 Adiciona o app de eventos
    path("", RedirectView.as_view(url="/fichas/", permanent=False)),  # redireciona raiz
]

# Exibe imagens (media) no modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
