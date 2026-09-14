"""Figuras do relatorio (fig3, fig4, fig5). Nao toca em figuras.py, que
produz as figuras ja aprovadas do banner -- so reaproveita a paleta e os
rotulos de paleta_sns.py. Renderizacao via seaborn sobre matplotlib.

Uso:  python experimento/figuras_relatorio.py
Saida: figuras/fig3_confiabilidade.png
       figuras/fig4_heatmap_beta_pi.png
       figuras/fig5_sensibilidade.png

Deterministico: mesmas sementes de varredura.py e metadados de PNG fixos, de
modo que duas execucoes produzem bytes identicos.
"""
import csv, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import Params, gerar                    # noqa: E402
from bracos import calcular                          # noqa: E402
from metricas import ece                             # noqa: E402
from figuras import RAIZ, RES, FIG                    # noqa: E402
from paleta_sns import (COR, ROTULO, TRACO, LARGURA, DIVERGENTE,  # noqa: E402
                        num, eixo_ptbr, VIRGULA, configurar_estilo, linha)

configurar_estilo()

# Mesmos parametros de varredura.py -- se divergirem, o ECE anotado na fig3
# deixa de bater com ece_media de resultados/varredura.csv.
N = 40_000
SEMENTES = range(8)
BINS = 10
REF_BETA, REF_PI, REF_RUIDO = 0.55, 0.15, 0.16
GRADE_BETA = (0.25, 0.40, 0.55, 0.70)
GRADE_PI = (0.05, 0.10, 0.15, 0.25)
# Metadados fixos: sem isso o PNG carrega a versao do matplotlib e o hash muda
# entre ambientes, tornando o teste de determinismo inconclusivo.
META = {"Software": None}


def ler(nome):
    with open(os.path.join(RES, nome), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# --------------------------------------------------------------------------
# fig3 -- diagrama de confiabilidade
# --------------------------------------------------------------------------
def _bins_ece(p):
    """Binning IDENTICO ao de metricas.ece: 10 bins de largura igual,
    np.digitize sobre as bordas internas. Replicado (e nao importado) porque
    metricas.ece devolve so o escalar; qualquer divergencia aqui faria a
    figura contradizer o numero publicado de ECE."""
    edges = np.linspace(0.0, 1.0, BINS + 1)
    return np.clip(np.digitize(p, edges[1:-1]), 0, BINS - 1)


def predicoes_referencia():
    """Regera as predicoes por caso na config de referencia. A grade agregada
    nao as guarda. Devolve (scores_empilhados, F_empilhado, ece_media_por_braco)."""
    params = Params(pi=REF_PI, f_base=REF_RUIDO, beta=REF_BETA)
    acum_p, acum_y, ece_sem = {}, [], {}
    for semente in SEMENTES:
        rng = np.random.default_rng(semente)
        ra, F, E, f_true = gerar(N, params, rng)
        acum_y.append(F)
        for b, s in calcular(ra, F, E, f_true, params).items():
            p = np.clip(s, 0.0, 1.0)
            acum_p.setdefault(b, []).append(p)
            ece_sem.setdefault(b, []).append(ece(p, F))
    y = np.concatenate(acum_y)
    P = {b: np.concatenate(v) for b, v in acum_p.items()}
    # media dos ECE por semente -- e' assim que varredura.py calcula ece_media
    ece_med = {b: float(np.mean(v)) for b, v in ece_sem.items()}
    return P, y, ece_med


def fig3(P, y, ece_med):
    # LOOKUP, A e B praticamente coincidem com a diagonal. Larguras e alfas
    # decrescentes (nao as fixas de paleta_sns.LARGURA) fazem os tres
    # aparecerem em vez de um esconder o outro -- especifico desta figura.
    bracos = (("LOOKUP", 7.0, 0.32, 3), ("A", 3.0, 1.0, 4), ("B", 1.8, 1.0, 5),
              ("C", 2.6, 1.0, 6))
    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    ax.plot([0, 1], [0, 1], color="#444444", lw=1.6, ls=(0, (4, 3)),
            label="Calibração perfeita", zorder=1)
    for b, lw, alfa, z in bracos:
        p = P[b]
        idx = _bins_ece(p)
        xs, ys, ws = [], [], []
        for k in range(BINS):
            m = idx == k
            if m.any():
                xs.append(p[m].mean()); ys.append(y[m].mean()); ws.append(m.mean())
        rotulo = f"{ROTULO[b]}  (ECE = " + f"{ece_med[b]:.4f}".replace(".", ",") + ")"
        resultado = sns.lineplot(x=xs, y=ys, ax=ax, color=COR[b], linewidth=lw,
                                  alpha=alfa, zorder=z, legend=False, label=rotulo)
        if TRACO[b]:
            resultado.lines[-1].set_dashes(TRACO[b])
        resultado.lines[-1].set_solid_capstyle("round")
        ax.scatter(xs, ys, s=30 + 900 * np.array(ws), color=COR[b],
                   alpha=0.45, edgecolors="none", zorder=2)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Probabilidade prevista (média do bin)")
    ax.set_ylabel("Frequência observada de fraude latente")
    ax.set_title("Diagrama de confiabilidade\n"
                 "(β = 0,55; π = 0,15; ruído = 0,16 — configuração de referência)")
    sns.despine(ax=ax, left=True)
    ax.legend(frameon=False, loc="upper left")
    eixo_ptbr(ax)
    ax.text(0.0, -0.145,
            "10 bins de largura igual, o mesmo binning de metricas.ece. Área do marcador "
            "proporcional à fração de casos no bin.\n"
            "8 sementes × 40.000 casos agrupadas; o ECE anotado é a média por semente, "
            "idêntica a ece_media de resultados/varredura.csv.\n"
            "Ressalva: o ECE nulo da tabela empírica é degenerado — ela estima P(F | padrão) "
            "nos próprios dados em que é avaliada.",
            transform=ax.transAxes, fontsize=9.5, color=COR["LOOKUP"], va="top")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig3_confiabilidade.png"),
                bbox_inches="tight", metadata=META)
    plt.close(fig)


