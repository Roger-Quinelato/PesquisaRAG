"""Paleta e estilo compartilhados pelas figuras do projeto -- somente seaborn
por cima de matplotlib (backend obrigatorio de qualquer biblioteca de plot em
Python). Nao adiciona scipy/sklearn/etc: só `seaborn`, que por sua vez só
depende de numpy/pandas/matplotlib, já presentes no ambiente.

Cor por identidade de braço, fixa em todas as figuras -- nunca redistribuída
por filtro, corte ou ordenação (um viewer que aprendeu "B é laranja" não pode
ser traído por um recorte diferente da grade).

Paleta categórica: os 3 primeiros matizes (azul/laranja/água) de uma ordem
de 8 validada por Delta-E em OKLab sob protanopia/deuteranopia
(Machado-Oliveira-Fernandes 2009), nunca ciclada nem escolhida a olho --
são os únicos 3 matizes que passam a checagem all-pairs (necessária quando
qualquer duas marcas podem ficar lado a lado, caso de dispersão/pontos), o
que importa porque a Figura 2 combina linha com marcador. Vermelho entra
só como polo da paleta divergente (Figura 4), nunca como identidade
categórica -- validado com `node scripts/validate_palette.js
"#2a78d6,#eb6834,#e34948"`, que reprova o par vermelho-laranja adjacente
(Delta E 5,6 sob deuteranopia, abaixo do piso de 6). Os dois braços de
regra e a tabela empírica não entram na paleta categórica porque não são
objeto de comparação de identidade nesta pesquisa: são referências de
contexto (o piso e o teto), e por isso usam tons de tinta (texto) em vez
de matiz -- a mesma convenção que separa "dado" de "anotação".
"""
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import LinearSegmentedColormap

# --- tokens de tinta (texto, grade, referência) ----------------------------
TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_MUTED = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"

# --- paleta categórica validada (slots 1, 2, 3, 8) -------------------------
AZUL = "#2a78d6"
LARANJA = "#eb6834"
AGUA = "#1baf7a"
VERMELHO = "#e34948"
CINZA_NEUTRO = "#f0efec"   # ponto médio da divergente -- lê como "nada"
REFERENCIA = "#7a9e7e"     # sage desaturado -- só para o teto LOOKUP, não é
                           # identidade categórica; existe para não colidir
                           # visualmente com o cinza de RULE_OR/RULE_CNT

ROTULO = {
    "RULE_OR": "Regra binária (OR)",
    "RULE_CNT": "Regra por contagem",
    "LOOKUP": "Tabela empírica (teto não paramétrico)",
    "A": "A — território ignorado",
    "B": "B — território na verossimilhança",
    "C": "C — território no prior",
}

# Cor por identidade de braço -- fixa em toda figura. RULE_OR, RULE_CNT e
# LOOKUP são referências de contexto (piso e teto), não objeto de
# identidade; usam tinta, não matiz. A, B, C são os três braços bayesianos
# comparados entre si e recebem a paleta categórica validada.
COR = {
    "RULE_OR": TINTA_MUTED,
    "RULE_CNT": TINTA_SECUNDARIA,
    "LOOKUP": REFERENCIA,
    "A": AZUL,
    "B": LARANJA,
    "C": AGUA,
}
# Traços em pontos (on, off, ...) no formato que Line2D/seaborn aceitam.
TRACO = {
    "RULE_OR": (1, 1.6),        # pontilhado -- baseline mais fraco, de-ênfase
    "RULE_CNT": (5, 2),         # tracejado -- referência ordinal
    "LOOKUP": (5, 1, 1, 1),     # traço-ponto -- teto não implementável
    "A": "",
    "B": "",
    "C": "",
}
LARGURA = {"RULE_OR": 1.6, "RULE_CNT": 1.8, "LOOKUP": 1.8, "A": 2.4, "B": 2.4, "C": 2.4}

# Diverging blue<->red com ponto médio cinza neutro -- os dois polos lêem
# como opostos (quente/frio) e o meio lê como "nada", nunca um terceiro
# matiz. Usada só na Figura 4 (correlação, grandeza com polaridade).
DIVERGENTE = LinearSegmentedColormap.from_list(
    "territorio_divergente", [VERMELHO, CINZA_NEUTRO, AZUL], N=256)


def num(x, casas=2):
    """Número no padrão brasileiro: vírgula decimal e sinal de menos
    tipográfico. Os documentos são em português; ponto decimal destoaria."""
    return f"{x:+.{casas}f}".replace("-", "−").replace(".", ",")


def _tick_ptbr(x, _pos=None):
    return f"{x:g}".replace("-", "−").replace(".", ",")


VIRGULA = FuncFormatter(_tick_ptbr)


def eixo_ptbr(*eixos):
    """Aplica vírgula decimal aos ticks. Não usar em eixo com rótulo fixo
    definido por set_xticklabels -- o formatador sobrescreveria o rótulo."""
    for ax in eixos:
        ax.xaxis.set_major_formatter(VIRGULA)
        ax.yaxis.set_major_formatter(VIRGULA)


def configurar_estilo():
    """Tema seaborn com os tokens de tinta do projeto: grade em traço fino e
    recessivo (nunca tracejada -- isso é reservado a "projeção/limiar"),
    eixos sem moldura no topo/direita, texto em tinta primária/secundária,
    nunca na cor de uma série."""
    sns.set_theme(style="whitegrid", rc={
        "figure.dpi": 160,
        "font.size": 13,
        "axes.labelsize": 14,
        "axes.titlesize": 15,
        "legend.fontsize": 11.5,
        "axes.edgecolor": EIXO,
        "axes.labelcolor": TINTA_PRIMARIA,
        "text.color": TINTA_PRIMARIA,
        "xtick.color": TINTA_MUTED,
        "ytick.color": TINTA_MUTED,
        "grid.color": GRADE,
        "grid.linewidth": 1.0,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "legend.frameon": False,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
    })
    sns.set_palette([AZUL, LARANJA, AGUA, VERMELHO])


def chaves_legenda(bracos, rotulos=None, **kw):
    """Chaves de legenda em ordem fixa por identidade de braço -- nunca a
    ordem de inserção do matplotlib. O traço vai na chave: uma chave sólida
    para uma curva tracejada faz o leitor procurar a série errada."""
    rotulos = rotulos or ROTULO
    saida = []
    for b in bracos:
        h = Line2D([], [], color=COR[b], lw=LARGURA[b], label=rotulos[b], **kw)
        if TRACO[b]:
            h.set_dashes(TRACO[b])
        saida.append(h)
    return saida


def linha(ax, x, y, braco, **kw):
    """sns.lineplot de uma única série, com cor/traço/largura fixos pela
    identidade do braço -- wrapper fino para não repetir os três dicionários
    em cada figura. O traço é aplicado no Line2D devolvido por lineplot,
    porque o parâmetro `dashes` de lineplot só se aplica a um mapeamento
    `style`, não a uma chamada de série única."""
    kwargs = dict(color=COR[braco], linewidth=LARGURA[braco], ax=ax, legend=False)
    kwargs.update(kw)
    resultado = sns.lineplot(x=x, y=y, **kwargs)
    dash = TRACO[braco]
    if dash:
        resultado.lines[-1].set_dashes(dash)
    return resultado
