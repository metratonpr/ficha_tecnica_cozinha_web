from django.contrib import admin
from .models import FuncaoEquipe

@admin.register(FuncaoEquipe)
class FuncaoEquipeAdmin(admin.ModelAdmin):
    list_display = ("nome", "valor_hora_padrao")
    search_fields = ("nome",)
