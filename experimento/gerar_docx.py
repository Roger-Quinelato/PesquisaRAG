"""Converte os relatorios de Markdown para .docx.

Uso:
    python experimento/gerar_docx.py                  # todos os .md de relatorios/
    python experimento/gerar_docx.py caminho/arq.md   # um arquivo especifico

O .md continua sendo a fonte da verdade. O .docx e' derivado e regenerado -- nunca
edite o .docx diretamente, porque a proxima execucao o sobrescreve.

Subconjunto de Markdown suportado: titulos (# a ####), paragrafos, negrito, italico,
codigo inline, listas com marcador e numeradas, tabelas com barra vertical, imagens,
citacoes e blocos de codigo cercados.
"""
import os
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELATORIOS = os.path.join(RAIZ, "relatorios")

LARGURA_UTIL_CM = 16.0          # A4 com margens de 2,5 cm
# O negrito fecha em "**" nao seguido de outro "*", para que "**a *b***" case o
# trecho inteiro em vez de parar no meio e deixar um asterisco solto no texto.
RE_INLINE = re.compile(r"(\*\*.+?\*\*(?!\*)|(?<!\*)\*(?!\*)[^*]+\*(?!\*)|`[^`]+?`)")
RE_IMAGEM = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)\s*$")
RE_TITULO = re.compile(r"^(?P<nivel>#{1,6})\s+(?P<texto>.+?)\s*#*\s*$")
RE_LISTA_NUM = re.compile(r"^\s*\d+[.)]\s+(?P<texto>.+)$")
RE_LISTA_MARC = re.compile(r"^\s*[-*+]\s+(?P<texto>.+)$")
RE_SEPARADOR = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")


