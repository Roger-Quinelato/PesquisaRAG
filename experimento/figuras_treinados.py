"""Figuras dos bracos treinados (fig6, fig7, fig8). Nao toca em figuras.py nem
em figuras_relatorio.py, cujas figuras continuam byte a byte iguais -- so
reaproveita a paleta, os rotulos e o binning do ECE.

Uso:  python experimento/figuras_treinados.py
Saida: figuras/fig6_treinados_precisao_ece.png
       figuras/fig7_treinados_fpr_ra.png
       figuras/fig8_treinados_confiabilidade.png

Cor = onde a RA entra (azul ausente, laranja verossimilhanca/feature, agua
prior/taxa), como em todas as figuras; o marcador distingue a familia do
modelo. Deterministico: mesmas sementes e ordem de rng de varredura.py e
metadados de PNG fixos.
"""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import Params, gerar                                  # noqa: E402
from bracos import BRACOS, calcular                                # noqa: E402
from bracos_ml import BRACOS_ML, calcular_ml                       # noqa: E402
from metricas import ece, precisao_topk                            # noqa: E402
from varredura import K                                            # noqa: E402
from figuras import FIG                                            # noqa: E402
import figuras                                                     # noqa: E402
from figuras_relatorio import (META, N, SEMENTES, BINS, _bins_ece,  # noqa: E402
                               REF_BETA, REF_PI, REF_RUIDO)
from paleta_sns import (COR, ROTULO, TRACO, LARGURA, REFERENCIA,    # noqa: E402
                        TINTA_PRIMARIA, TINTA_MUTED, AZUL, LARANJA, AGUA,
                        VIRGULA, eixo_ptbr, configurar_estilo)

configurar_estilo()

POSICOES = (
    ("RA ausente", ("A", "A_NB", "D_ML", "D_PL", "D_ISO")),
    ("RA na verossimilhança ou como feature", ("B", "B_NB", "E_ML", "E_PL", "E_ISO")),
    ("RA no prior ou como taxa", ("C", "C_NB", "F_ML", "F_PL", "F_ISO")),
)
COR_POSICAO = (AZUL, LARANJA, AGUA)
MARCADOR = {"fechado": "o", "nb": "s", "ada": "^", "platt": "D", "iso": "v"}
NOME_FAMILIA = {"fechado": "Fechado (parâmetros do gerador)",
                "nb": "Naive Bayes treinado",
                "ada": "AdaBoost",
                "platt": "AdaBoost + Platt",
                "iso": "AdaBoost + isotônica"}


def familia(b):
    if b in ("A", "B", "C"):
        return "fechado"
    return {"NB": "nb", "ML": "ada", "PL": "platt", "ISO": "iso"}[b.split("_")[1]]


