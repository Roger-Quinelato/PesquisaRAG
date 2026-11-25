"""Bracos treinados, analogos a A/B/C.

AdaBoost (discriminativo):
D_ML  RA ausente das features                          (espelha A)
E_ML  RA como feature de decisao, one-hot de 8 colunas  (espelha B)
F_ML  so a taxa de inconsistencia observada da RA       (espelha C)

Naive Bayes de Bernoulli treinado (A/B/C com parametros aprendidos do rotulo):
A_NB  RA ausente                                        (espelha A)
B_NB  verossimilhancas por RA, prior global              (espelha B)
C_NB  verossimilhancas globais, prior P(F=1|RA) por RA   (espelha C)

Diferente dos seis bracos fechados de bracos.py, estes sao treinados: a
amostra de cada configuracao e' dividida em treino e teste, e as metricas
saem so do teste. Todos usam o mesmo split.

E_ML e B_NB recebem so a identidade da RA e precisam aprender o efeito dela;
B recebe o FPR verdadeiro do gerador. C_NB difere de C de proposito: C usa a
taxa de EVIDENCIAS da RA (a unica observavel sem rotulo, que produz a dupla
contagem); C_NB usa a taxa de FRAUDE da RA, que so existe porque o treino tem
rotulo. predict_proba do AdaBoost fica em [0,1], mas nao e' uma calibracao
garantida: o ECE dele mede tambem a forma do score do boosting.

AdaBoost com calibracao posterior (o mesmo modelo de D_ML/E_ML/F_ML, sem retreino):
D_PL, E_PL, F_PL     Platt: regressao logistica sobre o decision_function
D_ISO, E_ISO, F_ISO  isotonica sobre o decision_function

Os dois calibradores sao ajustados em predicoes fora da dobra do TREINO
(validacao cruzada de 5 dobras, como CalibratedClassifierCV com ensemble=False),
entao o teste continua intocado. O Platt e' sem a suavizacao de alvo 1/(N+2) do
artigo original. O Platt preserva a ordenacao do AdaBoost; a isotonica pode
criar empates, que o topk desfaz por sorteio.
"""
import copy

import numpy as np
from sklearn.ensemble import AdaBoostClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.naive_bayes import BernoulliNB
from sklearn.tree import DecisionTreeClassifier

# Braco novo sempre no fim: a ordem define a sequencia de rng dos topk, e
# acrescentar no meio mudaria os numeros dos que vem depois.
BRACOS_ML = ("D_ML", "E_ML", "F_ML", "A_NB", "B_NB", "C_NB",
             "D_PL", "E_PL", "F_PL", "D_ISO", "E_ISO", "F_ISO")
FRAC_TREINO = 0.5
# Fixos e pre-registrados, nao ajustados por configuracao. O stump e' explicito
# para nao depender do default da versao; desde o scikit-learn 1.8 o AdaBoost
# so implementa SAMME (o parametro `algorithm` foi removido).
N_ESTIMADORES = 100
TAXA_APRENDIZADO = 1.0
N_DOBRAS = 5


def _adaboost(semente):
    return AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1),
                              n_estimators=N_ESTIMADORES,
                              learning_rate=TAXA_APRENDIZADO,
                              random_state=semente)


def _calibrados(modelo, X_tr, y_tr, X_te, semente):
    """Platt e isotonica para um AdaBoost ja ajustado em todo o treino.

    As predicoes fora da dobra vem de AdaBoosts com os mesmos hiperparametros e
    a mesma semente, um por dobra. As dobras nao embaralham, entao nada aqui
    consome o rng do experimento; a ordem do treino ja e' aleatoria (casos iid,
    split sorteado). As dobras sao independentes: n_jobs=-1 nao muda o resultado."""
    oof = cross_val_predict(_adaboost(semente), X_tr, y_tr,
                            cv=StratifiedKFold(N_DOBRAS), method="decision_function",
                            n_jobs=-1)
    s_te = modelo.decision_function(X_te)
    platt = LogisticRegression(C=np.inf).fit(oof[:, None], y_tr)
    iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip").fit(oof, y_tr)
    return platt.predict_proba(s_te[:, None])[:, 1], iso.predict(s_te)


def _naive_bayes(Et, Ft, rat, Es, ras, n_ras):
    """A_NB, B_NB e C_NB. BernoulliNB com alpha=1,0 (default, pre-registrado)
    e sem sorteio: nao consome rng."""
    # E vem em int8, e o fit soma as contagens no dtype de entrada: acima de 127
    # a contagem estoura e o modelo sai com NaN. Por isso float.
    Et, Es = Et.astype(float), Es.astype(float)
    a = BernoulliNB().fit(Et, Ft)

    pi_hat = Ft.mean()
    b = np.empty(len(Es), dtype=float)
    c = np.empty(len(Es), dtype=float)
    for r in range(n_ras):
        tr, te = rat == r, ras == r
        if not te.any():
            continue
        # B_NB: verossimilhancas aprendidas so com a RA, prior global.
        nb_r = BernoulliNB(class_prior=[1 - pi_hat, pi_hat]).fit(Et[tr], Ft[tr])
        b[te] = nb_r.predict_proba(Es[te])[:, 1]
        # C_NB: verossimilhancas globais, prior = taxa de fraude da RA no treino.
        p_r = Ft[tr].mean()
        nb_c = copy.deepcopy(a)
        nb_c.class_log_prior_ = np.log([1 - p_r, p_r])
        c[te] = nb_c.predict_proba(Es[te])[:, 1]

    return {"A_NB": a.predict_proba(Es)[:, 1], "B_NB": b, "C_NB": c}


def calcular_ml(ra, F, E, params, rng):
    """Retorna (scores_teste, idx_teste). scores_teste[nome] tem shape
    (n_teste,), alinhado a idx_teste: as metricas devem usar F[idx_teste]
    e ra[idx_teste], nunca os arrays completos.

    Consome o rng em ordem fixa: 1 sorteio para o split, 3 sementes
    (D, E, F; os calibrados reusam a do seu AdaBoost). O scikit-learn recebe
    inteiros, entao os sorteios internos dele nao consomem o rng do experimento."""
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

    entradas = {"D": (Et, Es, semente_d), "E": (Xe_tr, Xe_te, semente_e),
                "F": (Xf_tr, Xf_te, semente_f)}
    modelos = {k: _adaboost(sem).fit(X_tr, Ft) for k, (X_tr, _, sem) in entradas.items()}

    scores_teste = {f"{k}_ML": modelos[k].predict_proba(entradas[k][1])[:, 1] for k in entradas}
    scores_teste.update(_naive_bayes(Et, Ft, rat, Es, ras, n_ras))
    for k, (X_tr, X_te, sem) in entradas.items():
        scores_teste[f"{k}_PL"], scores_teste[f"{k}_ISO"] = _calibrados(
            modelos[k], X_tr, Ft, X_te, sem)
    return {b: scores_teste[b] for b in BRACOS_ML}, idx_teste
