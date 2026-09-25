"""Criterio (ii) na grade inteira: a direcao da disparidade territorial
sobrevive a variacao de beta e pi?

corr(cobertura_cadastral, FPR entre inocentes) por braco.
Negativa = quem mora onde o cadastro e' ruim paga mais falso positivo.
"""
import csv, itertools, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import Params, gerar, RAS, COBERTURA          # noqa: E402
from bracos import BRACOS, calcular                        # noqa: E402
from bracos_ml import BRACOS_ML, calcular_ml               # noqa: E402
from metricas import precisao_topk, fpr_por_ra             # noqa: E402

TODOS = BRACOS + BRACOS_ML

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N, K, SEMENTES = 40_000, 0.10, range(8)
GRADE_RUIDO = (0.07, 0.16, 0.28)
GRADE_BETA = (0.25, 0.40, 0.55, 0.70)
GRADE_PI = (0.05, 0.10, 0.15, 0.25)


def main():
    os.makedirs(os.path.join(RAIZ, "resultados"), exist_ok=True)
    linhas = []
    for f_base, beta, pi in itertools.product(GRADE_RUIDO, GRADE_BETA, GRADE_PI):
        params = Params(pi=pi, f_base=f_base, beta=beta)
        acc = {b: [] for b in TODOS}
        for semente in SEMENTES:
            rng = np.random.default_rng(semente)
            ra, F, E, f_true = gerar(N, params, rng)
            for b, s in calcular(ra, F, E, f_true, params).items():
                _, sel = precisao_topk(s, F, K, rng)
                acc[b].append(fpr_por_ra(sel, ra, F, N, len(RAS)))
            # Bracos treinados depois dos fechados (mesma ordem de rng de varredura.py).
            scores_ml, idx_teste = calcular_ml(ra, F, E, params, rng)
            F_t, ra_t = F[idx_teste], ra[idx_teste]
            for b in BRACOS_ML:
                _, sel = precisao_topk(scores_ml[b], F_t, K, rng)
                acc[b].append(fpr_por_ra(sel, ra_t, F_t, len(idx_teste), len(RAS)))
        linha = {"f_base": f_base, "beta": beta, "pi": pi}
        for b in TODOS:
            m = np.mean(acc[b], axis=0)
            linha[f"corr_{b}"] = float(np.corrcoef(COBERTURA, m)[0, 1])
            linha[f"amplitude_{b}"] = float(np.ptp(m))
        linhas.append(linha)

    cam = os.path.join(RAIZ, "resultados", "equidade.csv")
    with open(cam, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader(); w.writerows(linhas)
    print(f"-> {cam}  ({len(linhas)} configuracoes)\n")

    print("corr(cobertura, FPR entre inocentes) -- min / mediana / max na grade")
    print(f"{'braco':>9} | {'min':>7} {'mediana':>8} {'max':>7} | {'amplitude mediana':>18}")
    print("-" * 62)
    for b in TODOS:
        c = np.array([L[f"corr_{b}"] for L in linhas])
        a = np.array([L[f"amplitude_{b}"] for L in linhas])
        print(f"{b:>9} | {c.min():+7.3f} {np.median(c):+8.3f} {c.max():+7.3f} | {np.median(a):18.4f}")

    neg = np.array([L["corr_RULE_CNT"] for L in linhas]) < -0.5
    nao_neg = np.array([L["corr_B"] for L in linhas]) >= -0.1
    print(f"\n(ii) RULE_CNT com corr < -0.5 : {neg.sum()}/{len(linhas)} -> "
          f"{'PASSA' if neg.all() else 'FALHA'}")
    print(f"     B com corr >= -0.1       : {nao_neg.sum()}/{len(linhas)} -> "
          f"{'PASSA' if nao_neg.all() else 'FALHA'}")

    # Hipotese (a) para os bracos AdaBoost: F_ML reproduz a disparidade em toda a
    # grade, e E_ML NAO a corrige de forma robusta (mesmo limiar usado para B).
    f_neg = np.array([L["corr_F_ML"] for L in linhas]) < -0.5
    e_corrige = np.array([L["corr_E_ML"] for L in linhas]) >= -0.1
    amp = {b: np.median([L[f"amplitude_{b}"] for L in linhas]) for b in ("D_ML", "E_ML", "F_ML")}
    print(f"\n(v)  F_ML com corr < -0.5     : {f_neg.sum()}/{len(linhas)} -> "
          f"{'PASSA' if f_neg.all() else 'FALHA'}")
    print(f"     E_ML com corr >= -0.1    : {e_corrige.sum()}/{len(linhas)} -> "
          f"hipotese 'nao corrige' {'PASSA' if not e_corrige.all() else 'FALHA'}")
    print("     amplitude mediana: " + "  ".join(f"{b} {amp[b]:.4f}" for b in amp))


if __name__ == "__main__":
    main()