def ler(nome):
    # Le figuras.RES na hora da chamada, nao na importacao.
    with open(os.path.join(figuras.RES, nome), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def chave_familia(fam, **kw):
    return Line2D([], [], ls="none", marker=MARCADOR[fam], ms=9, color=TINTA_MUTED,
                  mec="white", mew=1.2, label=NOME_FAMILIA[fam], **kw)


# --------------------------------------------------------------------------
# fig6 -- precisao e ECE de todos os bracos, agrupados por onde a RA entra
# --------------------------------------------------------------------------
def estatisticas():
    idx = {}
    for L in ler("varredura.csv"):
        idx.setdefault((L["f_base"], L["beta"], L["pi"]), {})[L["braco"]] = L
    out = {}
    for b in BRACOS + BRACOS_ML:
        d = np.array([100 * (float(v[b]["prec_media"]) - float(v["LOOKUP"]["prec_media"]))
                      for v in idx.values()])
        e = np.array([float(v[b]["ece_media"]) for v in idx.values()])
        out[b] = (np.percentile(d, [25, 50, 75]), np.percentile(e, [25, 50, 75]))
    return out, len(idx)


def fig6():
    est, n_cfg = estatisticas()
    # Linhas de cima para baixo: cabecalho do grupo e seus cinco bracos.
    linhas = []
    for g, (titulo, bracos) in enumerate(POSICOES):
        linhas.append(("titulo", titulo, g))
        linhas += [("braco", b, g) for b in bracos]
    ys = np.arange(len(linhas))[::-1]

    fig, (ax_p, ax_e) = plt.subplots(1, 2, figsize=(15.4, 9.4), sharey=True,
                                     gridspec_kw={"wspace": 0.08})
    ax_p.axvline(0, color=REFERENCIA, lw=LARGURA["LOOKUP"], dashes=TRACO["LOOKUP"], zorder=1)
    for y, (tipo, nome, g) in zip(ys, linhas):
        if tipo == "titulo":
            continue
        cor, mk = COR_POSICAO[g], MARCADOR[familia(nome)]
        for ax, (q1, q2, q3) in ((ax_p, est[nome][0]), (ax_e, est[nome][1])):
            ax.plot([q1, q3], [y, y], color=cor, lw=2.2, solid_capstyle="round", zorder=2)
            ax.plot([q2], [y], ls="none", marker=mk, ms=10, color=cor,
                    mec="white", mew=1.6, zorder=3)

    # Cabecalho do grupo dentro do painel, alinhado a esquerda: como rotulo de
    # tick ele e' longo demais e sai cortado da figura.
    ax_p.set_yticks(ys)
    ax_p.set_yticklabels([nome if tipo == "braco" else "" for tipo, nome, _ in linhas],
                         fontsize=12.5, color=TINTA_PRIMARIA)
    ax_p.tick_params(axis="y", length=0)
    faixa = blended_transform_factory(ax_p.transAxes, ax_p.transData)
    for y, (tipo, nome, _) in zip(ys, linhas):
        if tipo == "titulo":
            ax_p.text(0.0, y, nome.upper(), transform=faixa, ha="left", va="center",
                      fontsize=11.5, fontweight="bold", color=TINTA_PRIMARIA, zorder=4,
                      bbox=dict(facecolor="white", edgecolor="none", pad=2))
    for ax in (ax_p, ax_e):
        ax.grid(axis="y", visible=False)
        sns.despine(ax=ax, left=True)

    ax_p.set_ylim(ys.min() - 0.7, ys.max() + 0.9)
    ax_p.set_xlabel("Precisão sob orçamento menos a da tabela empírica (p.p.)")
    ax_p.set_title("(a) Precisão nos 10% mais suspeitos", loc="left")
    ax_e.set_xscale("log")
    ax_e.set_xlabel("Erro de calibração esperado (ECE, escala log)")
    ax_e.set_title("(b) Calibração", loc="left")
    # So' o eixo x: eixo_ptbr sobrescreveria os rotulos fixos do eixo y.
    ax_p.xaxis.set_major_formatter(VIRGULA)
    ax_e.xaxis.set_major_formatter(VIRGULA)

    chaves = [chave_familia(f) for f in MARCADOR]
    chaves.append(Line2D([], [], color=REFERENCIA, lw=LARGURA["LOOKUP"],
                         dashes=TRACO["LOOKUP"], label="Tabela empírica (referência zero)"))
    fig.legend(handles=chaves, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 0.075), fontsize=12)
    fig.suptitle("Precisão e calibração de todos os braços, agrupados por onde a RA entra",
                 fontsize=15.5, y=0.975)
    fig.text(0.07, 0.012,
             f"Marcador = mediana nas {n_cfg} configurações; traço = intervalo interquartil. "
             "Cor = onde a RA entra. Os braços treinados são avaliados só na metade de teste\n"
             "(N ≈ 20.000); os fechados e a tabela empírica, na amostra inteira (N = 40.000). "
             "B recebe o falso positivo verdadeiro do gerador (oráculo). O ECE da tabela\n"
             "empírica (~0) é degenerado, porque ela é ajustada nos dados em que é avaliada, "
             "e por isso fica fora do painel (b).",
             fontsize=10, color=TINTA_MUTED, va="bottom", linespacing=1.5)
    fig.subplots_adjust(left=0.16, right=0.98, top=0.9, bottom=0.25)
    fig.savefig(os.path.join(FIG, "fig6_treinados_precisao_ece.png"), metadata=META)
    plt.close(fig)


