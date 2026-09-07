"""Os seis bracos comparados.

RULE_OR   regra binaria (OR das evidencias) -- nao ordena, incluida para
          mostrar que triagem sob orcamento exige score e nao rotulo
RULE_CNT  contagem de flags -- baseline ordinal justo
LOOKUP    P(F | padrao de flags) empirico -- teto nao-parametrico do que
          3 flags binarias entregam SEM territorio
A         Fellegi-Sunter com FPR global: RA ignorada
B         RA na VEROSSIMILHANCA: FPR de endereco especifico da regiao
C         RA no PRIOR: prior calibrado na taxa de inconsistencia observada
          da regiao -- o padrao que produz redlining
"""
import numpy as np

BRACOS = ("RULE_OR", "RULE_CNT", "LOOKUP", "A", "B", "C")
EPS = 1e-9


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def log_lr(E, sens, fpr):
    """Soma dos log da razao de verossimilhanca por evidencia.
    Presente -> log(s/f); ausente -> log((1-s)/(1-f))."""
    s = np.clip(np.broadcast_to(sens, E.shape), EPS, 1 - EPS)
    f = np.clip(np.broadcast_to(fpr, E.shape), EPS, 1 - EPS)
    return np.where(E == 1, np.log(s / f), np.log((1 - s) / (1 - f))).sum(axis=1)


def lookup(E, F):
    """P(F | padrao) estimado nos proprios dados. E' um teto: usa o rotulo
    latente, que na pratica nao existe. Serve para mostrar quanta informacao
    as 3 flags carregam, sem territorio."""
    codigo = E.astype(int) @ np.array([1, 2, 4])
    out = np.zeros(len(E), dtype=float)
    for c in range(8):
        m = codigo == c
        if m.any():
            out[m] = F[m].mean()
    return out


def calcular(ra, F, E, f_true, params):
    """Retorna {nome_do_braco: score em [0,1]}."""
    sens = params.sens_arr
    f_glob = params.fpr_global()
    log_prior = np.log(params.pi / (1 - params.pi))

    observado = E.max(axis=1)
    taxa_ra = np.array([observado[ra == r].mean() if (ra == r).any() else params.pi
                        for r in range(len(params.cobertura))])
    taxa_ra = np.clip(taxa_ra, 0.01, 0.99)
    prior_c = taxa_ra[ra]

    return {
        "RULE_OR":  observado.astype(float),
        "RULE_CNT": E.sum(axis=1) / 3.0,
        "LOOKUP":   lookup(E, F),
        "A": _sigmoid(log_prior + log_lr(E, sens, f_glob)),
        "B": _sigmoid(log_prior + log_lr(E, sens, f_true)),
        "C": _sigmoid(np.log(prior_c / (1 - prior_c)) + log_lr(E, sens, f_glob)),
    }
