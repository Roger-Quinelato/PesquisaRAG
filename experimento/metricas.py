"""Metricas de calibracao e de utilidade decisoria sob orcamento."""
import numpy as np


def brier(p, y):
    return float(np.mean((p - y) ** 2))


def ece(p, y, bins=10):
    """Expected Calibration Error, bins de largura igual."""
    edges = np.linspace(0.0, 1.0, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    total = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(total)


def topk_desempate(score, k, u):
    """Indices dos k*n maiores. Empates desfeitos pelo vetor aleatorio `u`, ja
    sorteado -- essencial, porque um score binario empata em massa e ordenacao
    estavel o favoreceria artificialmente. Receber `u` pronto (de fluxos.py)
    permite desempatar um braco sem rodar os outros."""
    tamanho = max(1, int(round(k * len(score))))
    return np.lexsort((u, -score))[:tamanho]


def topk(score, k, rng):
    """Mesmo que topk_desempate, sorteando `u` do rng na hora."""
    return topk_desempate(score, k, rng.random(len(score)))


def precisao_topk_desempate(score, y, k, u):
    sel = topk_desempate(score, k, u)
    return float(y[sel].mean()), sel


def precisao_topk(score, y, k, rng):
    sel = topk(score, k, rng)
    return float(y[sel].mean()), sel


def fpr_por_ra(sel, ra, y, n, n_ras):
    """Entre os NAO-fraudes de cada RA, fracao mandada a revisao humana.
    E' a metrica de equidade: mede quem paga o custo do falso positivo."""
    marcado = np.zeros(n, dtype=bool)
    marcado[sel] = True
    out = np.full(n_ras, np.nan)
    for r in range(n_ras):
        m = (ra == r) & (y == 0)
        if m.any():
            out[r] = marcado[m].mean()
    return out
