from django.contrib import admin
from django.utils.formats import number_format
from django.utils.html import format_html
from .models import Categoria, Ingrediente, Receita, ItemReceita, ComponenteReceita


# ------------------- INLINES -------------------

class ItemInline(admin.TabularInline):
    """Permite editar os ingredientes diretamente dentro da receita."""
    model = ItemReceita
    extra = 1


class ComponenteInline(admin.TabularInline):
    """Permite adicionar sub-receitas dentro de uma receita principal."""
    model = ComponenteReceita
    fk_name = "receita"
    extra = 0


# ------------------- CATEGORIA -------------------

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Admin para categorias de receitas."""
    list_display = ("nome", "descricao")
    search_fields = ("nome",)


# ------------------- INGREDIENTE -------------------

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    """
    Admin de ingredientes com preview da foto
    e formatação do custo por unidade.
    """
    list_display = ("foto_preview", "nome", "unidade_base", "custo_por_unidade_formatado")
    search_fields = ("nome",)
    readonly_fields = ("foto_preview",)

    def foto_preview(self, obj):
        """Mostra miniatura da imagem no admin."""
        if obj.foto:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:6px"/>', obj.foto.url)
        return "(sem imagem)"
    foto_preview.short_description = "Foto"

    def custo_por_unidade_formatado(self, obj):
        """Formata o custo com símbolo de moeda."""
        return f"R$ {number_format(obj.custo_por_unidade, decimal_pos=2, use_l10n=True)}"
    custo_por_unidade_formatado.short_description = "Custo por unidade"


# ------------------- RECEITA -------------------

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    """
    Admin completo da ficha técnica (receita).
    Exibe custos, porções e imagem do preparo.
    """
    list_display = (
        "foto_preview",
        "titulo",
        "categoria",
        "custo_total_formatado",
        "numero_porcoes_formatado",
        "custo_por_porcao_formatado",
    )
    search_fields = ("titulo", "categoria__nome")
    list_filter = ("categoria",)
    inlines = [ItemInline, ComponenteInline]

    readonly_fields = (
        "foto_preview",
        "custo_total_formatado",
        "numero_porcoes_formatado",
        "custo_por_porcao_formatado",
    )

    fieldsets = (
        ("Identificação", {
            "fields": ("titulo", "categoria", "disciplina", "tipo_coccao")
        }),
        ("Preparo e Foto", {
            "fields": ("foto_preparo", "foto_preview", "modo_preparo", "observacoes")
        }),
        ("Rendimento e Custos", {
            "fields": (
                "rendimento_total",
                "unidade_rendimento",
                "peso_por_porcao",
                "custo_total_formatado",
                "numero_porcoes_formatado",
                "custo_por_porcao_formatado",
            )
        }),
    )

    # ------------------- CAMPOS FORMATADOS -------------------

    def foto_preview(self, obj):
        """Mostra uma miniatura da foto do preparo."""
        if obj.foto_preparo:
            return format_html('<img src="{}" width="90" height="90" style="object-fit:cover;border-radius:6px"/>', obj.foto_preparo.url)
        return "(sem imagem)"
    foto_preview.short_description = "Imagem do preparo"

    def custo_total_formatado(self, obj):
        """Formata custo total com símbolo monetário."""
        return f"R$ {number_format(obj.custo_total, decimal_pos=2, use_l10n=True)}"
    custo_total_formatado.short_description = "Custo total"

    def custo_por_porcao_formatado(self, obj):
        """Formata custo por porção."""
        return f"R$ {number_format(obj.custo_por_porcao, decimal_pos=2, use_l10n=True)}"
    custo_por_porcao_formatado.short_description = "Custo por porção"

    def numero_porcoes_formatado(self, obj):
        """Mostra número de porções formatado."""
        return number_format(obj.numero_porcoes, decimal_pos=0, use_l10n=True)
    numero_porcoes_formatado.short_description = "Nº porções"
