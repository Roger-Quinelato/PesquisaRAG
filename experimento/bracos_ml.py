"""Tres bracos discriminativos (AdaBoost), analogos a A/B/C.

D_ML  RA ausente das features                          (espelha A)
E_ML  RA como feature de decisao, one-hot de 8 colunas  (espelha B)
F_ML  so a taxa de inconsistencia observada da RA       (espelha C)

Diferente dos seis bracos fechados de bracos.py, estes sao treinados: a
amostra de cada configuracao e' dividida em treino e teste, e as metricas
saem so do teste. Unico modulo do experimento que depende de scikit-learn
(excecao documentada no CLAUDE.md).

E_ML recebe so a identidade da RA e precisa aprender o efeito dela; B recebe
o FPR verdadeiro do gerador. E_ML e', portanto, mais realista que B.
predict_proba devolve valores em [0,1], mas nao e' uma calibracao garantida:
o ECE destes bracos mede tambem a forma do score do boosting.
"""
import numpy as np
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier

BRACOS_ML = ("D_ML", "E_ML", "F_ML")
FRAC_TREINO = 0.5
# Fixos e pre-registrados, nao ajustados por configuracao. O stump e' explicito
# para nao depender do default da versao; desde o scikit-learn 1.8 o AdaBoost
# so implementa SAMME (o parametro `algorithm` foi removido).
N_ESTIMADORES = 100
TAXA_APRENDIZADO = 1.0


def _ajustar(X, y, semente):
    return AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1),
                              n_estimators=N_ESTIMADORES,
                              learning_rate=TAXA_APRENDIZADO,
                              random_state=semente).fit(X, y)


def calcular_ml(ra, F, E, params, rng):
    """Retorna (scores_teste, idx_teste). scores_teste[nome] tem shape
    (n_teste,), alinhado a idx_teste: as metricas devem usar F[idx_teste]
    e ra[idx_teste], nunca os arrays completos.

    Consome o rng em ordem fixa: 1 sorteio para o split, 3 sementes
    (D_ML, E_ML, F_ML). O scikit-learn recebe inteiros, entao os sorteios
    internos dele nao consomem o rng do experimento."""
    treino = rng.random(len(F)) < FRAC_TREINO
    idx_treino, idx_teste = np.flatnonzero(treino), np.flatnonzero(~treino)
    semente_d, semente_e, semente_f = (int(rng.integers(0, 2**32 - 1)) for _ in range(3))

    Et, Es = E[idx_treino], E[idx_teste]
    rat, ras = ra[idx_treino], ra[idx_teste]
    Ft = F[idx_treino]
    n_ras = len(params.cobertura)

    onehot = np.eye(n_ras)
    Xe_tr, Xe_te = np.hstack([Et, onehot[rat]]), np.hstack([Es, onehot[ras]])

    # Mesma formula de taxa_ra usada por C em bracos.calcular, mas estimada
    # so no treino, para a feature do caso de teste nao depender do proprio teste.
    obs_tr = Et.max(axis=1)
    taxa_ra = np.array([obs_tr[rat == r].mean() if (rat == r).any() else params.pi
                        for r in range(n_ras)])
    taxa_ra = np.clip(taxa_ra, 0.01, 0.99)
    Xf_tr, Xf_te = np.hstack([Et, taxa_ra[rat][:, None]]), np.hstack([Es, taxa_ra[ras][:, None]])

    scores_teste = {
        "D_ML": _ajustar(Et, Ft, semente_d).predict_proba(Es)[:, 1],
        "E_ML": _ajustar(Xe_tr, Ft, semente_e).predict_proba(Xe_te)[:, 1],
        "F_ML": _ajustar(Xf_tr, Ft, semente_f).predict_proba(Xf_te)[:, 1],
    }
    return scores_teste, idx_teste