# --------------------------------------------------------------------------
# fig4 -- onde B inverte o sinal da correlacao
# --------------------------------------------------------------------------
def fig4():
    E = ler("equidade.csv")
    df = pd.DataFrame(E)
    for col in ("f_base", "beta", "pi", "corr_B"):
        df[col] = df[col].astype(float)
    ruidos = sorted(df["f_base"].unique())
    n_ok = int((df["corr_B"] >= -0.10).sum())
    n_pos = int((df["corr_B"] >= 0.0).sum())
    NT = len(df)

    fig, axes = plt.subplots(1, len(ruidos), figsize=(15.6, 5.4))
    ultimo = None
    for i, (ax, r) in enumerate(zip(axes, ruidos)):
        sub = df[np.isclose(df["f_base"], r)]
        M = (sub.pivot(index="beta", columns="pi", values="corr_B")
                .reindex(index=GRADE_BETA, columns=GRADE_PI))
        anot = M.map(lambda v: num(v))
        ultimo = sns.heatmap(
            M, ax=ax, cmap=DIVERGENTE, vmin=-1, vmax=1, center=0,
            annot=anot, fmt="", annot_kws={"fontsize": 11},
            linewidths=2, linecolor="white", cbar=False, square=False,
        )
        # Anel de reprovacao: borda preta nas celulas abaixo do criterio
        # pre-registrado (corr >= -0,10). Mesma semantica visual da figura
        # original -- reprovacao marcada por contorno, nao so por cor.
        for yi, beta in enumerate(GRADE_BETA):
            for xi, pi in enumerate(GRADE_PI):
                if M.loc[beta, pi] < -0.10:
                    ax.add_patch(plt.Rectangle((xi, yi), 1, 1, fill=False,
                                               edgecolor="#111111", lw=2.6))
        ax.set_xticklabels([f"{p:.2f}".replace(".", ",") for p in GRADE_PI])
        ax.set_yticklabels([f"{b:.2f}".replace(".", ",") for b in GRADE_BETA], rotation=0)
        ax.set_xlabel("π (prevalência de fraude)")
        ax.set_ylabel("β (gradiente territorial)" if i == 0 else "")
        ax.set_title(f"ruído = {r:.2f}".replace(".", ","))
    cb = fig.colorbar(ultimo.collections[0], ax=axes, fraction=0.022, pad=0.015)
    cb.set_label("corr(cobertura, FPR entre inocentes) — braço B")
    cb.ax.yaxis.set_major_formatter(VIRGULA)
    fig.suptitle("Onde B inverte o sinal da disparidade territorial — e onde não inverte\n"
                 f"critério pré-registrado (corr ≥ −0,10) atendido em {n_ok}/{NT}; "
                 f"sinal estritamente positivo em {n_pos}/{NT}. "
                 "Células com borda preta = reprovação.", fontsize=13.5, y=1.06)
    fig.savefig(os.path.join(FIG, "fig4_heatmap_beta_pi.png"),
                bbox_inches="tight", metadata=META)
    plt.close(fig)
    return n_ok, n_pos, NT


# --------------------------------------------------------------------------
# fig5 -- sensibilidade da diferenca contra a tabela empirica
# --------------------------------------------------------------------------
def _serie(df, beta, pi):
    sub = df[np.isclose(df["beta"], beta) & np.isclose(df["pi"], pi)]
    return sub.sort_values("f_base")


