from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from django.db import models


# ------------------- Função utilitária -------------------
def q(value, places=2):
    """Arredonda valores decimais com precisão configurável."""
    return (Decimal(value).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
            if value is not None else None)


# ------------------- Unidades -------------------
class Unidade(models.TextChoices):
    """Enum de unidades de medida — padrão SENAC."""
    # Peso
    KG = "kg", "Quilo (kg)"
    G = "g", "Grama (g)"
    MG = "mg", "Miligrama (mg)"

    # Volume
    L = "l", "Litro (l)"
    DL = "dl", "Decilitro (dl)"
    CL = "cl", "Centilitro (cl)"
    ML = "ml", "Mililitro (ml)"

    # Medidas caseiras (aproximadas)
    CS = "cs", "Colher de sopa (~15 ml)"
    CC = "cc", "Colher de chá (~5 ml)"
    XIC = "xic", "Xícara (~240 ml)"
    PT = "pt", "Pitada"
    GT = "gt", "Gota"

    # Unidades
    UND = "und", "Unidade"
    DZ = "dz", "Dúzia"

    # Outros
    QB = "qb", "Quanto baste (q.b.)"


# Conversões básicas + aproximações culinárias
CONVERSOES = {
    # peso
    ("kg", "g"): Decimal("1000"),
    ("g", "kg"): Decimal("0.001"),
    ("g", "mg"): Decimal("1000"),
    ("mg", "g"): Decimal("0.001"),

    # volume
    ("l", "ml"): Decimal("1000"),
    ("ml", "l"): Decimal("0.001"),
    ("l", "dl"): Decimal("10"),
    ("dl", "l"): Decimal("0.1"),
    ("dl", "cl"): Decimal("10"),
    ("cl", "dl"): Decimal("0.1"),
    ("cl", "ml"): Decimal("10"),
    ("ml", "cl"): Decimal("0.1"),

    # medidas caseiras (aproximadas em ml)
    ("cs", "ml"): Decimal("15"),
    ("cc", "ml"): Decimal("5"),
    ("xic", "ml"): Decimal("240"),

    # aproximações culinárias comuns
    ("und_cebola", "kg"): Decimal("0.15"),   # 1 cebola média = 150 g
    ("und_alho", "kg"): Decimal("0.005"),    # 1 dente de alho = 5 g
    ("und_ovo", "kg"): Decimal("0.050"),     # 1 ovo médio = 50 g
}


def converter(qtd, de, para):
    """Converte quantidade entre unidades conhecidas."""
    if de == para:
        return qtd
    fator = CONVERSOES.get((de, para))
    if fator is None:
        raise ValidationError(f"Sem conversão direta de {de} para {para}")
    return (qtd * fator) if qtd is not None else None


# ------------------- Categoria -------------------
class Categoria(models.Model):
    """Classificação geral das receitas."""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.nome


# ------------------- Ingrediente -------------------
class Ingrediente(models.Model):
    """Cadastro de ingredientes com unidade base e custo."""
    nome = models.CharField(max_length=150, unique=True)
    unidade_base = models.CharField(max_length=5, choices=Unidade.choices, default=Unidade.KG)
    custo_por_unidade = models.DecimalField(max_digits=12, decimal_places=4)
    foto = models.ImageField(upload_to="ingredientes/", blank=True, null=True,
                             help_text="Foto ilustrativa do ingrediente")  # ✅ NOVO

    def __str__(self):
        return self.nome


# ------------------- Receita -------------------
class Receita(models.Model):
    """Ficha técnica padrão SENAC: define ingredientes, preparo e custo."""
    titulo = models.CharField(max_length=160)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="receitas")
    disciplina = models.CharField(max_length=120, blank=True, help_text="Ex.: Cozinha Fria, Padaria")
    tipo_coccao = models.CharField(max_length=120, blank=True, help_text="Ex.: Processador, Assar, Cozinhar")
    tempo_coccao_min = models.PositiveIntegerField(default=0)
    tempo_preparo_min = models.PositiveIntegerField(default=0)

    foto_preparo = models.ImageField(upload_to="receitas/", blank=True, null=True,
                                     help_text="Imagem do prato final ou preparo")  # ✅ RENOMEADO
    modo_preparo = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)

    rendimento_total = models.DecimalField(max_digits=10, decimal_places=3)
    unidade_rendimento = models.CharField(max_length=5, choices=Unidade.choices, default=Unidade.KG)
    peso_por_porcao = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return self.titulo

    # --- Cálculos automáticos ---
    @property
    def custo_total(self):
        """Soma o custo dos itens e sub-receitas."""
        total = Decimal("0.0")
        for item in self.itens.all():
            total += item.custo_total or Decimal("0.0")
        for comp in self.componentes.all():
            total += comp.custo_total or Decimal("0.0")
        return q(total, 2)

    @property
    def numero_porcoes(self):
        """Calcula o número de porções baseado no peso por porção."""
        if self.peso_por_porcao and self.peso_por_porcao > 0:
            return q(self.rendimento_total / self.peso_por_porcao, 2)
        return None

    @property
    def custo_por_porcao(self):
        """Divide o custo total pelo número de porções."""
        if self.numero_porcoes and self.numero_porcoes > 0:
            return q(self.custo_total / self.numero_porcoes, 2)
        return None


# ------------------- Item de Receita -------------------
class ItemReceita(models.Model):
    """Composição de uma receita com seus ingredientes."""
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name="itens")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT)
    unidade = models.CharField(max_length=5, choices=Unidade.choices)
    peso_bruto = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    peso_liquido = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    fator_correcao = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    medida_caseira = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"{self.ingrediente} em {self.receita}"

    @property
    def quantidade_liquida(self):
        """Calcula o peso líquido considerando fator de correção."""
        if self.peso_liquido is not None:
            return self.peso_liquido
        if self.peso_bruto is not None and self.fator_correcao:
            return q(self.peso_bruto * self.fator_correcao, 3)
        return self.peso_bruto

    @property
    def custo_total(self):
        """Calcula o custo do ingrediente proporcional à quantidade usada."""
        if self.unidade == Unidade.QB or self.quantidade_liquida is None:
            return Decimal("0.00")

        qtd = Decimal(self.quantidade_liquida)
        ing = self.ingrediente

        # Se a unidade já é a base
        if self.unidade == ing.unidade_base:
            qtd_na_base = qtd
        else:
            try:
                qtd_na_base = converter(qtd, self.unidade, ing.unidade_base)
            except ValidationError:
                # fallback: assume proporção direta
                return q(qtd * ing.custo_por_unidade, 2)

        return q(qtd_na_base * ing.custo_por_unidade, 2)


# ------------------- Sub-receitas -------------------
class ComponenteReceita(models.Model):
    """Permite usar sub-receitas dentro de uma receita principal."""
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name="componentes")
    sub_receita = models.ForeignKey(Receita, on_delete=models.PROTECT, related_name="como_componente")
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    unidade = models.CharField(max_length=5, choices=Unidade.choices)

    def __str__(self):
        return f"{self.sub_receita} em {self.receita}"

    @property
    def custo_total(self):
        """Custo proporcional da sub-receita."""
        sub = self.sub_receita
        try:
            qtd_na_base = converter(self.quantidade, self.unidade, sub.unidade_rendimento)
        except ValidationError:
            qtd_na_base = self.quantidade if self.unidade == sub.unidade_rendimento else None

        if not qtd_na_base or sub.rendimento_total == 0:
            return Decimal("0.00")

        frac = Decimal(qtd_na_base) / Decimal(sub.rendimento_total)
        return q(sub.custo_total * frac, 2)
