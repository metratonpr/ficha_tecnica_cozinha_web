from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Receita, Categoria, Ingrediente


class ReceitaListView(ListView):
    """
    Exibe a lista paginada de fichas técnicas de receitas (padrão SENAC).
    Permite filtrar por categoria via ?categoria=<id>.
    """
    model = Receita
    template_name = "fichas/lista_fichas.html"
    context_object_name = "receitas"
    paginate_by = 10

    def get_queryset(self):
        """
        Filtra e ordena receitas por categoria e título.
        """
        queryset = Receita.objects.select_related("categoria").order_by("categoria__nome", "titulo")
        categoria_id = self.request.GET.get("categoria")

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adiciona lista de categorias e filtro ativo ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all().order_by("nome")
        context["categoria_selecionada"] = self.request.GET.get("categoria")
        return context


class ReceitaDetailView(DetailView):
    """
    Exibe a ficha técnica completa (modelo SENAC), com:
    - Ingredientes detalhados
    - Sub-receitas (componentes)
    - Custos total e por porção
    - Rendimento e preparo
    """
    model = Receita
    template_name = "fichas/ficha.html"
    context_object_name = "receita"

    def get_context_data(self, **kwargs):
        """
        Adiciona itens, componentes e cálculos ao contexto da ficha.
        """
        context = super().get_context_data(**kwargs)
        receita = self.object

        # Ingredientes da receita
        context["itens"] = receita.itens.select_related("ingrediente")

        # Sub-receitas (componentes)
        context["componentes"] = receita.componentes.select_related("sub_receita")

        # Cálculos de custo
        context["custo_total"] = receita.custo_total
        context["numero_porcoes"] = receita.numero_porcoes
        context["custo_por_porcao"] = receita.custo_por_porcao

        return context

class IngredienteListView(ListView):
    """
    Exibe a lista simples de ingredientes com nome, unidade e custo.
    """
    model = Ingrediente
    template_name = "fichas/lista_ingredientes.html"
    context_object_name = "ingredientes"
    ordering = ["nome"]
    paginate_by = 20