def escrever_inline(paragrafo, texto, negrito=False, italico=False):
    """Quebra o texto em trechos formatados e os adiciona como runs.
    Recursivo, para que enfase aninhada ("**negrito com *italico* dentro**")
    preserve as duas marcacoes em vez de perder a interna."""
    for trecho in RE_INLINE.split(texto):
        if not trecho:
            continue
        if len(trecho) > 4 and trecho.startswith("**") and trecho.endswith("**"):
            escrever_inline(paragrafo, trecho[2:-2], True, italico)
        elif len(trecho) > 2 and trecho.startswith("`") and trecho.endswith("`"):
            r = paragrafo.add_run(trecho[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(10)
            r.bold, r.italic = negrito, italico
        elif len(trecho) > 2 and trecho.startswith("*") and trecho.endswith("*"):
            escrever_inline(paragrafo, trecho[1:-1], negrito, True)
        else:
            # "\|" e' escape de markdown; fora de tabela ainda precisa virar "|".
            r = paragrafo.add_run(trecho.replace("\\|", "|"))
            r.bold, r.italic = negrito, italico


def linha_de_tabela(linha):
    return linha.lstrip().startswith("|") and linha.rstrip().endswith("|")


def inicia_bloco(linha):
    """A linha abre um novo bloco (em vez de continuar o anterior)?"""
    return bool(RE_TITULO.match(linha) or linha_de_tabela(linha)
                or RE_LISTA_NUM.match(linha) or RE_LISTA_MARC.match(linha)
                or RE_SEPARADOR.match(linha) or linha.strip().startswith("```")
                or linha.lstrip().startswith(">") or RE_IMAGEM.match(linha.strip()))


def juntar_continuacao(linhas, i, texto):
    """Absorve as linhas de continuacao de um item de lista.

    Sem isto, enfase que atravessa a quebra de linha no fonte ("**inicio ...
    \\n ... fim**") chega ao Word com os asteriscos visiveis, porque cada
    linha isolada tem marcadores desbalanceados."""
    while i < len(linhas) and linhas[i].strip() and not inicia_bloco(linhas[i]):
        texto += " " + linhas[i].strip()
        i += 1
    return texto, i


def celulas(linha):
    """Divide a linha em celulas. Barra escapada (\\|) e' conteudo, nao delimitador --
    a notacao condicional do projeto, como P(F | padrao), depende disso."""
    corpo = linha.strip()
    corpo = corpo[1:] if corpo.startswith("|") else corpo
    if corpo.endswith("|") and not corpo.endswith("\\|"):
        corpo = corpo[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", corpo)]


def eh_separador_de_tabela(linha):
    return bool(re.fullmatch(r"\|[\s:|-]+\|", linha.strip()))


def inserir_tabela(doc, blocos):
    """blocos: linhas de uma tabela markdown, ja sem a linha separadora."""
    dados = [celulas(l) for l in blocos]
    # Cabecalho vazio ("| | |") e' tabela de definicao, sem cabecalho real.
    # Mante-lo produziria uma primeira linha em branco e em negrito no Word.
    com_cabecalho = bool(dados) and any(c for c in dados[0])
    if not com_cabecalho:
        dados = dados[1:]
    if not dados:
        return
    n_col = max(len(l) for l in dados)
    tabela = doc.add_table(rows=len(dados), cols=n_col)
    tabela.style = "Table Grid"
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, linha in enumerate(dados):
        for j in range(n_col):
            cel = tabela.cell(i, j)
            cel.text = ""
            p = cel.paragraphs[0]
            escrever_inline(p, linha[j] if j < len(linha) else "")
            for run in p.runs:
                run.font.size = Pt(9)
                if i == 0 and com_cabecalho:
                    run.bold = True
    doc.add_paragraph()


def inserir_imagem(doc, src, alt, base):
    for cand in (os.path.join(base, src), os.path.join(RAIZ, src), src):
        caminho = os.path.normpath(cand)
        if os.path.isfile(caminho):
            doc.add_picture(caminho, width=Cm(LARGURA_UTIL_CM))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            if alt:
                leg = doc.add_paragraph()
                leg.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = leg.add_run(alt)
                r.italic = True
                r.font.size = Pt(9)
            return True
    # Imagem ausente e' erro visivel, nao silencioso: o .docx vai para a banca.
    p = doc.add_paragraph()
    p.add_run("[IMAGEM NAO ENCONTRADA: " + src + "]").bold = True
    print("   AVISO: imagem nao encontrada -> " + src)
    return False


def converter(caminho_md):
    base = os.path.dirname(os.path.abspath(caminho_md))
    with open(caminho_md, encoding="utf-8") as fh:
        linhas = fh.read().splitlines()

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.5)
        s.left_margin = s.right_margin = Cm(2.5)

    i, em_codigo, buffer_codigo = 0, False, []
    while i < len(linhas):
        linha = linhas[i]

        if linha.strip().startswith("```"):
            if em_codigo:
                p = doc.add_paragraph()
                r = p.add_run("\n".join(buffer_codigo))
                r.font.name = "Consolas"
                r.font.size = Pt(9)
                buffer_codigo, em_codigo = [], False
            else:
                em_codigo = True
            i += 1
            continue
        if em_codigo:
            buffer_codigo.append(linha)
            i += 1
            continue

        if not linha.strip() or RE_SEPARADOR.match(linha):
            i += 1
            continue

        if linha_de_tabela(linha):
            bloco = []
            while i < len(linhas) and linha_de_tabela(linhas[i]):
                if not eh_separador_de_tabela(linhas[i]):
                    bloco.append(linhas[i])
                i += 1
            if bloco:
                inserir_tabela(doc, bloco)
            continue

        m = RE_IMAGEM.match(linha.strip())
        if m:
            inserir_imagem(doc, m.group("src"), m.group("alt"), base)
            i += 1
            continue

        m = RE_TITULO.match(linha)
        if m:
            doc.add_heading(m.group("texto"), level=min(len(m.group("nivel")), 4))
            i += 1
            continue

        m = RE_LISTA_NUM.match(linha)
        if m:
            texto, i = juntar_continuacao(linhas, i + 1, m.group("texto"))
            escrever_inline(doc.add_paragraph(style="List Number"), texto)
            continue

        m = RE_LISTA_MARC.match(linha)
        if m:
            texto, i = juntar_continuacao(linhas, i + 1, m.group("texto"))
            escrever_inline(doc.add_paragraph(style="List Bullet"), texto)
            continue

        if linha.lstrip().startswith(">"):
            # Uma citacao pode ocupar varias linhas e ate varios paragrafos
            # (separados por uma linha ">" vazia). Junta cada paragrafo antes
            # de formatar, pela mesma razao de juntar_continuacao.
            paragrafos, atual = [], []
            while i < len(linhas) and linhas[i].lstrip().startswith(">"):
                conteudo = linhas[i].lstrip().lstrip(">").strip()
                if conteudo:
                    atual.append(conteudo)
                elif atual:
                    paragrafos.append(" ".join(atual))
                    atual = []
                i += 1
            if atual:
                paragrafos.append(" ".join(atual))
            for texto in paragrafos:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(1)
                escrever_inline(p, texto, italico=True)
            continue

        # Paragrafo: junta linhas ate a proxima linha em branco ou marcador de bloco.
        texto, i = juntar_continuacao(linhas, i + 1, linha.strip())
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        escrever_inline(p, texto)

    saida = os.path.splitext(caminho_md)[0] + ".docx"
    doc.save(saida)
    return saida


def main():
    alvos = sys.argv[1:]
    if not alvos:
        if not os.path.isdir(RELATORIOS):
            print("ERRO: " + RELATORIOS + " nao existe.")
            return 1
        alvos = sorted(os.path.join(RELATORIOS, f) for f in os.listdir(RELATORIOS)
                       if f.lower().endswith(".md"))
    if not alvos:
        print("Nenhum .md encontrado em relatorios/.")
        return 1
    for md in alvos:
        if not os.path.isfile(md):
            print("ERRO: nao encontrado -> " + md)
            return 1
        saida = converter(md)
        kb = os.path.getsize(saida) / 1024
        print("-> " + os.path.relpath(saida, RAIZ) + "  ({:.0f} KB)".format(kb))
    return 0


if __name__ == "__main__":
    sys.exit(main())
