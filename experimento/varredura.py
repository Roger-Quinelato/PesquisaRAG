"""Varredura de sensibilidade + verificacao dos criterios de aceitacao.

Uso:  python experimento/varredura.py [--workers W] [--familias F1,F2]
                                      [--aceitar-cache F1,F2] [--sem-cache]
                                      [--conferir K]
Saida: resultados/varredura.csv, resultados/fpr_por_ra.csv (referencia),
       resultados/fpr_grade.csv (FPR por RA de toda a grade, lido por
       equidade.py), resultados/manifesto.sha256 e um veredito impresso sobre
       cada criterio declarado ANTES de rodar.

As metricas por (configuracao, semente, braco) ficam em resultados/cache/, uma
familia por arquivo (ver pipeline.py). Por padrao so se calcula o que falta ou
cuja chave de codigo mudou:
  --familias F        recalcula F mesmo com cache valido;
  --aceitar-cache F   usa o cache de F mesmo com a chave desatualizada (quando
                      a mudanca de codigo comprovadamente nao afeta F);
  --sem-cache         recalcula tudo;
  --conferir K        reexecuta K configuracoes (8 sementes) e compara bit a
                      bit com o cache -- a conferencia de determinismo.
"""
import argparse
import csv
import hashlib
import itertools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import RAS, COBERTURA                         # noqa: E402
from bracos import BRACOS                                  # noqa: E402
from bracos_ml import BRACOS_ML                            # noqa: E402
from pipeline import FAMILIAS, executar, _cfg               # noqa: E402

TODOS = BRACOS + BRACOS_ML

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "resultados")
CACHE = os.path.join(SAIDA, "cache")

N = 40_000
K = 0.10
SEMENTES = range(8)
GRADE_RUIDO = np.round(np.linspace(0.01, 0.40, 14), 4)
GRADE_BETA = (0.25, 0.40, 0.55, 0.70)
GRADE_PI = (0.05, 0.10, 0.15, 0.25)

# Config de referencia, usada nas figuras e na tabela por RA
REF_BETA, REF_PI, REF_RUIDO = 0.55, 0.15, 0.16
METRICAS = ("prec", "brier", "ece")


def e_referencia(f_base, beta, pi):
    return (round(beta, 4) == REF_BETA and round(pi, 4) == REF_PI
            and abs(f_base - REF_RUIDO) < 1e-6)


def atualizar_manifesto():
    """SHA-256 de cada CSV de resultados/. Conferencia completa de uma segunda
    rodada:  sha256sum -c resultados/manifesto.sha256  (a partir da raiz)."""
    nomes = sorted(n for n in os.listdir(SAIDA) if n.endswith(".csv"))
    with open(os.path.join(SAIDA, "manifesto.sha256"), "w", encoding="utf-8", newline="\n") as fh:
        for nome in nomes:
            with open(os.path.join(SAIDA, nome), "rb") as arq:
                fh.write(f"{hashlib.sha256(arq.read()).hexdigest()}  resultados/{nome}\n")


def _lista(texto):
    fams = tuple(f for f in texto.split(",") if f)
    ruins = set(fams) - set(FAMILIAS)
    if ruins:
        raise SystemExit(f"familias desconhecidas: {sorted(ruins)}; validas: {list(FAMILIAS)}")
    return fams


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--familias", default="", help="recalcula estas familias (ex.: calibrados)")
    ap.add_argument("--aceitar-cache", default="", help="usa o cache destas mesmo desatualizado")
    ap.add_argument("--sem-cache", action="store_true", help="recalcula todas as familias")
    ap.add_argument("--conferir", type=int, default=0, metavar="K",
                    help="reexecuta K configuracoes e compara bit a bit com o cache")
    args = ap.parse_args(argv)
    forcar = tuple(FAMILIAS) if args.sem_cache else _lista(args.familias)
    aceitar = _lista(args.aceitar_cache)

    os.makedirs(SAIDA, exist_ok=True)
    combos = list(itertools.product(GRADE_RUIDO, GRADE_BETA, GRADE_PI))
    print(f"{len(combos)} configuracoes x {len(list(SEMENTES))} sementes x {N:,} casos"
          f"  ({args.workers} processos)")

    def progresso(i, total):
        if i % 224 == 0 or i == total:
            print(f"  {i}/{total}", flush=True)

    tudo = executar(combos, SEMENTES, N, K, CACHE, forcar=forcar, aceitar_velho=aceitar,
                    workers=args.workers, progresso=progresso)

    # Agregacao na ordem das sementes, identica a da varredura sequencial antiga:
    # medias de floats lidos em repr (ida e volta exata) saem bit a bit iguais.
    linhas, grade, fpr_ref = [], [], {b: [] for b in TODOS}
    for f_base, beta, pi in combos:
        regs = [tudo[(_cfg(f_base, beta, pi), s)] for s in SEMENTES]
        for b in TODOS:
            por_semente = [r[b] for r in regs]
            linhas.append({
                "f_base": f_base, "beta": beta, "pi": pi, "braco": b,
                **{f"{m}_media": float(np.mean([r[m] for r in por_semente])) for m in METRICAS},
                **{f"{m}_dp": float(np.std([r[m] for r in por_semente])) for m in METRICAS},
                # Os bracos treinados sao avaliados so no teste: N menor, mais variancia.
                "n_efetivo": float(np.mean([r["n"] for r in por_semente])),
            })
            media_fpr = np.mean([r["fpr"] for r in por_semente], axis=0)
            grade.append([repr(float(f_base)), repr(float(beta)), repr(float(pi)), b,
                          *(repr(float(x)) for x in media_fpr)])
            if e_referencia(f_base, beta, pi):
                fpr_ref[b] = [r["fpr"] for r in por_semente]

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

    cam3 = os.path.join(SAIDA, "fpr_grade.csv")
    with open(cam3, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["f_base", "beta", "pi", "braco"] + [f"fpr_{r}" for r in range(len(RAS))])
        w.writerows(grade)
    print(f"-> {cam3}")
    atualizar_manifesto()

    verificar(linhas, medias)

    if args.conferir:
        conferir(args.conferir, combos, tudo, args.workers)


