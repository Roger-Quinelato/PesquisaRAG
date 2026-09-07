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
from metricas import precisao_topk, fpr_por_ra             # noqa: E402

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
        acc = {b: [] for b in BRACOS}
        for semente in SEMENTES:
            rng = np.random.default_rng(semente)
            ra, F, E, f_true = gerar(N, params, rng)
            for b, s in calcular(ra, F, E, f_true, params).items():
                _, sel = precisao_topk(s, F, K, rng)
                acc[b].append(fpr_por_ra(sel, ra, F, N, len(RAS)))
        linha = {"f_base": f_base, "beta": beta, "pi": pi}
        for b in BRACOS:
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
    for b in BRACOS:
        c = np.array([L[f"corr_{b}"] for L in linhas])
        a = np.array([L[f"amplitude_{b}"] for L in linhas])
        print(f"{b:>9} | {c.min():+7.3f} {np.median(c):+8.3f} {c.max():+7.3f} | {np.median(a):18.4f}")

    neg = np.array([L["corr_RULE_CNT"] for L in linhas]) < -0.5
    nao_neg = np.array([L["corr_B"] for L in linhas]) >= -0.1
    print(f"\n(ii) RULE_CNT com corr < -0.5 : {neg.sum()}/{len(linhas)} -> "
          f"{'PASSA' if neg.all() else 'FALHA'}")
    print(f"     B com corr >= -0.1       : {nao_neg.sum()}/{len(linhas)} -> "
          f"{'PASSA' if nao_neg.all() else 'FALHA'}")


if __name__ == "__main__":
    main()
