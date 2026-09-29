"""Toda a aleatoriedade de uma semente, sorteada de uma vez e na ordem historica.

O experimento sempre consumiu um unico rng por semente, nesta ordem:

    1. gerar (integers, random, random)          -- os dados
    2. random(N) por braco fechado, na ordem de BRACOS   -- desempate do topk
    3. random(N) para o split treino/teste
    4. 3 x integers(0, 2**32 - 1)                -- sementes do AdaBoost D, E, F
    5. random(n_teste) por braco de BRACOS_ML, na ordem da tupla  -- desempate

Os tamanhos de todos os sorteios sao conhecidos sem calcular nenhum modelo.
Entao `fluxos` refaz essa sequencia inteira (so gerar numeros aleatorios,
custo desprezivel) e entrega cada vetor ao braco dono dele. Com isso qualquer
familia de bracos roda isolada e sai bit a bit igual a quando roda junto com
as outras -- e igual a todas as rodadas anteriores.

Consequencia que continua valendo: braco novo so entra no FIM de BRACOS ou de
BRACOS_ML, e nenhum braco e' removido (um aposentado mantem o slot, porque o
sorteio dele continua sendo consumido).
"""
from dataclasses import dataclass

import numpy as np

from gerador import gerar
from bracos import BRACOS
from bracos_ml import BRACOS_ML, FRAC_TREINO


@dataclass(frozen=True)
class Fluxos:
    ra: np.ndarray
    F: np.ndarray
    E: np.ndarray
    f_true: np.ndarray
    treino: np.ndarray          # mascara booleana do split
    sementes: tuple             # sementes inteiras do AdaBoost D, E, F
    desempate: dict             # braco -> vetor uniforme do topk


def fluxos(semente, params, n):
    rng = np.random.default_rng(semente)
    ra, F, E, f_true = gerar(n, params, rng)
    desempate = {b: rng.random(n) for b in BRACOS}
    treino = rng.random(n) < FRAC_TREINO
    sementes = tuple(int(rng.integers(0, 2**32 - 1)) for _ in range(3))
    n_teste = int((~treino).sum())
    desempate.update({b: rng.random(n_teste) for b in BRACOS_ML})
    return Fluxos(ra, F, E, f_true, treino, sementes, desempate)
