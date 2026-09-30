"""Constantes compartilhadas do experimento: caminhos, tamanho da simulacao,
grades da varredura, configuracao de referencia e limiares pre-registrados.

Fonte unica: varredura.py, equidade.py e os scripts de figura importam daqui,
em vez de copiar os valores a mao. Mudar qualquer valor muda numero
publicado -- rode o pipeline duas vezes e declare a mudanca no commit.
"""
import csv
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
FIG = os.path.join(RAIZ, "figuras")

N = 40_000            # casos por simulacao
K = 0.10              # orcamento do analista: fracao dos casos revisada
SEMENTES = range(8)
GRADE_BETA = (0.25, 0.40, 0.55, 0.70)
GRADE_PI = (0.05, 0.10, 0.15, 0.25)

# Config de referencia, usada nas figuras e na tabela por RA
REF_BETA, REF_PI, REF_RUIDO = 0.55, 0.15, 0.16

# Criterio (ii), declarado antes de rodar: corr(cobertura, FPR entre inocentes)
LIMIAR_CORR_RULE = -0.5   # RULE_CNT abaixo disto: a disparidade existe
LIMIAR_CORR_B = -0.10     # B em ou acima disto: a disparidade foi corrigida


def eh_referencia(f_base, beta, pi):
    """True se (f_base, beta, pi) e' a configuracao de referencia."""
    return (abs(f_base - REF_RUIDO) < 1e-6 and abs(beta - REF_BETA) < 1e-6
            and abs(pi - REF_PI) < 1e-6)


def veredito(ok):
    """Rotulo impresso ao lado de cada criterio de aceitacao."""
    return "PASSA" if ok else "FALHA"


def ler(nome):
    """Le resultados/<nome> como lista de dicts (valores em texto)."""
    with open(os.path.join(RES, nome), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))