def amostra_conferencia(combos, k):
    """Referencia primeiro; o resto sorteado com semente fixa. Sempre a mesma."""
    ref = [c for c in combos if e_referencia(*c)]
    resto = [c for c in combos if not e_referencia(*c)]
    escolha = np.random.default_rng(12345).choice(len(resto), size=max(0, k - len(ref)),
                                                 replace=False)
    return ref + [resto[i] for i in sorted(escolha)]


def conferir(k, combos, tudo, workers):
    """Reexecuta a amostra em processos novos e compara cada registro bit a bit."""
    from concurrent.futures import ProcessPoolExecutor
    from pipeline import _tarefa, _inicializar_worker
    amostra = amostra_conferencia(combos, k)
    tarefas = [(float(f), float(b), float(p), s, tuple(FAMILIAS), N, K)
               for f, b, p in amostra for s in SEMENTES]
    print(f"\nConferencia de determinismo: {len(amostra)} configuracoes x "
          f"{len(list(SEMENTES))} sementes")
    with ProcessPoolExecutor(max_workers=workers, initializer=_inicializar_worker) as ex:
        novos = list(ex.map(_tarefa, tarefas))
    difere = []
    for args, novo in zip(tarefas, novos):
        antigo = tudo[(_cfg(*args[:3]), args[3])]
        for b in TODOS:
            a, n = antigo[b], novo[b]
            if not (all(a[m] == n[m] for m in ("prec", "brier", "ece", "n"))
                    and np.array_equal(a["fpr"], n["fpr"], equal_nan=True)):
                difere.append((args[:4], b))
    if difere:
        print(f"  NAO BATE em {len(difere)} registros, ex.: {difere[:5]}")
        raise SystemExit(1)
    print(f"  OK: {len(tarefas) * len(TODOS)} registros bit a bit iguais")


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

    # --- AdaBoost calibrado (Platt e isotonica), criterios declarados antes de rodar ---
    print("\n" + "-" * 66)
    print("ADABOOST CALIBRADO (CV de 5 dobras no treino; avaliado so no teste)")
    print("-" * 66)
    ece_med = {b: np.median([v[b]["ece_media"] for v in idx.values()])
               for b in ("D_ML", "D_PL", "D_ISO", "E_PL", "E_ISO", "F_PL", "F_ISO", "A_NB")}
    print("(xi)  ECE mediano: " + "  ".join(f"{b} {ece_med[b]:.4f}" for b in ece_med))
    print(f"      D_PL e D_ISO < 0,01 -> "
          f"{'PASSA' if max(ece_med['D_PL'], ece_med['D_ISO']) < 0.01 else 'FALHA'}")

    d_iso = np.median([v["D_ISO"]["prec_media"] - v["D_ML"]["prec_media"] for v in idx.values()])
    d_pl = np.median([v["D_PL"]["prec_media"] - v["D_ML"]["prec_media"] for v in idx.values()])
    print(f"(xii) mediana de prec D_ISO - D_ML = {100*d_iso:+.3f} p.p. (>= -0,1) "
          f"-> {'PASSA' if d_iso >= -0.001 else 'FALHA'}   "
          f"[D_PL - D_ML = {100*d_pl:+.3f} p.p., so desempate]")

    for b in ("D_PL", "D_ISO"):
        c = np.corrcoef(COBERTURA, medias_fpr[b])[0, 1]
        print(f"(xiii) {b} corr(cobertura, FPR) na referencia = {c:+.3f}  (grade inteira: equidade.py)")

    brier_ok = sum(1 for v in idx.values() if v["D_ISO"]["brier_media"] < v["D_ML"]["brier_media"])
    print(f"(xiv) ECE mediano D_ISO <= A_NB: {ece_med['D_ISO']:.4f} vs {ece_med['A_NB']:.4f} "
          f"-> {'PASSA' if ece_med['D_ISO'] <= ece_med['A_NB'] else 'FALHA'}")
    print(f"      Brier D_ISO < D_ML: {brier_ok}/{len(idx)} "
          f"-> {'PASSA' if brier_ok == len(idx) else 'FALHA'}")


if __name__ == "__main__":
    main()
