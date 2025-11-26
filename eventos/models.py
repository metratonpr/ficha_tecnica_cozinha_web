from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from fichas.models import Receita
from equipe.models import FuncaoEquipe


# ------------------- Função utilitária -------------------
def q(value, places=2):
    """Arredonda valores decimais com precisão definida."""
    if value is None:
        return None
    return Decimal(value).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)


# ------------------- Modelo principal -------------------
class Evento(models.Model):
    """
    Representa um evento gastronômico.
    Contém receitas, equipe e custos associados.
    Baseado no padrão de Ficha Técnica SENAC.
    """
    nome = models.CharField(max_length=150)
    data = models.DateField()
    numero_pessoas = models.PositiveIntegerField()
    custo_indireto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2, default=30)

    def __str__(self):
        """Retorna o nome do evento e o número de pessoas."""
        return f"{self.nome} ({self.numero_pessoas} pessoas)"

    # ------------------- CÁLCULOS DE CUSTOS -------------------

    @property
    def custo_receitas(self):
        """Soma o custo total das receitas associadas ao evento."""
        return sum(
            [(i.custo_total or Decimal("0.00")) for i in self.itens.all()],
            Decimal("0.00")
        )

    @property
    def custo_mao_obra_total(self):
        """Soma o custo total da equipe envolvida no evento."""
        return sum(
            [(p.custo_total or Decimal("0.00")) for p in self.participacoes.all()],
            Decimal("0.00")
        )

    @property
    def custo_total(self):
        """Custo total (receitas + equipe + custos indiretos)."""
        return q(self.custo_receitas + self.custo_mao_obra_total + self.custo_indireto, 2)

    @property
    def preco_venda_total(self):
        """Preço total de venda considerando a margem de lucro."""
        return q(self.custo_total * (1 + (self.margem_lucro / 100)), 2)

    @property
    def lucro_estimado(self):
        """Lucro total estimado (preço - custo)."""
        return q(self.preco_venda_total - self.custo_total, 2)

    # ------------------- CAMPOS PADRÃO SENAC -------------------

    @property
    def custo_por_pessoa(self):
        """Custo médio por pessoa — padrão SENAC."""
        if self.numero_pessoas and self.numero_pessoas > 0:
            return q(self.custo_total / Decimal(self.numero_pessoas), 2)
        return Decimal("0.00")

    @property
    def preco_venda_por_pessoa(self):
        """Preço médio de venda por pessoa — padrão SENAC."""
        if self.numero_pessoas and self.numero_pessoas > 0:
            return q(self.preco_venda_total / Decimal(self.numero_pessoas), 2)
        return Decimal("0.00")


# ------------------- Item de Cardápio -------------------
class ItemCardapio(models.Model):
    """
    Associa uma receita ao evento, com porções e foto opcional.
    Permite registrar visualmente o prato servido.
    """
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="itens")
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE)
    porcoes_por_pessoa = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    foto_item = models.ImageField(
        upload_to="itens_cardapio/", blank=True, null=True,
        help_text="Foto do prato servido no evento (opcional)."
    )

    def __str__(self):
        """Nome amigável para exibição."""
        return f"{self.receita.titulo} no evento {self.evento.nome}"

    @property
    def custo_total(self):
        """Cálculo do custo total da receita para o evento."""
        if self.receita.custo_por_porcao:
            return q(
                self.receita.custo_por_porcao * self.evento.numero_pessoas * self.porcoes_por_pessoa,
                2
            )
        return Decimal("0.00")


# ------------------- Participação da Equipe -------------------
class ParticipacaoEquipe(models.Model):
    """
    Representa a participação de membros da equipe em um evento.
    Utiliza o valor hora da função ou valor personalizado.
    """
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="participacoes")
    funcao = models.ForeignKey(FuncaoEquipe, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)
    horas = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        """Exibe a função e evento de forma legível."""
        return f"{self.quantidade}x {self.funcao.nome} em {self.evento.nome}"

    @property
    def custo_unitario(self):
        """Custo unitário por participante (função x horas)."""
        valor = self.valor_hora or self.funcao.valor_hora_padrao
        return q(self.horas * valor, 2)

    @property
    def custo_total(self):
        """Custo total considerando a quantidade e horas."""
        return q(self.custo_unitario * self.quantidade, 2)