# --------------------------------------------------------------------------
# fig7 -- falso positivo por RA na referencia, por posicao da RA
# --------------------------------------------------------------------------
def fig7():
    R = sorted(ler("fpr_por_ra.csv"), key=lambda r: float(r["cobertura"]))
    cob = np.array([100 * float(r["cobertura"]) for r in R])
    E = ler("equidade.csv")

    fig, axes = plt.subplots(1, 3, figsize=(17.4, 6.6), sharey=True,
                             gridspec_kw={"wspace": 0.07})
    for g, (ax, (titulo, bracos)) in enumerate(zip(axes, POSICOES)):
        for b in bracos[:3]:
            y = np.array([100 * float(r[b]) for r in R])
            n_ok = sum(float(L[f"corr_{b}"]) >= -0.10 for L in E)
            ln, = ax.plot(cob, y, color=COR_POSICAO[g], lw=LARGURA[b],
                          marker=MARCADOR[familia(b)], ms=8, mec="white", mew=1.4,
                          label=f"{b}: {NOME_FAMILIA[familia(b)].split(' (')[0]}"
                                f" — corr ≥ −0,10 em {n_ok}/{len(E)}")
            if TRACO[b]:
                ln.set_dashes(TRACO[b])
        ax.set_title(titulo, loc="left", fontsize=13.5)
        ax.set_xlabel("Cobertura do cadastro territorial (%)")
        ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17),
                  fontsize=10.5, handlelength=3.2)
        sns.despine(ax=ax, left=True)
        eixo_ptbr(ax)
    axes[0].set_ylabel("Inocentes enviados à revisão (%)")
    fig.suptitle("Quem paga o falso positivo, por família de modelo\n"
                 "(configuração de referência: β = 0,55; π = 0,15; ruído = 0,16)",
                 fontsize=15, y=0.99)
    fig.text(0.05, 0.015,
             "A contagem na legenda é o critério pré-registrado de equidade (corr(cobertura, FPR) "
             "≥ −0,10) nas 48 configurações de β × π × ruído; atendê-lo em todas seria\n"
             "corrigir a disparidade. Os braços treinados são avaliados só na metade de teste. "
             "Taxa de fraude idêntica em todas as RAs, por construção.",
             fontsize=10, color=TINTA_MUTED, va="bottom", linespacing=1.5)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.85, bottom=0.36)
    fig.savefig(os.path.join(FIG, "fig7_treinados_fpr_ra.png"), metadata=META)
    plt.close(fig)


# --------------------------------------------------------------------------
# fig8 -- diagrama de confiabilidade: A, Naive Bayes e AdaBoost cru/calibrado
# --------------------------------------------------------------------------
BRACOS_F8 = ("A", "A_NB", "D_ML", "D_PL", "D_ISO")


def predicoes_referencia():
    """Regera as predicoes por caso na referencia, replicando a ordem de rng de
    varredura.uma_config: gerar, calcular, os seis topk dos fechados e so' entao
    calcular_ml. Qualquer desvio muda o split, e conferir_ece acusa."""
    params = Params(pi=REF_PI, f_base=REF_RUIDO, beta=REF_BETA)
    P, Y, ece_sem = {b: [] for b in BRACOS_F8}, {b: [] for b in BRACOS_F8}, \
        {b: [] for b in BRACOS_F8}
    for semente in SEMENTES:
        rng = np.random.default_rng(semente)
        ra, F, E, f_true = gerar(N, params, rng)
        fechados = calcular(ra, F, E, f_true, params)
        for s in fechados.values():
            precisao_topk(s, F, K, rng)
        treinados, idx_teste = calcular_ml(ra, F, E, params, rng)
        for b in BRACOS_F8:
            s, y = (fechados[b], F) if b in fechados else (treinados[b], F[idx_teste])
            p = np.clip(s, 0.0, 1.0)
            P[b].append(p); Y[b].append(y); ece_sem[b].append(ece(p, y))
    return ({b: np.concatenate(v) for b, v in P.items()},
            {b: np.concatenate(v) for b, v in Y.items()},
            {b: float(np.mean(v)) for b, v in ece_sem.items()})


