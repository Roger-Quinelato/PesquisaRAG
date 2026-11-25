"""Criterio (ii) na grade inteira: a direcao da disparidade territorial
sobrevive a variacao de beta e pi?

corr(cobertura_cadastral, FPR entre inocentes) por braco.
Negativa = quem mora onde o cadastro e' ruim paga mais falso positivo.

Nao calcula nada: le resultados/fpr_grade.csv, escrito por varredura.py. Os
ruidos daqui (0,07; 0,16; 0,28) sao os mesmos floats da grade da varredura, e o
pipeline por semente e' o mesmo, entao o resultado e' bit a bit igual ao de
recalcular. Rode varredura.py antes.
"""
import csv, itertools, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import COBERTURA                              # noqa: E402
from varredura import TODOS, GRADE_BETA, GRADE_PI, SAIDA, atualizar_manifesto  # noqa: E402

GRADE_RUIDO = (0.07, 0.16, 0.28)


def ler_grade():
    cam = os.path.join(SAIDA, "fpr_grade.csv")
    if not os.path.exists(cam):
        raise SystemExit(f"{cam} nao existe: rode experimento/varredura.py antes.")
    grade = {}
    with open(cam, encoding="utf-8", newline="") as fh:
        for L in csv.DictReader(fh):
            chave = (float(L["f_base"]), float(L["beta"]), float(L["pi"]), L["braco"])
            grade[chave] = np.array([float(L[f"fpr_{r}"]) for r in range(len(COBERTURA))])
    return grade


def main():
    grade = ler_grade()
    linhas = []
    for f_base, beta, pi in itertools.product(GRADE_RUIDO, GRADE_BETA, GRADE_PI):
        linha = {"f_base": f_base, "beta": beta, "pi": pi}
        for b in TODOS:
            # Media por semente do FPR por RA, gravada pela varredura em repr.
            m = grade.get((f_base, beta, pi, b))
            if m is None:
                raise SystemExit(f"fpr_grade.csv nao cobre ({f_base}, {beta}, {pi}, {b}): "
                                 "rode experimento/varredura.py com a grade completa.")
            linha[f"corr_{b}"] = float(np.corrcoef(COBERTURA, m)[0, 1])
            linha[f"amplitude_{b}"] = float(np.ptp(m))
        linhas.append(linha)

    cam = os.path.join(SAIDA, "equidade.csv")
    with open(cam, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader(); w.writerows(linhas)
    print(f"-> {cam}  ({len(linhas)} configuracoes)\n")
    atualizar_manifesto()

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

    # (ix) Naive Bayes treinado: B_NB nao corrige a disparidade de forma robusta.
    bnb_corrige = np.array([L["corr_B_NB"] for L in linhas]) >= -0.1
    print(f"\n(ix) B_NB com corr >= -0.1    : {bnb_corrige.sum()}/{len(linhas)} -> "
          f"hipotese 'nao corrige' {'PASSA' if not bnb_corrige.all() else 'FALHA'}")

    # (xiii) Calibrar nao corrige a disparidade: D_PL e D_ISO com corr < 0 em toda a grade.
    print("\n(xiii) calibrar nao corrige a disparidade:")
    for b in ("D_PL", "D_ISO"):
        neg_b = np.array([L[f"corr_{b}"] for L in linhas]) < 0
        print(f"       {b} com corr < 0     : {neg_b.sum()}/{len(linhas)} -> "
              f"{'PASSA' if neg_b.all() else 'FALHA'}")
    for b in ("E_ML", "E_PL", "E_ISO"):
        n_b = int((np.array([L[f"corr_{b}"] for L in linhas]) >= -0.1).sum())
        print(f"       {b} com corr >= -0.1 : {n_b}/{len(linhas)}")


if __name__ == "__main__":
    main()
