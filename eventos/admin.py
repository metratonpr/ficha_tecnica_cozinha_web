from django.contrib import admin
from django.utils.html import format_html
from django.utils.formats import number_format
from .models import Evento, ItemCardapio, ParticipacaoEquipe


# ------------------- INLINES -------------------

class ItemCardapioInline(admin.TabularInline):
    """Permite editar receitas associadas diretamente dentro do evento."""
    model = ItemCardapio
    extra = 1
    fields = ("foto_preview", "receita", "porcoes_por_pessoa", "custo_total_formatado")
    readonly_fields = ("foto_preview", "custo_total_formatado")

    def foto_preview(self, obj):
        """Exibe miniatura da foto do prato (ou da receita se o item não tiver)."""
        if obj.foto_item:
            return format_html(
                '<img src="{}" width="70" height="70" style="object-fit:cover;border-radius:6px"/>',
                obj.foto_item.url
            )
        elif obj.receita and obj.receita.foto_preparo:
            return format_html(
                '<img src="{}" width="70" height="70" style="object-fit:cover;border-radius:6px"/>',
                obj.receita.foto_preparo.url
            )
        return "(sem imagem)"
    foto_preview.short_description = "Foto do prato"

    def custo_total_formatado(self, obj):
        """Formata o custo total do item."""
        return f"R$ {number_format(obj.custo_total, decimal_pos=2, use_l10n=True)}"
    custo_total_formatado.short_description = "Custo total"


class ParticipacaoEquipeInline(admin.TabularInline):
    """Permite editar a equipe participante diretamente dentro do evento."""
    model = ParticipacaoEquipe
    extra = 1
    fields = ("funcao", "quantidade", "horas", "valor_hora", "custo_total_formatado")
    readonly_fields = ("custo_total_formatado",)

    def custo_total_formatado(self, obj):
        """Formata o custo total da equipe."""
        return f"R$ {number_format(obj.custo_total, decimal_pos=2, use_l10n=True)}"
    custo_total_formatado.short_description = "Custo total"


# ------------------- EVENTO -------------------

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    """Admin visual e completo para gestão de eventos gastronômicos."""
    list_display = (
        "nome",
        "data",
        "numero_pessoas",
        "custo_total_formatado",
        "preco_venda_total_formatado",
        "custo_por_pessoa_formatado",
        "preco_venda_por_pessoa_formatado",
        "lucro_estimado_formatado",
    )
    list_filter = ("data",)
    search_fields = ("nome",)
    inlines = [ItemCardapioInline, ParticipacaoEquipeInline]

    readonly_fields = (
        "custo_receitas_formatado",
        "custo_mao_obra_total_formatado",
        "custo_total_formatado",
        "preco_venda_total_formatado",
        "custo_por_pessoa_formatado",
        "preco_venda_por_pessoa_formatado",
        "lucro_estimado_formatado",
    )

    fieldsets = (
        ("📅 Informações do Evento", {
            "fields": ("nome", "data", "numero_pessoas")
        }),
        ("💰 Custos e Margem de Lucro", {
            "fields": (
                "custo_receitas_formatado",
                "custo_mao_obra_total_formatado",
                "custo_indireto",
                "custo_total_formatado",
                "margem_lucro",
                "preco_venda_total_formatado",
                "custo_por_pessoa_formatado",
                "preco_venda_por_pessoa_formatado",
                "lucro_estimado_formatado",
            )
        }),
    )

    # ------------------- CAMPOS FORMATADOS -------------------

    def custo_receitas_formatado(self, obj):
        return f"R$ {number_format(obj.custo_receitas, decimal_pos=2, use_l10n=True)}"
    custo_receitas_formatado.short_description = "Custo das receitas"

    def custo_mao_obra_total_formatado(self, obj):
        return f"R$ {number_format(obj.custo_mao_obra_total, decimal_pos=2, use_l10n=True)}"
    custo_mao_obra_total_formatado.short_description = "Custo da equipe"

    def custo_total_formatado(self, obj):
        return f"R$ {number_format(obj.custo_total, decimal_pos=2, use_l10n=True)}"
    custo_total_formatado.short_description = "Custo total"

    def preco_venda_total_formatado(self, obj):
        return f"R$ {number_format(obj.preco_venda_total, decimal_pos=2, use_l10n=True)}"
    preco_venda_total_formatado.short_description = "Preço de venda total"

    def custo_por_pessoa_formatado(self, obj):
        return f"R$ {number_format(obj.custo_por_pessoa, decimal_pos=2, use_l10n=True)}"
    custo_por_pessoa_formatado.short_description = "Custo por pessoa"

    def preco_venda_por_pessoa_formatado(self, obj):
        return f"R$ {number_format(obj.preco_venda_por_pessoa, decimal_pos=2, use_l10n=True)}"
    preco_venda_por_pessoa_formatado.short_description = "Preço por pessoa"

    def lucro_estimado_formatado(self, obj):
        return f"R$ {number_format(obj.lucro_estimado, decimal_pos=2, use_l10n=True)}"
    lucro_estimado_formatado.short_description = "Lucro estimado"
