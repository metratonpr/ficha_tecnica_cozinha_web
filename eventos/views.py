from collections import defaultdict
from decimal import Decimal
from django.views.generic import ListView, DetailView
from fichas.models import Ingrediente
from .models import Evento


# ---------------------------------------------------------------------
# 📅 LISTA DE EVENTOS
# ---------------------------------------------------------------------
class EventoListView(ListView):
    """
    Exibe a lista de eventos cadastrados, ordenados por data (mais recentes primeiro).
    """
    model = Evento
    template_name = "eventos/lista_eventos.html"
    context_object_name = "eventos"
    paginate_by = 10
    ordering = ["-data"]

    def get_queryset(self):
        """
        Permite filtrar eventos por nome (busca simples).
        """
        queryset = super().get_queryset()
        busca = self.request.GET.get("q")
        if busca:
            queryset = queryset.filter(nome__icontains=busca)
        return queryset


# ---------------------------------------------------------------------
# 📋 DETALHE DO EVENTO + LISTA DE COMPRAS
# ---------------------------------------------------------------------
class EventoDetailView(DetailView):
    """
    Exibe os detalhes completos de um evento (ficha técnica e lista de compras).
    """
    model = Evento
    template_name = "eventos/evento.html"
    context_object_name = "evento"

    def get_context_data(self, **kwargs):
        from fichas.models import ItemReceita  # evita import circular
        context = super().get_context_data(**kwargs)
        evento = self.object

        context["itens"] = evento.itens.select_related("receita")
        context["participacoes"] = evento.participacoes.select_related("funcao")

        # ------------------------------------------------------
        # 🧾 LISTA DE COMPRAS (precisa de Decimal para precisão)
        # ------------------------------------------------------
        lista = defaultdict(lambda: {
            "quantidade": Decimal("0.0"),
            "unidade": "",
            "custo_unit": Decimal("0.0")
        })

        for item_evento in evento.itens.all():
            receita = item_evento.receita
            rendimento = receita.rendimento_total or Decimal("1.0")

            # fator = porções por pessoa × nº de pessoas ÷ rendimento da receita
            fator = (
                Decimal(item_evento.porcoes_por_pessoa or 0)
                * Decimal(evento.numero_pessoas or 0)
                / Decimal(rendimento)
            )

            # Ingredientes diretos
            for item in receita.itens.select_related("ingrediente"):
                ing = item.ingrediente
                if not ing:
                    continue

                peso_liquido = Decimal(item.peso_liquido or 0)
                custo_unit = Decimal(ing.custo_por_unidade or 0)

                lista[ing.nome]["quantidade"] += peso_liquido * fator
                lista[ing.nome]["unidade"] = ing.unidade_base
                lista[ing.nome]["custo_unit"] = custo_unit

            # Sub-receitas (componentes)
            for componente in receita.componentes.select_related("sub_receita"):
                sub = componente.sub_receita
                if sub and sub.rendimento_total:
                    fator_sub = (
                        fator * Decimal(componente.quantidade or 0)
                        / Decimal(sub.rendimento_total)
                    )
                    for sub_item in sub.itens.select_related("ingrediente"):
                        ing = sub_item.ingrediente
                        if not ing:
                            continue

                        peso_liquido = Decimal(sub_item.peso_liquido or 0)
                        custo_unit = Decimal(ing.custo_por_unidade or 0)

                        lista[ing.nome]["quantidade"] += peso_liquido * fator_sub
                        lista[ing.nome]["unidade"] = ing.unidade_base
                        lista[ing.nome]["custo_unit"] = custo_unit

        # Converte o dicionário em lista ordenada
        context["lista_compras"] = [
            {
                "ingrediente": nome,
                "quantidade": round(data["quantidade"], 3),
                "unidade": data["unidade"],
                "custo_total": round(data["quantidade"] * data["custo_unit"], 2),
            }
            for nome, data in sorted(lista.items())
        ]

        return context
