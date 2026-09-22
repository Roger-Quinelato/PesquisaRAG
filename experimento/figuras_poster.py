"""Figuras do pôster (Congresso de IC UnB/DF): versões enxutas das figuras 1 e 2
do relatório e quatro figuras novas, desenhadas para a largura de uma coluna do
pôster. Lê resultados/ e gerador.Params; escreve figuras/poster_*.png.

    python experimento/figuras_poster.py

Convenção fixa (paleta_sns.py): A azul, B laranja, C água, regra por contagem
em tinta, tabela empírica em sage; dado de entrada que não é braço em cinza;
texto sempre em tinta; legenda nunca sobre os dados.
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.patches import FancyBboxPatch, Patch
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import RAS, COBERTURA, IDX_ENDERECO, Params  # noqa: E402
from paleta_sns import (COR, LARGURA, TRACO, num, eixo_ptbr, VIRGULA,  # noqa: E402
                        configurar_estilo, linha, chaves_legenda,
                        TINTA_PRIMARIA, TINTA_SECUNDARIA, TINTA_MUTED, EIXO)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES, FIG = os.path.join(RAIZ, "resultados"), os.path.join(RAIZ, "figuras")
REF_F, REF_BETA, REF_PI = 0.16, 0.55, 0.15
META = {"Software": None}   # hash estável entre execuções
DPI = 300
ROT = {"RULE_CNT": "Regra por contagem", "LOOKUP": "Tabela empírica",
       "A": "A: sem território", "B": "B: RA na verossimilhança",
       "C": "C: RA no prior"}
CINZA_CLARO = "#d6d5cd"
FUNDO_NEUTRO = "#f3f2ee"

configurar_estilo()
sns.set_context("talk", rc={"axes.titlesize": 20, "axes.labelsize": 16,
                            "xtick.labelsize": 14, "ytick.labelsize": 14,
                            "legend.fontsize": 14})


def ler(nome):
    return pd.read_csv(os.path.join(RES, nome), encoding="utf-8")


MARGEM = 0.03   # título, legenda e rodapé alinhados à esquerda da figura


def titulo(fig, texto, y=0.965):
    fig.text(MARGEM, y, texto, fontsize=20, fontweight="bold", color=TINTA_PRIMARIA,
             va="top")


def painel(ax, texto):
    ax.set_title(texto, loc="left", fontsize=15, color=TINTA_SECUNDARIA, pad=10)


def rodape(fig, texto, y=0.025):
    fig.text(MARGEM, y, texto, fontsize=12, color=TINTA_MUTED, va="bottom",
             linespacing=1.45)


def salvar(fig, nome):
    fig.savefig(os.path.join(FIG, nome), dpi=DPI, metadata=META)
    plt.close(fig)


def pct(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",")


# --------------------------------------------------------------------------
# Objetivo -- onde a RA entra na regra de Bayes (diagrama, sem dados)
# --------------------------------------------------------------------------
def objetivo():
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    fig.subplots_adjust(left=MARGEM, right=0.98, top=0.88, bottom=0.03)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 6.0)
    ax.axis("off")
    titulo(fig, "Onde a Região Administrativa entra no modelo")

    ax.text(0.0, 5.55, "Regra de Bayes:  posterior ∝ prior × verossimilhança",
            fontsize=16, color=TINTA_SECUNDARIA, va="center")
    LARG = 2.7
    colunas = {"prior": (5.9, "Prior", "(suspeita inicial)"),
               "veross": (9.0, "Verossimilhança", "(peso das evidências)")}
    for x, nome, sub in colunas.values():
        ax.text(x, 4.75, nome, ha="center", va="center", fontsize=17,
                fontweight="bold", color=TINTA_PRIMARIA)
        ax.text(x, 4.3, sub, ha="center", va="center", fontsize=14, color=TINTA_MUTED)

    linhas = [("A", "ignora a RA", None), ("B", "RA na verossimilhança", "veross"),
              ("C", "RA no prior", "prior")]
    for (braco, desc, onde), y in zip(linhas, (3.4, 2.2, 1.0)):
        ax.add_patch(FancyBboxPatch((0.0, y - 0.38), 0.76, 0.76,
                                    boxstyle="round,pad=0,rounding_size=0.12",
                                    fc=COR[braco], ec="none"))
        ax.text(0.38, y, braco, ha="center", va="center", fontsize=20,
                fontweight="bold", color="white")
        ax.text(1.0, y, desc, va="center", fontsize=16, color=TINTA_PRIMARIA)
        for chave, (x, _, _) in colunas.items():
            destaque = chave == onde
            ax.add_patch(FancyBboxPatch(
                (x - LARG / 2, y - 0.42), LARG, 0.84,
                boxstyle="round,pad=0,rounding_size=0.14",
                fc=to_rgba(COR[braco], 0.16) if destaque else FUNDO_NEUTRO,
                ec=COR[braco] if destaque else EIXO,
                lw=2.8 if destaque else 1.2))
            ax.text(x, y, "muda com a RA" if destaque else "igual para todos",
                    ha="center", va="center", fontsize=15,
                    fontweight="bold" if destaque else "normal",
                    color=TINTA_PRIMARIA if destaque else TINTA_MUTED)

    ax.text(0.0, 0.12, "No gerador dos dados, a RA só altera o ruído do endereço "
            "(a verossimilhança).", fontsize=12.5, color=TINTA_MUTED, va="center")
    salvar(fig, "poster_objetivo_onde_entra_ra.png")


# --------------------------------------------------------------------------
# Metodologia -- o mecanismo: só o endereço piora onde o cadastro é pior
# --------------------------------------------------------------------------
def metodologia():
    p = Params()
    total = p.fpr_por_ra(np.arange(len(RAS)))[:, IDX_ENDERECO] * 100
    base = np.full(len(RAS), p.f_base * 100)
    y = np.arange(len(RAS))

    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    fig.subplots_adjust(left=0.27, right=0.95, top=0.79, bottom=0.23)
    ax.barh(y, base, height=0.64, color=CINZA_CLARO, edgecolor="white", lw=2)
    ax.barh(y, total - base, left=base, height=0.64, color=TINTA_SECUNDARIA,
            edgecolor="white", lw=2)
    for yi, v in zip(y, total):
        ax.text(v + 0.7, yi, f"{pct(v)}%", va="center", fontsize=14, color=TINTA_PRIMARIA)
    ax.set_yticks(y, [f"{ra} · {c * 100:.0f}%" for ra, c in zip(RAS, COBERTURA)])
    ax.invert_yaxis()
    ax.set_xlim(0, 47)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(VIRGULA)
    ax.set_xlabel("Falso positivo da evidência de endereço (%)")
    ax.set_ylabel("RA · cobertura do cadastro")

    fig.legend(handles=[Patch(color=CINZA_CLARO, label=f"ruído base: {pct(base[0], 0)}% em toda RA"),
                        Patch(color=TINTA_SECUNDARIA, label="acréscimo pela falta de cadastro")],
               loc="upper left", bbox_to_anchor=(MARGEM - 0.008, 0.9), ncol=2, frameon=False,
               handlelength=1.2, columnspacing=1.6)
    titulo(fig, "Só o endereço fica mais ruidoso onde o cadastro é pior")
    rodape(fig, f"Fraude idêntica em todas as RAs ({pct(p.pi * 100, 0)}%), por construção. "
                "Status e valor: ruído base em toda RA.\n"
                "Cobertura estipulada, não medida. Configuração de referência "
                f"(β = {pct(p.beta, 2)}).")
    salvar(fig, "poster_metodologia_mecanismo.png")


# --------------------------------------------------------------------------
# Resultados -- tamanho do efeito e calibração (versão enxuta da fig1)
# --------------------------------------------------------------------------
def efeito_calibracao():
    df = ler("varredura.csv")
    df = df[np.isclose(df["beta"], REF_BETA) & np.isclose(df["pi"], REF_PI)]
    df = df.sort_values("f_base")
    base = df[df["braco"] == "LOOKUP"].set_index("f_base")["prec_media"]

    fig, ax = plt.subplots(1, 2, figsize=(12, 6.2))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.80, bottom=0.30, wspace=0.28)
    titulo(fig, "B ganha pouca precisão; RA no prior descalibra o modelo")

    zero = ax[0].axhline(0, color=COR["LOOKUP"], lw=LARGURA["LOOKUP"])
    zero.set_dashes(TRACO["LOOKUP"])
    for b in ("A", "B", "C"):
        d = df[df["braco"] == b].set_index("f_base")
        diff = (d["prec_media"] - base) * 100
        linha(ax[0], diff.index, diff.values, b)
    ax[0].set_ylabel("Diferença de precisão (p.p.)")
    painel(ax[0], "(a) Precisão contra a tabela empírica")

    for b in ("A", "B", "C"):
        d = df[df["braco"] == b]
        linha(ax[1], d["f_base"], d["ece_media"], b)
    fim_ab = df[(df["braco"].isin(["A", "B"])) & np.isclose(df["f_base"], REF_F)]["ece_media"].max()
    ax[1].annotate(f"A e B ≈ {num(fim_ab, 3).lstrip('+')}", (0.30, fim_ab),
                   xytext=(0, 14), textcoords="offset points", ha="center",
                   fontsize=13, color=TINTA_SECUNDARIA)
    ax[1].set_ylabel("Erro de calibração (ECE)")
    painel(ax[1], "(b) Calibração")

    for a in ax:
        a.set_xlabel("Ruído da evidência")
    eixo_ptbr(*ax)
    fig.legend(handles=chaves_legenda(("A", "B", "C", "LOOKUP"), ROT),
               loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.08),
               handlelength=2.4, columnspacing=1.6)
    rodape(fig, "Configuração de referência (β = 0,55; π = 0,15). "
                "Tabela empírica = linha zero do painel (a).")
    salvar(fig, "poster_resultados_efeito_calibracao.png")


# --------------------------------------------------------------------------
# Resultados -- quem paga o falso positivo (versão enxuta da fig2)
# --------------------------------------------------------------------------
def equidade():
    df = ler("fpr_por_ra.csv").sort_values("cobertura")
    df["cobertura"] *= 100
    eq = ler("equidade.csv")
    n_pos, n_tot = int((eq["corr_B"] >= 0).sum()), len(eq)

    fig, ax = plt.subplots(figsize=(10.5, 6.8))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.34)
    rotulos = {}
    for b in ("RULE_CNT", "A", "B", "C"):
        y = df[b] * 100
        r = np.corrcoef(df["cobertura"], y)[0, 1]
        rotulos[b] = f"{ROT[b]} (r = {num(r, 3)})"
        linha(ax, df["cobertura"], y, b, marker="o", markersize=9)

    ceil = df[df["ra"] == "Ceilândia"].iloc[0]
    pp = df[df["ra"] == "Plano Piloto"].iloc[0]
    ax.annotate("Ceilândia", (ceil["cobertura"], ceil["C"] * 100), xytext=(12, -2),
                textcoords="offset points", va="center", fontsize=13, color=TINTA_SECUNDARIA)
    ax.annotate("Plano Piloto", (pp["cobertura"], pp["C"] * 100), xytext=(8, 24),
                textcoords="offset points", ha="right", va="center", fontsize=13,
                color=TINTA_SECUNDARIA)
    ax.set_ylim(bottom=-0.8)
    ax.set_xlabel("Cobertura do cadastro da RA (%)")
    ax.set_ylabel("Inocentes enviados à revisão (%)")
    eixo_ptbr(ax)
    titulo(fig, "Inocentes de RAs com cadastro pior vão mais à revisão")
    fig.legend(handles=chaves_legenda(("RULE_CNT", "A", "B", "C"), rotulos, marker="o",
                                      markersize=8),
               loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.1),
               handlelength=2.4, columnspacing=1.8)
    rodape(fig, "Configuração de referência; fraude idêntica em todas as RAs; cobertura "
                f"estipulada.\nB só inverte o sinal em {n_pos} das {n_tot} configurações testadas.")
    salvar(fig, "poster_resultados_equidade.png")


# --------------------------------------------------------------------------
# Resultados -- robustez dos achados na grade inteira
# --------------------------------------------------------------------------
def robustez():
    v = ler("varredura.csv").pivot_table(index=["f_base", "beta", "pi"], columns="braco",
                                         values=["prec_media", "brier_media", "ece_media"])
    eq = ler("equidade.csv")
    nv, ne = len(v), len(eq)
    c_pior = int(((v["brier_media"]["C"] > v["brier_media"]["A"])
                  & (v["ece_media"]["C"] > v["ece_media"]["A"])).sum())
    b_prec = int((v["prec_media"]["B"] > v["prec_media"]["LOOKUP"]).sum())
    cnt_neg = int((eq["corr_RULE_CNT"] < -0.5).sum())
    b_eq = int((eq["corr_B"] >= -0.10).sum())
    achados = [
        ("RA no prior (C) piora a calibração", c_pior, nv, "C", True),
        ("RA na verossimilhança (B) ganha precisão", b_prec, nv, "B", True),
        ("Sem RA no modelo, o cadastro pior é penalizado", cnt_neg, ne, "RULE_CNT", True),
        ("B corrige a disparidade (critério pré-registrado)", b_eq, ne, "B", b_eq == ne),
    ]

    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    fig.subplots_adjust(left=MARGEM, right=0.97, top=0.86, bottom=0.2)
    for i, (texto, n, tot, braco, passou) in enumerate(achados):
        frac = 100 * n / tot
        ax.barh(i, frac, height=0.42, color=COR[braco] if passou else to_rgba(COR[braco], 0.25),
                edgecolor=COR[braco], lw=0 if passou else 2.2, hatch=None if passou else "//")
        ax.text(0, i - 0.36, texto, va="bottom", fontsize=15, color=TINTA_PRIMARIA)
        marca = "✓ sustentado" if passou else "✗ reprovado"
        ax.text(frac + 1.5, i, f"{n}/{tot}  {marca}", va="center", fontsize=14,
                color=TINTA_PRIMARIA, fontweight="bold" if not passou else "normal")
    ax.set_yticks([])
    ax.set_ylim(len(achados) - 0.55, -0.95)   # espaço para o rótulo da 1ª linha
    ax.set_xlim(0, 135)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Configurações em que o achado vale (%)")
    titulo(fig, "Três achados se sustentam; B falha na equidade")
    rodape(fig, f"Grade: {nv} configurações para precisão e calibração, {ne} para equidade. "
                f"O critério de B exigia {ne}/{ne}.")
    salvar(fig, "poster_resultados_robustez.png")


# --------------------------------------------------------------------------
# Conclusão -- amplitude da disparidade entre RAs
# --------------------------------------------------------------------------
def amplitude():
    eq = ler("equidade.csv")
    bracos = ("A", "B", "C")
    med = {b: eq[f"amplitude_{b}"].median() * 100 for b in bracos}
    lo = {b: eq[f"amplitude_{b}"].min() * 100 for b in bracos}
    hi = {b: eq[f"amplitude_{b}"].max() * 100 for b in bracos}

    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    fig.subplots_adjust(left=0.30, right=0.96, top=0.86, bottom=0.25)
    for i, b in enumerate(bracos):
        ax.barh(i, med[b], height=0.56, color=COR[b])
        ax.plot([lo[b], hi[b]], [i, i], color=TINTA_SECUNDARIA, lw=2, solid_capstyle="butt")
        ax.plot([lo[b], lo[b]], [i - 0.12, i + 0.12], color=TINTA_SECUNDARIA, lw=2)
        ax.plot([hi[b], hi[b]], [i - 0.12, i + 0.12], color=TINTA_SECUNDARIA, lw=2)
        extra = "" if b == "A" else f"  ({pct(med[b] / med['A'])}× A)"
        ax.text(hi[b] + 0.6, i, f"{pct(med[b])} p.p.{extra}", va="center", fontsize=14,
                color=TINTA_PRIMARIA)
    ax.set_yticks(range(len(bracos)), [ROT[b] for b in bracos])
    ax.invert_yaxis()
    ax.set_xlim(0, 33)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(VIRGULA)
    ax.set_xlabel("Diferença de falso positivo entre RAs (p.p.)")
    titulo(fig, "B e C ampliam a disparidade entre RAs")
    rodape(fig, "Diferença entre a RA mais e a menos penalizada, entre inocentes. "
                f"Barra: mediana em {len(eq)} configurações;\ntraço: mínimo a máximo.")
    salvar(fig, "poster_conclusao_amplitude.png")


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    for f in (objetivo, metodologia, efeito_calibracao, equidade, robustez, amplitude):
        f()
    for nome in sorted(os.listdir(FIG)):
        if nome.startswith("poster_"):
            print("-> figuras/" + nome)
