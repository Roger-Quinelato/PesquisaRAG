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

A, B e C sao Fellegi-Sunter: prior em log-odds mais a soma das log-razoes de
verossimilhanca por evidencia. Isso e' exatamente um Naive Bayes de Bernoulli
com parametros conhecidos, entao sao escritos com o BernoulliNB do
scikit-learn, com os parametros do gerador injetados em vez de ajustados. Nao
ha treino: nenhum deles usa o rotulo F. Em relacao a formula direta em numpy,
os scores diferem so no arredondamento (~1e-16), e a ordenacao nao muda.
"""
import numpy as np
from sklearn.naive_bayes import BernoulliNB

BRACOS = ("RULE_OR", "RULE_CNT", "LOOKUP", "A", "B", "C")
EPS = 1e-9


def _nb_fixo(sens, fpr, prior):
    """BernoulliNB com parametros dados, sem fit. Classe 0 = sem fraude
    (P(E_j=1) = fpr_j), classe 1 = fraude (P(E_j=1) = sens_j)."""
    nb = BernoulliNB(binarize=None)
    nb.classes_ = np.array([0, 1])
    nb.class_log_prior_ = np.log([1 - prior, prior])
    nb.feature_log_prob_ = np.log(np.clip(np.vstack([fpr, sens]), EPS, 1 - EPS))
    nb.n_features_in_ = len(sens)
    return nb


def _por_ra(E, ra, n_ras, modelo_da_ra):
    """P(F=1|E) com um modelo por RA, aplicado so aos casos daquela RA."""
    out = np.empty(len(E), dtype=float)
    for r in range(n_ras):
        m = ra == r
        if m.any():
            out[m] = modelo_da_ra(r).predict_proba(E[m])[:, 1]
    return out


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
    n_ras = len(params.cobertura)

    observado = E.max(axis=1)
    taxa_ra = np.array([observado[ra == r].mean() if (ra == r).any() else params.pi
                        for r in range(n_ras)])
    taxa_ra = np.clip(taxa_ra, 0.01, 0.99)

    # f_true so varia com a RA do caso, entao B e' um modelo por RA com o FPR
    # verdadeiro daquela regiao; C e' um modelo por RA com o prior taxa_ra[r].
    return {
        "RULE_OR":  observado.astype(float),
        "RULE_CNT": E.sum(axis=1) / 3.0,
        "LOOKUP":   lookup(E, F),
        "A": _nb_fixo(sens, f_glob, params.pi).predict_proba(E)[:, 1],
        "B": _por_ra(E, ra, n_ras,
                     lambda r: _nb_fixo(sens, params.fpr_por_ra(np.array([r]))[0], params.pi)),
        "C": _por_ra(E, ra, n_ras, lambda r: _nb_fixo(sens, f_glob, taxa_ra[r])),
    }
