"""Varredura de sensibilidade + verificacao dos criterios de aceitacao.

Uso:  python experimento/varredura.py
Saida: resultados/varredura.csv, resultados/fpr_por_ra.csv e um veredito
       impresso sobre cada criterio declarado ANTES de rodar.
"""
import csv
import itertools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import Params, gerar, RAS, COBERTURA          # noqa: E402
from bracos import BRACOS, calcular                        # noqa: E402
from bracos_ml import BRACOS_ML, calcular_ml               # noqa: E402
from metricas import brier, ece, precisao_topk, fpr_por_ra  # noqa: E402

TODOS = BRACOS + BRACOS_ML

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "resultados")

N = 40_000
K = 0.10
SEMENTES = range(8)
GRADE_RUIDO = np.round(np.linspace(0.01, 0.40, 14), 4)
GRADE_BETA = (0.25, 0.40, 0.55, 0.70)
GRADE_PI = (0.05, 0.10, 0.15, 0.25)

# Config de referencia, usada nas figuras e na tabela por RA
REF_BETA, REF_PI, REF_RUIDO = 0.55, 0.15, 0.16


def uma_config(f_base, beta, pi, semente):
    params = Params(pi=pi, f_base=f_base, beta=beta)
    rng = np.random.default_rng(semente)
    ra, F, E, f_true = gerar(N, params, rng)
    scores = calcular(ra, F, E, f_true, params)

    linha, fpr = {}, {}
    for nome, s in scores.items():
        p = np.clip(s, 0.0, 1.0)
        prec, sel = precisao_topk(s, F, K, rng)
        linha[nome] = {"prec": prec, "brier": brier(p, F), "ece": ece(p, F), "n": N}
        fpr[nome] = fpr_por_ra(sel, ra, F, N, len(RAS))

    # Bracos treinados: estritamente depois dos seis fechados, para nao mudar
    # a sequencia do rng que eles consomem. `sel` aqui indexa o subconjunto
    # de teste, nunca os N casos completos.
    scores_ml, idx_teste = calcular_ml(ra, F, E, params, rng)
    F_t, ra_t, n_t = F[idx_teste], ra[idx_teste], len(idx_teste)
    for nome in BRACOS_ML:
        s = scores_ml[nome]
        p = np.clip(s, 0.0, 1.0)
        prec, sel = precisao_topk(s, F_t, K, rng)
        linha[nome] = {"prec": prec, "brier": brier(p, F_t), "ece": ece(p, F_t), "n": n_t}
        fpr[nome] = fpr_por_ra(sel, ra_t, F_t, n_t, len(RAS))
    return linha, fpr