def fig5():
    V = ler("varredura.csv")
    df = pd.DataFrame(V)
    for col in ("f_base", "beta", "pi", "prec_media"):
        df[col] = df[col].astype(float)

    fig, axes = plt.subplots(2, 4, figsize=(18.0, 8.6), sharex=True, sharey=True)

    def painel(ax, beta, pi, titulo):
        sub = _serie(df, beta, pi)
        base = sub[sub["braco"] == "LOOKUP"].set_index("f_base")["prec_media"]
        ax.axhline(0, color=COR["LOOKUP"], lw=LARGURA["LOOKUP"], ls="-.")
        for b in ("RULE_CNT", "A", "B", "C"):
            d = sub[sub["braco"] == b].set_index("f_base")
            diff = (d["prec_media"] - base) * 100
            linha(ax, diff.index, diff.values, b)
        ax.set_title(titulo, fontsize=13)
        sns.despine(ax=ax, left=True)
        # Recorte: sem ele o unico ponto extremo da regra por contagem
        # (pi=0,10 e ruido=0,01: -9,1 p.p.) achata todos os demais paineis.
        ax.set_ylim(-4.6, 3.4)
        for b in ("RULE_CNT", "A", "B", "C"):
            d = sub[sub["braco"] == b].set_index("f_base")
            diff = (d["prec_media"] - base) * 100
            fora = diff[diff < -4.6]
            if len(fora):
                ax.annotate(f"{ROTULO[b]}: "
                            + f"{fora.min():.1f}".replace("-", "−").replace(".", ",")
                            + " p.p. fora de escala",
                            xy=(0.03, 0.04), xycoords="axes fraction", fontsize=9.5,
                            color=COR[b])

    for j, beta in enumerate(GRADE_BETA):
        painel(axes[0, j], beta, REF_PI,
               f"β = {beta:.2f}".replace(".", ",") + f"  (π = {REF_PI:.2f})".replace(".", ","))
    for j, pi in enumerate(GRADE_PI):
        painel(axes[1, j], REF_BETA, pi,
               f"π = {pi:.2f}".replace(".", ",") + f"  (β = {REF_BETA:.2f})".replace(".", ","))

    eixo_ptbr(*axes.ravel())
    axes[0, 0].set_ylabel("Diferença contra a\ntabela empírica (p.p.)")
    axes[1, 0].set_ylabel("Diferença contra a\ntabela empírica (p.p.)")
    for j in range(4):
        axes[1, j].set_xlabel("Ruído da evidência")
    handles = [plt.Line2D([], [], color=COR[b], lw=LARGURA[b], label=ROTULO[b])
               for b in ("LOOKUP", "RULE_CNT", "A", "B", "C")]
    fig.legend(handles=handles, frameon=False, ncol=5, loc="lower center",
               bbox_to_anchor=(0.5, -0.055), fontsize=12.5)
    fig.suptitle("A direção sobrevive à variação dos parâmetros\n"
                 "linha superior: varia β com π fixo — linha inferior: varia π com β fixo",
                 fontsize=15, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig5_sensibilidade.png"),
                bbox_inches="tight", metadata=META)
    plt.close(fig)


def conferir_ece(ece_med):
    """O ECE recalculado tem de bater com ece_media de varredura.csv na linha
    de referencia. Se nao bater, o binning da fig3 esta errado."""
    alvo = {}
    for L in ler("varredura.csv"):
        if (abs(float(L["f_base"]) - REF_RUIDO) < 1e-6
                and float(L["beta"]) == REF_BETA and float(L["pi"]) == REF_PI):
            alvo[L["braco"]] = float(L["ece_media"])
    print("\nCoerencia do ECE (recalculado x resultados/varredura.csv):")
    ok = True
    for b in ("LOOKUP", "A", "B", "C"):
        d = abs(ece_med[b] - alvo[b])
        ok &= d < 1e-9
        print(f"  {b:>7}: recalc={ece_med[b]:.10f}  varredura={alvo[b]:.10f}  |dif|={d:.2e}")
    print("  ->", "BATE" if ok else "NAO BATE -- binning errado")
    return ok


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    P, y, ece_med = predicoes_referencia()
    fig3(P, y, ece_med)
    n_ok, n_pos, NT = fig4()
    fig5()
    print("-> figuras/fig3_confiabilidade.png")
    print(f"-> figuras/fig4_heatmap_beta_pi.png  (B: {n_ok}/{NT} pelo criterio, "
          f"{n_pos}/{NT} com sinal positivo)")
    print("-> figuras/fig5_sensibilidade.png")
    conferir_ece(ece_med)
