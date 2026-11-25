"""Criterio (ii) na grade inteira: a direcao da disparidade territorial
sobrevive a variacao de beta e pi?

corr(cobertura_cadastral, FPR entre inocentes) por braco.
Negativa = quem mora onde o cadastro e' ruim paga mais falso positivo.
"""
import csv, itertools, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import Params, RAS, COBERTURA                 # noqa: E402
from bracos import BRACOS                                  # noqa: E402
from metricas import fpr_por_ra                            # noqa: E402
from varredura import simular                              # noqa: E402
from configuracao import (RES, SEMENTES, GRADE_BETA, GRADE_PI,  # noqa: E402
                          LIMIAR_CORR_RULE, LIMIAR_CORR_B, veredito)

GRADE_RUIDO = (0.07, 0.16, 0.28)


def main():
    """Mede corr e amplitude do FPR por RA em cada config da grade,
    escreve resultados/equidade.csv e imprime o veredito do criterio (ii)."""
    os.makedirs(RES, exist_ok=True)
    linhas = []
    for f_base, beta, pi in itertools.product(GRADE_RUIDO, GRADE_BETA, GRADE_PI):
        params = Params(pi=pi, f_base=f_base, beta=beta)
        acc = {b: [] for b in BRACOS}
        for semente in SEMENTES:
            ra, F, _, topo = simular(params, semente)
            for b, (_, sel) in topo.items():
                acc[b].append(fpr_por_ra(sel, ra, F, len(RAS)))
        linha = {"f_base": f_base, "beta": beta, "pi": pi}
        for b in BRACOS:
            m = np.mean(acc[b], axis=0)
            linha[f"corr_{b}"] = float(np.corrcoef(COBERTURA, m)[0, 1])
            linha[f"amplitude_{b}"] = float(np.ptp(m))
        linhas.append(linha)

    cam = os.path.join(RES, "equidade.csv")
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

    neg = np.array([L["corr_RULE_CNT"] for L in linhas]) < LIMIAR_CORR_RULE
    nao_neg = np.array([L["corr_B"] for L in linhas]) >= LIMIAR_CORR_B
    print(f"\n(ii) RULE_CNT com corr < -0.5 : {neg.sum()}/{len(linhas)} -> "
          f"{veredito(neg.all())}")
    print(f"     B com corr >= -0.1       : {nao_neg.sum()}/{len(linhas)} -> "
          f"{veredito(nao_neg.all())}")


if __name__ == "__main__":
    main()
