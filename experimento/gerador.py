"""Gerador do mecanismo causal.

O ponto central: a fraude F e' LATENTE e nao observavel. As evidencias
documentais sao sinais ruidosos dela. A taxa de falso-positivo da evidencia
de ENDERECO cresce onde a cobertura do cadastro territorial e' baixa --
e a taxa de fraude e' IDENTICA em todas as RAs por construcao, de modo que
qualquer disparidade territorial observada e' artefato da qualidade da
fonte, nunca da populacao.
"""
from dataclasses import dataclass, field
import numpy as np

RAS = ["Plano Piloto", "Águas Claras", "Guará", "Taguatinga",
       "Gama", "Sobradinho", "Samambaia", "Ceilândia"]

# Cobertura do cadastro territorial por RA.
# ESTIPULADO, nao medido -- ver Etapa 3a do plano (buscar dado real no
# Geoportal/SEDUH). A varredura de beta e' a defesa contra esta escolha.
COBERTURA = np.array([0.97, 0.94, 0.90, 0.84, 0.76, 0.70, 0.62, 0.55])

EVIDENCIAS = ["status", "endereco", "valor"]
IDX_ENDERECO = 1


@dataclass(frozen=True)
class Params:
    pi: float = 0.15                 # P(F=1), igual em toda RA
    f_base: float = 0.16             # falso-positivo base das evidencias
    beta: float = 0.55               # quanto a falta de cobertura infla o FP de endereco
    sens: tuple = (0.65, 0.70, 0.60)  # P(E_j=1 | F=1)
    cobertura: np.ndarray = field(default_factory=lambda: COBERTURA)

    @property
    def sens_arr(self):
        return np.asarray(self.sens)

    def fpr_por_ra(self, ra):
        """P(E_j=1 | F=0) para cada caso. So o endereco depende da RA."""
        f = np.full((len(ra), 3), self.f_base, dtype=float)
        f[:, IDX_ENDERECO] = self.f_base + self.beta * (1.0 - self.cobertura[ra])
        return np.clip(f, 0.0, 0.95)

    def fpr_global(self):
        """O que um modelo que ignora territorio enxerga: a media marginal."""
        f = np.full(3, self.f_base, dtype=float)
        f[IDX_ENDERECO] = self.f_base + self.beta * (1.0 - self.cobertura.mean())
        return np.clip(f, 0.0, 0.95)


def gerar(n, params, rng):
    """Retorna (ra, F, E, f_true). F e' latente; so E e ra sao observaveis."""
    ra = rng.integers(0, len(params.cobertura), size=n)
    F = (rng.random(n) < params.pi).astype(np.int8)
    f_true = params.fpr_por_ra(ra)
    p = np.where(F[:, None] == 1, params.sens_arr[None, :], f_true)
    E = (rng.random((n, 3)) < p).astype(np.int8)
    return ra, F, E, f_true
