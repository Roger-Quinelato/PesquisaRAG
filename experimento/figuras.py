"""As duas figuras do banner. Le resultados/, escreve figuras/. Renderizacao
via seaborn (sobre matplotlib); paleta e estilo compartilhados estao em
paleta_sns.py."""
import csv, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import RAS, COBERTURA  # noqa: E402
from bracos import BRACOS           # noqa: E402
from paleta_sns import (COR, ROTULO, LARGURA, num, eixo_ptbr, chaves_legenda,  # noqa: E402
                        configurar_estilo, linha, TINTA_SECUNDARIA, TINTA_MUTED)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES, FIG = os.path.join(RAIZ, "resultados"), os.path.join(RAIZ, "figuras")
REF_BETA, REF_PI = 0.55, 0.15

configurar_estilo()


def ler(nome):
    with open(os.path.join(RES, nome), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fig1():
    R = [L for L in ler("varredura.csv")
         if float(L["beta"]) == REF_BETA and float(L["pi"]) == REF_PI]
    df = pd.DataFrame(R)
    df["f_base"] = df["f_base"].astype(float)
    df["prec_media"] = df["prec_media"].astype(float)
    df["ece_media"] = df["ece_media"].astype(float)
    df = df.sort_values("f_base")

    fig, ax = plt.subplots(1, 3, figsize=(17.5, 6.0))

    # Painel 1 -- utilidade sob orcamento.
    for b in BRACOS:
        d = df[df["braco"] == b]
        linha(ax[0], d["f_base"], d["prec_media"], b)
    ax[0].set_ylabel("Precisão no topo 10%")
    ax[0].set_title("Utilidade da triagem sob orçamento")

    # Painel 2 -- diferenca contra a tabela empirica. Sem ele o ganho de B
    # fica escondido sob as curvas sobrepostas -- e o tamanho do efeito e' o
    # ponto.
    base = df[df["braco"] == "LOOKUP"].set_index("f_base")["prec_media"]
    ax[1].axhline(0, color=COR["LOOKUP"], lw=LARGURA["LOOKUP"], ls="-.")
    for b in ("RULE_CNT", "A", "B", "C"):
        d = df[df["braco"] == b].set_index("f_base")
        diff = (d["prec_media"] - base) * 100
        linha(ax[1], diff.index, diff.values, b)
    ax[1].set_ylabel("Diferença contra a tabela empírica (p.p.)")
    ax[1].set_title("Tamanho do efeito — o ganho de B é modesto")

    # Painel 3 -- calibracao.
    for b in ("LOOKUP", "A", "B", "C"):
        d = df[df["braco"] == b]
        linha(ax[2], d["f_base"], d["ece_media"], b)
    ax[2].set_ylabel("Erro de calibração esperado (ECE)")
    ax[2].set_title("Calibração — território no prior colapsa")

    for a in ax:
        a.set_xlabel("Ruído da evidência (taxa de falso-positivo base)")
        sns.despine(ax=a, left=True)
    eixo_ptbr(*ax)

    # Legenda unica, fora da area de plotagem. Uma por painel cobriria as
    # curvas (a de C sobe ate' o canto superior direito do painel 3) e
    # repetiria tres vezes a mesma convencao de cor, que e' fixa em toda a
    # pesquisa. Duas linhas de tres para nao estourar a largura.
    fig.legend(handles=chaves_legenda(BRACOS), loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, 0.0), columnspacing=2.4,
               handlelength=2.8)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.savefig(os.path.join(FIG, "fig1_precisao_calibracao.png"))
    plt.close(fig)


def fig2():
    R = ler("fpr_por_ra.csv")
    df = pd.DataFrame(R)
    df["cobertura"] = df["cobertura"].astype(float) * 100
    for b in ("RULE_CNT", "A", "B", "C"):
        df[b] = df[b].astype(float) * 100
    df = df.sort_values("cobertura")

    # Rotulo curto so' nesta figura: a legenda completa de ROTULO alarga a
    # caixa o bastante para colidir com as anotacoes "Ceilandia"/"Plano
    # Piloto". A descricao completa de cada braco ja esta no eixo/legenda
    # das figuras 1, 3 e 5 -- aqui basta a letra e o mecanismo.
    rotulo_curto = {"RULE_CNT": "Regra por contagem", "A": "A (sem território)",
                    "B": "B (verossimilhança)", "C": "C (prior)"}
    fig, ax = plt.subplots(figsize=(12.6, 6.3))
    for b in ("RULE_CNT", "A", "B", "C"):
        r = np.corrcoef(df["cobertura"], df[b])[0, 1]
        resultado = linha(ax, df["cobertura"], df[b], b, marker="o", markersize=8)
        resultado.lines[-1].set_label(f"{rotulo_curto[b]}  (r = {num(r)})")
    # Fora da area de plotagem: dentro dela a caixa cobre o topo da curva de
    # C, que e' justamente o ponto da figura (Ceilandia no extremo alto).
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.015, 1.0),
              handlelength=2.8, borderaxespad=0)

    for _, row in df.iterrows():
        if row["ra"] == "Ceilândia":
            ax.annotate(row["ra"], (row["cobertura"], row["C"]),
                        textcoords="offset points", xytext=(14, -4),
                        ha="left", fontsize=11, color=TINTA_SECUNDARIA)
        elif row["ra"] == "Plano Piloto":
            ax.annotate(row["ra"], (row["cobertura"], row["C"]),
                        textcoords="offset points", xytext=(-6, 12),
                        ha="right", fontsize=11, color=TINTA_SECUNDARIA)

    ax.set_xlabel("Cobertura do cadastro territorial da Região Administrativa (%)")
    ax.set_ylabel("Inocentes enviados à revisão (%)")
    ax.set_title("Quem paga o falso positivo\n"
                 "(taxa de fraude idêntica em todas as regiões, por construção)")
    ax.margins(y=0.12)
    sns.despine(ax=ax, left=True)
    eixo_ptbr(ax)
    # Ressalva obrigatoria: a inversao de sinal de B NAO e' robusta. Quebrada
    # a mao e ancorada na figura: uma linha unica em coordenadas do eixo
    # estourava a tela e, com bbox_inches="tight", esmagava o grafico.
    fig.text(0.07, 0.025,
             "Configuração de referência (β = 0,55; π = 0,15; ruído = 0,16). "
             "A correlação negativa em A e C se mantém em 48/48 configurações;\n"
             "a inversão estrita de sinal em B ocorre em apenas 30/48 (o critério "
             "pré-registrado, mais tolerante, é atendido em 33/48),\n"
             "falhando sob ruído baixo com gradiente íngreme e sob ruído alto com "
             "prevalência alta.",
             fontsize=10, color=TINTA_MUTED, va="bottom", linespacing=1.5)
    fig.subplots_adjust(left=0.07, right=0.66, top=0.86, bottom=0.27)
    fig.savefig(os.path.join(FIG, "fig2_equidade_territorial.png"))
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    fig1(); fig2()
    print("-> figuras/fig1_precisao_calibracao.png")
    print("-> figuras/fig2_equidade_territorial.png")