def main():
    os.makedirs(SAIDA, exist_ok=True)
    combos = list(itertools.product(GRADE_RUIDO, GRADE_BETA, GRADE_PI))
    print(f"{len(combos)} configuracoes x {len(list(SEMENTES))} sementes x {N:,} casos")

    linhas, fpr_ref = [], {b: [] for b in TODOS}
    for i, (f_base, beta, pi) in enumerate(combos, 1):
        acumulado = {b: {m: [] for m in ("prec", "brier", "ece", "n")} for b in TODOS}
        for semente in SEMENTES:
            res, fpr = uma_config(f_base, beta, pi, semente)
            for b in TODOS:
                for m in ("prec", "brier", "ece", "n"):
                    acumulado[b][m].append(res[b][m])
                if (round(beta, 4) == REF_BETA and round(pi, 4) == REF_PI
                        and abs(f_base - REF_RUIDO) < 1e-6):
                    fpr_ref[b].append(fpr[b])
        for b in TODOS:
            linhas.append({
                "f_base": f_base, "beta": beta, "pi": pi, "braco": b,
                **{f"{m}_media": float(np.mean(acumulado[b][m])) for m in ("prec", "brier", "ece")},
                **{f"{m}_dp": float(np.std(acumulado[b][m])) for m in ("prec", "brier", "ece")},
                # Os bracos treinados sao avaliados so no teste: N menor, mais variancia.
                "n_efetivo": float(np.mean(acumulado[b]["n"])),
            })
        if i % 28 == 0:
            print(f"  {i}/{len(combos)}")

    cam = os.path.join(SAIDA, "varredura.csv")
    with open(cam, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"\n-> {cam}  ({len(linhas)} linhas)")

    cam2 = os.path.join(SAIDA, "fpr_por_ra.csv")
    with open(cam2, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ra", "cobertura"] + list(TODOS))
        medias = {b: np.mean(fpr_ref[b], axis=0) for b in TODOS}
        for r, nome in enumerate(RAS):
            w.writerow([nome, COBERTURA[r]] + [f"{medias[b][r]:.6f}" for b in TODOS])
    print(f"-> {cam2}")

    verificar(linhas, medias)


def verificar(linhas, medias_fpr):
    """Criterios declarados no plano ANTES de rodar."""
    print("\n" + "=" * 66)
    print("CRITERIOS DE ACEITACAO")
    print("=" * 66)

    idx = {}
    for L in linhas:
        idx.setdefault((L["f_base"], L["beta"], L["pi"]), {})[L["braco"]] = L

    falhas_brier = [k for k, v in idx.items()
                    if not (v["C"]["brier_media"] > v["A"]["brier_media"])]
    falhas_ece = [k for k, v in idx.items()
                  if not (v["C"]["ece_media"] > v["A"]["ece_media"])]
    print(f"(i)  C pior que A em Brier: {len(idx)-len(falhas_brier)}/{len(idx)} "
          f"-> {'PASSA' if not falhas_brier else 'FALHA'}")
    print(f"     C pior que A em ECE  : {len(idx)-len(falhas_ece)}/{len(idx)} "
          f"-> {'PASSA' if not falhas_ece else 'FALHA'}")

    c_rule = np.corrcoef(COBERTURA, medias_fpr["RULE_CNT"])[0, 1]
    c_b = np.corrcoef(COBERTURA, medias_fpr["B"])[0, 1]
    c_c = np.corrcoef(COBERTURA, medias_fpr["C"])[0, 1]
    print(f"\n(ii) corr(cobertura, FPR entre inocentes) na config de referencia:")
    print(f"       RULE_CNT = {c_rule:+.3f}  (esperado NEGATIVO)  "
          f"-> {'PASSA' if c_rule < -0.5 else 'FALHA'}")
    print(f"       B        = {c_b:+.3f}  (esperado >= 0)      "
          f"-> {'PASSA' if c_b >= -0.1 else 'FALHA'}")
    print(f"       C        = {c_c:+.3f}  (redlining amplificado)")

    b_vence = sum(1 for v in idx.values()
                  if v["B"]["prec_media"] > max(v["A"]["prec_media"], v["LOOKUP"]["prec_media"]))
    print(f"\n(iii) B supera A e LOOKUP em precisao@10%: {b_vence}/{len(idx)} configuracoes")

    # --- Bracos AdaBoost (D_ML/E_ML/F_ML), criterios declarados antes de rodar ---
    # (a) um classificador discriminativo tambem falha na equidade sem dado de RA
    #     de qualidade; (b) o ganho de precisao dele sobre LOOKUP supera o de B.
    print("\n" + "-" * 66)
    print("BRACOS ADABOOST (avaliados so no teste: N ~ metade)")
    print("-" * 66)
    f_brier = [k for k, v in idx.items()
               if not (v["F_ML"]["brier_media"] > v["D_ML"]["brier_media"])]
    f_ece = [k for k, v in idx.items()
             if not (v["F_ML"]["ece_media"] > v["D_ML"]["ece_media"])]
    print(f"(iv) F_ML pior que D_ML em Brier: {len(idx)-len(f_brier)}/{len(idx)} "
          f"-> {'PASSA' if not f_brier else 'FALHA'}")
    print(f"     F_ML pior que D_ML em ECE  : {len(idx)-len(f_ece)}/{len(idx)} "
          f"-> {'PASSA' if not f_ece else 'FALHA'}")

    c_f = np.corrcoef(COBERTURA, medias_fpr["F_ML"])[0, 1]
    c_e = np.corrcoef(COBERTURA, medias_fpr["E_ML"])[0, 1]
    print(f"\n(v)  corr(cobertura, FPR entre inocentes) na config de referencia:")
    print(f"       F_ML = {c_f:+.3f}  (esperado NEGATIVO)       "
          f"-> {'PASSA' if c_f < -0.5 else 'FALHA'}")
    print(f"       E_ML = {c_e:+.3f}  (hipotese: nao corrige)  "
          f"-> {'PASSA' if c_e < -0.1 else 'FALHA'}  (grade inteira: equidade.py)")

    ganho_e = np.median([v["E_ML"]["prec_media"] - v["LOOKUP"]["prec_media"] for v in idx.values()])
    ganho_b = np.median([v["B"]["prec_media"] - v["LOOKUP"]["prec_media"] for v in idx.values()])
    print(f"\n(vi) mediana do ganho de precisao@10% sobre LOOKUP:")
    print(f"       E_ML = {100*ganho_e:+.3f} p.p.   B = {100*ganho_b:+.3f} p.p.  "
          f"-> {'PASSA' if ganho_e > ganho_b else 'FALHA'}")
    print("       (E_ML fora da amostra; LOOKUP e B na propria amostra)")

    # --- Naive Bayes treinado (A_NB/B_NB/C_NB), criterios declarados antes de rodar ---
    print("\n" + "-" * 66)
    print("NAIVE BAYES TREINADO (avaliado so no teste: N ~ metade)")
    print("-" * 66)
    ece_anb = np.median([v["A_NB"]["ece_media"] for v in idx.values()])
    print(f"(vii) A_NB calibrado, ECE mediano < 0,01: {ece_anb:.4f} "
          f"-> {'PASSA' if ece_anb < 0.01 else 'FALHA'}")

    c_dominado = sum(1 for v in idx.values()
                     if v["C_NB"]["brier_media"] > v["A_NB"]["brier_media"]
                     and v["C_NB"]["ece_media"] > v["A_NB"]["ece_media"])
    print(f"(viii) C_NB pior que A_NB em Brier e ECE: {c_dominado}/{len(idx)} "
          f"(hipotese: no maximo metade) -> {'PASSA' if c_dominado <= len(idx) // 2 else 'FALHA'}")

    c_bnb = np.corrcoef(COBERTURA, medias_fpr["B_NB"])[0, 1]
    print(f"(ix)  B_NB corr(cobertura, FPR) na referencia = {c_bnb:+.3f}  (grade inteira: equidade.py)")

    bnb_vence = sum(1 for v in idx.values()
                    if v["B_NB"]["prec_media"] > v["LOOKUP"]["prec_media"])
    print(f"(x)   B_NB supera LOOKUP em precisao@10%: {bnb_vence}/{len(idx)} "
          f"-> {'PASSA' if bnb_vence > len(idx) // 2 else 'FALHA'}")


if __name__ == "__main__":
    main()
