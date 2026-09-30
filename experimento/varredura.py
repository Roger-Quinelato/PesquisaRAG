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
from metricas import brier, ece, precisao_topk, fpr_por_ra  # noqa: E402
from configuracao import (RES, N, K, SEMENTES, GRADE_BETA, GRADE_PI,  # noqa: E402
                          LIMIAR_CORR_RULE, LIMIAR_CORR_B, eh_referencia, veredito)

GRADE_RUIDO = np.round(np.linspace(0.01, 0.40, 14), 4)
METRICAS = ("prec", "brier", "ece")


def simular(params, semente):
    """Uma semente: gera N casos, pontua os seis bracos e seleciona o topo K
    de cada um. A ordem dos sorteios (gerar, depois o desempate do topk de
    cada braco na ordem de BRACOS) e' o que torna a saida reprodutivel.
    Retorna (ra, F, scores, {braco: (precisao, indices_selecionados)})."""
    rng = np.random.default_rng(semente)
    ra, F, E, f_true = gerar(N, params, rng)
    scores = calcular(ra, F, E, f_true, params)
    topo = {b: precisao_topk(s, F, K, rng) for b, s in scores.items()}
    return ra, F, scores, topo


def uma_config(f_base, beta, pi, semente, com_fpr=False):
    """Metricas escalares de cada braco numa (config, semente); com_fpr
    acrescenta o FPR por RA, que so a config de referencia usa."""
    ra, F, scores, topo = simular(Params(pi=pi, f_base=f_base, beta=beta), semente)
    linha, fpr = {}, {}
    for nome, s in scores.items():
        prec, sel = topo[nome]
        linha[nome] = {"prec": prec, "brier": brier(s, F), "ece": ece(s, F)}
        if com_fpr:
            fpr[nome] = fpr_por_ra(sel, ra, F, len(RAS))
    return linha, fpr


def main():
    """Roda a grade inteira, escreve varredura.csv e fpr_por_ra.csv e
    imprime o veredito dos criterios de aceitacao."""
    os.makedirs(RES, exist_ok=True)
    combos = list(itertools.product(GRADE_RUIDO, GRADE_BETA, GRADE_PI))
    print(f"{len(combos)} configuracoes x {len(SEMENTES)} sementes x {N:,} casos")

    linhas, fpr_ref = [], {b: [] for b in BRACOS}
    for i, (f_base, beta, pi) in enumerate(combos, 1):
        ref = eh_referencia(f_base, beta, pi)
        acumulado = {b: {m: [] for m in METRICAS} for b in BRACOS}
        for semente in SEMENTES:
            res, fpr = uma_config(f_base, beta, pi, semente, com_fpr=ref)
            for b in BRACOS:
                for m in METRICAS:
                    acumulado[b][m].append(res[b][m])
                if ref:
                    fpr_ref[b].append(fpr[b])
        for b in BRACOS:
            linhas.append({
                "f_base": f_base, "beta": beta, "pi": pi, "braco": b,
                **{f"{m}_media": float(np.mean(acumulado[b][m])) for m in METRICAS},
                **{f"{m}_dp": float(np.std(acumulado[b][m])) for m in METRICAS},
            })
        if i % 28 == 0:
            print(f"  {i}/{len(combos)}")

    cam = os.path.join(RES, "varredura.csv")
    with open(cam, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"\n-> {cam}  ({len(linhas)} linhas)")

    cam2 = os.path.join(RES, "fpr_por_ra.csv")
    with open(cam2, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ra", "cobertura"] + list(BRACOS))
        medias = {b: np.mean(fpr_ref[b], axis=0) for b in BRACOS}
        for r, nome in enumerate(RAS):
            w.writerow([nome, COBERTURA[r]] + [f"{medias[b][r]:.6f}" for b in BRACOS])
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

    for m, rotulo in (("brier", "(i)  C pior que A em Brier"),
                      ("ece", "     C pior que A em ECE  ")):
        ok = sum(1 for v in idx.values() if v["C"][f"{m}_media"] > v["A"][f"{m}_media"])
        print(f"{rotulo}: {ok}/{len(idx)} -> {veredito(ok == len(idx))}")

    c = {b: np.corrcoef(COBERTURA, medias_fpr[b])[0, 1] for b in ("RULE_CNT", "B", "C")}
    print(f"\n(ii) corr(cobertura, FPR entre inocentes) na config de referencia:")
    print(f"       RULE_CNT = {c['RULE_CNT']:+.3f}  (esperado NEGATIVO)  "
          f"-> {veredito(c['RULE_CNT'] < LIMIAR_CORR_RULE)}")
    print(f"       B        = {c['B']:+.3f}  (esperado >= 0)      "
          f"-> {veredito(c['B'] >= LIMIAR_CORR_B)}")
    print(f"       C        = {c['C']:+.3f}  (redlining amplificado)")

    b_vence = sum(1 for v in idx.values()
                  if v["B"]["prec_media"] > max(v["A"]["prec_media"], v["LOOKUP"]["prec_media"]))
    print(f"\n(iii) B supera A e LOOKUP em precisao@10%: {b_vence}/{len(idx)} configuracoes")


if __name__ == "__main__":
    main()
