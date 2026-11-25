"""Intervalos de confianca das diferencas entre bracos, a partir de
resultados/varredura_sementes.csv (valores brutos por semente).

Uso:  python experimento/intervalos.py B LOOKUP prec

Para cada configuracao (f_base, beta, pi), as 8 sementes geram diferencas
pareadas (o mesmo conjunto de dados alimenta os dois bracos na mesma semente).
O intervalo e' t de Student com S-1 graus de liberdade sobre essas diferencas.

Limites declarados:
- 8 sementes dao um intervalo grosseiro; ele mede a variacao de amostragem
  dentro da configuracao, e nao a incerteza do mecanismo estipulado.
- Os bracos treinados sao avaliados so no teste (N ~ metade), enquanto os
  fechados usam N inteiro. Na diferenca entre os dois grupos, a metrica de um
  lado vem de amostra menor; leia o intervalo com essa ressalva.
- Nenhum ajuste para comparacoes multiplas: ha uma por configuracao.
"""
import csv
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from configuracao import RES  # noqa: E402

METRICAS = ("prec", "brier", "ece")


def ler_sementes(caminho=None):
    """{(f_base, beta, pi): {braco: {metrica: array por semente}}}. As sementes
    ficam na ordem em que foram gravadas, igual para todos os bracos."""
    caminho = caminho or os.path.join(RES, "varredura_sementes.csv")
    out = {}
    with open(caminho, encoding="utf-8", newline="") as fh:
        for L in csv.DictReader(fh):
            cfg = (float(L["f_base"]), float(L["beta"]), float(L["pi"]))
            braco = out.setdefault(cfg, {}).setdefault(L["braco"], {m: [] for m in METRICAS})
            for m in METRICAS:
                braco[m].append(float(L[m]))
    return {cfg: {b: {m: np.array(v) for m, v in ms.items()} for b, ms in bs.items()}
            for cfg, bs in out.items()}


def diferenca_pareada(dados, a, b, metrica="prec", nivel=0.95):
    """Por configuracao: media da diferenca (a - b) entre sementes, desvio e o
    intervalo t. `exclui_zero` e' True quando o intervalo nao contem 0."""
    linhas = []
    for cfg, bracos in sorted(dados.items()):
        d = bracos[a][metrica] - bracos[b][metrica]
        s = len(d)
        media = float(d.mean())
        dp = float(d.std(ddof=1)) if s > 1 else float("nan")
        meia = float(stats.t.ppf(0.5 + nivel / 2, s - 1) * dp / np.sqrt(s)) if s > 1 else float("nan")
        linhas.append({"f_base": cfg[0], "beta": cfg[1], "pi": cfg[2], "n_sementes": s,
                       "media": media, "dp": dp, "ic_inf": media - meia, "ic_sup": media + meia,
                       "exclui_zero": bool(abs(media) > meia) if s > 1 else False})
    return linhas


def resumo(linhas):
    """Contagens que acompanham o n/N de cada achado."""
    n = len(linhas)
    pos = sum(1 for L in linhas if L["ic_inf"] > 0)
    neg = sum(1 for L in linhas if L["ic_sup"] < 0)
    return {"configuracoes": n, "ic_positivo": pos, "ic_negativo": neg,
            "ic_inclui_zero": n - pos - neg,
            "mediana_da_media": float(np.median([L["media"] for L in linhas]))}


def main():
    if len(sys.argv) != 4:
        sys.exit("uso: python experimento/intervalos.py BRACO_A BRACO_B {prec|brier|ece}")
    a, b, m = sys.argv[1:]
    r = resumo(diferenca_pareada(ler_sementes(), a, b, m))
    print(f"{a} - {b} em {m}: {r['configuracoes']} configuracoes")
    print(f"  IC95% todo acima de 0 : {r['ic_positivo']}")
    print(f"  IC95% todo abaixo de 0: {r['ic_negativo']}")
    print(f"  IC95% inclui 0        : {r['ic_inclui_zero']}")
    print(f"  mediana da diferenca  : {r['mediana_da_media']:+.6f}")


if __name__ == "__main__":
    main()
