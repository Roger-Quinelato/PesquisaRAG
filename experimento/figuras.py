"""As duas figuras do banner. Le resultados/, escreve figuras/."""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import RAS, COBERTURA  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES, FIG = os.path.join(RAIZ, "resultados"), os.path.join(RAIZ, "figuras")
REF_BETA, REF_PI = 0.55, 0.15

ROTULO = {"RULE_OR": "Regra binária (OR)", "RULE_CNT": "Regra por contagem",
          "LOOKUP": "Tabela empírica", "A": "A — território ignorado",
          "B": "B — território na verossimilhança", "C": "C — território no prior"}
COR = {"RULE_OR": "#999999", "RULE_CNT": "#5B7DB1", "LOOKUP": "#7A9E7E",
       "A": "#1F4E79", "B": "#C1651A", "C": "#A4243B"}
ESTILO = {"RULE_OR": ":", "RULE_CNT": "--", "LOOKUP": "-.", "A": "-", "B": "-", "C": "-"}

plt.rcParams.update({"font.size": 13, "axes.labelsize": 14, "axes.titlesize": 15,
                     "legend.fontsize": 11.5, "figure.dpi": 160})


def ler(nome):
    with open(os.path.join(RES, nome), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fig1():
    R = [L for L in ler("varredura.csv")
         if float(L["beta"]) == REF_BETA and float(L["pi"]) == REF_PI]
    serie = {}
    for b in ROTULO:
        d = sorted((L for L in R if L["braco"] == b), key=lambda L: float(L["f_base"]))
        serie[b] = (np.array([float(L["f_base"]) for L in d]),
                    np.array([float(L["prec_media"]) for L in d]),
                    np.array([float(L["ece_media"]) for L in d]))

    fig, ax = plt.subplots(1, 3, figsize=(17.5, 5.2))

    for b in ROTULO:
        x, prec, _ = serie[b]
        ax[0].plot(x, prec, ESTILO[b], color=COR[b], lw=2.4, label=ROTULO[b])
    ax[0].set_ylabel("Precisão no topo 10%")
    ax[0].set_title("Utilidade da triagem sob orçamento")
    ax[0].legend(frameon=False)

    # Painel 2: diferença contra a tabela empírica. Sem ele o ganho de B fica
    # escondido sob as curvas sobrepostas -- e o tamanho do efeito é o ponto.
    base = serie["LOOKUP"][1]
    for b in ("RULE_CNT", "A", "B", "C"):
        x, prec, _ = serie[b]
        ax[1].plot(x, (prec - base) * 100, ESTILO[b], color=COR[b], lw=2.4,
                   label=ROTULO[b])
    ax[1].axhline(0, color="#7A9E7E", lw=2.4, ls="-.")
    ax[1].set_ylabel("Diferença contra a tabela empírica (p.p.)")
    ax[1].set_title("Tamanho do efeito — o ganho de B é modesto")
    ax[1].legend(frameon=False, loc="lower left")

    for b in ("LOOKUP", "A", "B", "C"):
        x, _, e = serie[b]
        ax[2].plot(x, e, ESTILO[b], color=COR[b], lw=2.4, label=ROTULO[b])
    ax[2].set_ylabel("Erro de calibração esperado (ECE)")
    ax[2].set_title("Calibração — território no prior colapsa")
    ax[2].legend(frameon=False)

    for a in ax:
        a.set_xlabel("Ruído da evidência (taxa de falso-positivo base)")
        a.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig1_precisao_calibracao.png"), bbox_inches="tight")
    plt.close(fig)


def fig2():
    R = ler("fpr_por_ra.csv")
    cob = np.array([float(L["cobertura"]) for L in R])
    nomes = [L["ra"] for L in R]
    fig, ax = plt.subplots(figsize=(9.5, 6))
    for b in ("RULE_CNT", "A", "B", "C"):
        y = np.array([float(L[b]) for L in R]) * 100
        r = np.corrcoef(cob, y)[0, 1]
        ax.plot(cob * 100, y, "o-", color=COR[b], lw=2.4, ms=7,
                label=f"{ROTULO[b]}  (r = {r:+.2f})")
    for x, y, nm in zip(cob * 100, [float(L["C"]) * 100 for L in R], nomes):
        if nm == "Ceilândia":
            ax.annotate(nm, (x, y), textcoords="offset points", xytext=(14, -4),
                        ha="left", fontsize=11, color="#555555")
        elif nm == "Plano Piloto":
            ax.annotate(nm, (x, y), textcoords="offset points", xytext=(-6, 12),
                        ha="right", fontsize=11, color="#555555")
    ax.set_xlabel("Cobertura do cadastro territorial da Região Administrativa (%)")
    ax.set_ylabel("Inocentes enviados à revisão (%)")
    ax.set_title("Quem paga o falso positivo\n"
                 "(taxa de fraude idêntica em todas as regiões, por construção)")
    ax.margins(y=0.12)
    ax.grid(alpha=0.25); ax.legend(frameon=False, loc="upper right")
    # Ressalva obrigatoria: a inversao de sinal de B NAO e' robusta.
    ax.text(0.0, -0.20,
            "Configuração de referência (β = 0,55; π = 0,15; ruído = 0,16). "
            "A correlação negativa em A e C se mantém em 48/48 configurações;\n"
            "a inversão de sinal em B ocorre em apenas 33/48, falhando sob ruído "
            "baixo e gradiente territorial íngreme.",
            transform=ax.transAxes, fontsize=10, color="#666666", va="top")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig2_equidade_territorial.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    fig1(); fig2()
    print("-> figuras/fig1_precisao_calibracao.png")
    print("-> figuras/fig2_equidade_territorial.png")
