"""Metricas de calibracao e de utilidade decisoria sob orcamento."""
import numpy as np

BINS = 10


def brier(p, y):
    return float(np.mean((p - y) ** 2))


def bins_ece(p, bins=BINS):
    """Indice do bin de cada probabilidade: bins de largura igual em [0, 1].
    Usado por ece() e pelo diagrama de confiabilidade, que assim nao tem
    como divergir do numero publicado."""
    edges = np.linspace(0.0, 1.0, bins + 1)
    return np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)


def ece(p, y, bins=BINS):
    """Expected Calibration Error, bins de largura igual."""
    idx = bins_ece(p, bins)
    total = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(total)


def topk(score, k, rng):
    """Indices dos k*n maiores. Empates desfeitos aleatoriamente -- essencial,
    porque um score binario empata em massa e ordenacao estavel o favoreceria
    artificialmente."""
    n = len(score)
    tamanho = max(1, int(round(k * n)))
    return np.lexsort((rng.random(n), -score))[:tamanho]


def precisao_topk(score, y, k, rng):
    sel = topk(score, k, rng)
    return float(y[sel].mean()), sel


def fpr_por_ra(sel, ra, y, n_ras):
    """Entre os NAO-fraudes de cada RA, fracao mandada a revisao humana.
    E' a metrica de equidade: mede quem paga o custo do falso positivo."""
    marcado = np.zeros(len(ra), dtype=bool)
    marcado[sel] = True
    out = np.full(n_ras, np.nan)
    for r in range(n_ras):
        m = (ra == r) & (y == 0)
        if m.any():
            out[r] = marcado[m].mean()
    return out