def fig8(P, Y, ece_med):
    # Os quatro calibrados coincidem com a diagonal: larguras e alfas
    # decrescentes fazem todos aparecerem, como na fig3.
    estilo = {"A": (6.5, 0.30, 3), "A_NB": (3.2, 1.0, 4), "D_PL": (2.4, 1.0, 5),
              "D_ISO": (1.6, 1.0, 6), "D_ML": (2.4, 1.0, 7)}
    fig, ax = plt.subplots(figsize=(9.4, 8.2))
    ax.plot([0, 1], [0, 1], color="#444444", lw=1.6, ls=(0, (4, 3)), zorder=1,
            label="Calibração perfeita")
    for b in BRACOS_F8:
        lw, alfa, z = estilo[b]
        p, y = P[b], Y[b]
        idx = _bins_ece(p)
        xs, ys, ws = [], [], []
        for k in range(BINS):
            m = idx == k
            if m.any():
                xs.append(p[m].mean()); ys.append(y[m].mean()); ws.append(m.mean())
        rotulo = (f"{b}: {NOME_FAMILIA[familia(b)].split(' (')[0]}  (ECE = "
                  + f"{ece_med[b]:.4f}".replace(".", ",") + ")")
        ln, = ax.plot(xs, ys, color=COR[b], lw=lw, alpha=alfa, zorder=z,
                      marker=MARCADOR[familia(b)], ms=8, mec="white", mew=1.2, label=rotulo)
        if TRACO[b]:
            ln.set_dashes(TRACO[b])
        ax.scatter(xs, ys, s=30 + 900 * np.array(ws), color=COR[b], alpha=0.25,
                   edgecolors="none", zorder=2)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Probabilidade prevista (média do bin)")
    ax.set_ylabel("Frequência observada de fraude latente")
    ax.set_title("O AdaBoost cru comprime os scores; Platt e isotônica os recalibram\n"
                 "(β = 0,55; π = 0,15; ruído = 0,16 — configuração de referência)")
    ax.legend(frameon=False, loc="upper left", fontsize=11, handlelength=3.0)
    sns.despine(ax=ax, left=True)
    eixo_ptbr(ax)
    fig.text(0.06, 0.012,
             "10 bins de largura igual, o mesmo binning de metricas.ece. Área do círculo "
             "proporcional à fração de casos no bin.\n"
             "ECE = média por semente, idêntica a ece_media de resultados/varredura.csv.\n"
             "A é avaliado na amostra inteira (N = 40.000); os treinados, só na metade de teste.",
             fontsize=9.5, color=TINTA_MUTED, va="bottom", linespacing=1.5)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.89, bottom=0.19)
    fig.savefig(os.path.join(FIG, "fig8_treinados_confiabilidade.png"), metadata=META)
    plt.close(fig)


def conferir_ece(ece_med):
    """O ECE recalculado tem de bater com ece_media de varredura.csv. Para os
    treinados, isso so' acontece se o split foi replicado exatamente."""
    alvo = {}
    for L in ler("varredura.csv"):
        if (abs(float(L["f_base"]) - REF_RUIDO) < 1e-6
                and float(L["beta"]) == REF_BETA and float(L["pi"]) == REF_PI):
            alvo[L["braco"]] = float(L["ece_media"])
    print("\nCoerencia do ECE (recalculado x resultados/varredura.csv):")
    ok = True
    for b in BRACOS_F8:
        d = abs(ece_med[b] - alvo[b])
        ok &= d < 1e-9
        print(f"  {b:>7}: recalc={ece_med[b]:.10f}  varredura={alvo[b]:.10f}  |dif|={d:.2e}")
    print("  ->", "BATE" if ok else "NAO BATE -- split ou binning errado")
    return ok


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    fig6()
    fig7()
    P, Y, ece_med = predicoes_referencia()
    fig8(P, Y, ece_med)
    print("-> figuras/fig6_treinados_precisao_ece.png")
    print("-> figuras/fig7_treinados_fpr_ra.png")
    print("-> figuras/fig8_treinados_confiabilidade.png")
    conferir_ece(ece_med)
