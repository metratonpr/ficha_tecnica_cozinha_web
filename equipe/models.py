from decimal import Decimal
from django.db import models

class FuncaoEquipe(models.Model):
    """Catálogo de funções/cargos (sem vínculo com eventos)."""
    nome = models.CharField(max_length=100, unique=True)
    valor_hora_padrao = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal("20.00"),
        help_text="Valor/hora padrão dessa função"
    )

    def __str__(self):
        return f"{self.nome} (R$ {self.valor_hora_padrao}/h)"
