# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este diretório

Pacote de dados e documentos de uma **pesquisa** — não é uma base de código. Não há código-fonte, build, lint, testes nem git. O objetivo é produzir um experimento e um paper curto sobre detecção explicável de inconsistências cadastrais/documentais em análise de crédito no DF/RIDE, combinando RAG, tipificação simbólica e inferência bayesiana.

O idioma de trabalho do projeto é **português do Brasil**. Documentos, nomes de colunas e saídas devem seguir esse idioma.

Quando código for escrito, ele ainda não tem lugar definido — proponha a estrutura antes de criar diretórios.

## Ambiente

- Windows 11, **PowerShell** é o shell primário (a ferramenta Bash existe mas `ls`/`head` não estão disponíveis nela).
- Python disponível com `pypdf`, `pymupdf` (`fitz`) e `pdfplumber`.
- **`openpyxl` e `pandas` NÃO estão instalados.** Para ler o `.xlsx`, use `zipfile` + `xml.etree.ElementTree` sobre `xl/workbook.xml`, `xl/sharedStrings.xml` e `xl/worksheets/sheetN.xml`, ou instale a dependência antes.
- Não há repositório git. Não assuma versionamento.

## Comandos úteis

Reproduzir o experimento inteiro do zero (determinístico por semente; ~8 min):

```bash
python experimento/varredura.py && python experimento/equidade.py && python experimento/figuras.py
```

`varredura.py` imprime o veredito dos critérios de aceitação e escreve `resultados/`.
`equidade.py` testa o critério de equidade na grade completa de β × π.
`figuras.py` lê `resultados/` e escreve `figuras/`.

Regerar o dataset de casos com rótulo latente:

```bash
python experimento/exportar_dataset.py 5000
```

Não existem comandos de build/lint/test. Os demais comandos recorrentes são de leitura:

Extrair o texto da proposta (8 páginas) para o scratchpad:

```bash
python -c "import fitz; d=fitz.open(r'C:\Pesquisa_RAG\Proposta_PIDTI_RAG_Bayesiano2.pdf'); print('\n'.join(p.get_text() for p in d))"
```

Carregar o dataset (atenção ao delimitador e ao BOM):

```bash
python -c "import csv; rows=list(csv.DictReader(open(r'C:\Pesquisa_RAG\dataset_sintetico_500_casos.csv',encoding='utf-8-sig'),delimiter=';')); print(len(rows), rows[0])"
```

## Convenções de dados

- CSVs usam **`;` como delimitador** e **UTF-8 com BOM** — abra com `encoding='utf-8-sig'`, senão a primeira chave vem como `\ufeffcase_id`.
- Decimais com **ponto**, sem separador de milhar.
- Todos os identificadores (`SYN-CNPJ-*`, razões sociais, endereços, valores) são **sintéticos**. O README declara explicitamente que nada aqui pode ser usado para concessão, negação ou decisão real de crédito.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `Proposta_PIDTI_RAG_Bayesiano2.pdf` | Proposta PIDTI completa: hipóteses H1–H3, arquitetura em 4 camadas, cronograma, referências |
| `dataset_sintetico_500_casos.csv` | 500 casos controlados, ver semântica abaixo |
| `fontes_oficiais.csv` | 7 fontes oficiais (Receita Federal, Geoportal/SEDUH, BCB/SCR) com URL e uso pretendido |
| `base_paper_rag_bayesiano.xlsx` | 4 abas: `Fontes Oficiais`, `Dataset Sintetico` (espelho do CSV), `Schema` (dicionário de campos), `Experimento` (as 7 etapas do desenho experimental) |
| `README.md` | Escopo sugerido do short paper e restrições de uso |
| `dataset_sintetico_v2.csv` | **Use este.** 5.000 casos com `fraude_latente` separada das evidências — `OR(evidencias) != fraude_latente` em 41,5% das linhas. Gerado por `experimento/exportar_dataset.py` |
| `Resumo Congresso IC UnB - Modelo Preditivo.md` | Resumo de IC anterior (projeto de dengue). **É o modelo de formato e de registro** para qualquer resumo novo |
| `Resumo Congresso IC UnB - RAG Bayesiano.md` | Resumo desta pesquisa |

## Experimento

`experimento/` — `gerador.py` (mecanismo causal), `bracos.py` (as seis abordagens),
`metricas.py`, `varredura.py`, `equidade.py`, `figuras.py`, `exportar_dataset.py`.
Saídas em `resultados/` e `figuras/`, ambas fora do versionamento por serem regeneráveis.

Dependências: apenas `numpy` e `matplotlib`. **Não instalar** scipy, sklearn, PyMC, SDV nem
geradores baseados em GAN — nenhum é necessário, e um gerador ajustado destruiria a
verificabilidade da calibração, que depende de conhecer os parâmetros verdadeiros.

### Achados verificados (não reabrir sem novo experimento)

- A variante bayesiana sem território **não supera** a tabela empírica: diferença mediana de
  0,059 p.p. na precisão sob orçamento.
- Condicionar o **prior** à taxa observada da região é dominado em **224/224** configurações
  (Brier e ECE piores) — a mesma evidência é contada duas vezes.
- Com taxa de fraude **idêntica por construção**, a discriminação territorial emerge sozinha:
  correlação −0,997 entre cobertura cadastral e falsos positivos, em **48/48** configurações.
- **Reprovado e removido do resumo:** mover o território para a verossimilhança *não* corrige
  a inequidade de forma robusta (inverte o sinal em apenas 33/48).

## Semântica do dataset

Cada linha pareia um campo **declarado** com um campo de **referência** (endereço, situação cadastral, valor). As colunas `evidencia_*` marcam divergência detectável; `tipo_cenario` estratifica o experimento (`consistente` 204, `territorial` 74, `multiplas` 67, `valor` 62, `cadastral` 62, `ambiguo` 31); `regiao_administrativa` cobre 8 RAs do DF. Rótulo: 265 positivos / 235 negativos.

### Propriedade crítica — verificada, não presumida

O dataset **não discrimina** entre abordagens. Três fatos medidos sobre os 500 casos:

1. `ground_truth_inconsistencia == OR(evidencia_status, evidencia_endereco, evidencia_valor)` em **500/500 linhas**, sem exceção.
2. As flags `evidencia_*` reproduzem a comparação bruta dos campos em 469/500. As 31 exceções são exatamente os casos `tipo_cenario == 'ambiguo'`.
3. Nos casos `ambiguo`, `|valor_declarado − valor_referencia|` fica entre **R$ 0,01 e R$ 1,94**. Nos casos com `evidencia_valor == 1`, fica entre **R$ 156,74 e R$ 10.519,61**. Separação de duas ordens de grandeza.

**Consequência:** a regra `endereço≠ OR status≠ OR |Δvalor| > 2` atinge F1 = 1,000 e Brier = 0,000. O braço "regras simples" satura, e o *ablation study* previsto na aba `Experimento` não consegue mostrar ganho algum de RAG ou de Bayes. **Não reporte métricas de comparação sobre este arquivo sem antes regerá-lo.** Reproduza o achado com:

```bash
python -c "import csv; rows=list(csv.DictReader(open(r'C:\Pesquisa_RAG\dataset_sintetico_500_casos.csv',encoding='utf-8-sig'),delimiter=';')); print(sum(1 for r in rows if int(int(r['evidencia_status'])+int(r['evidencia_endereco'])+int(r['evidencia_valor'])>0)!=int(r['ground_truth_inconsistencia'])), 'divergencias em', len(rows))"
```

## Decisões metodológicas vigentes

Estas foram fixadas em revisão crítica e substituem partes do PDF e da aba `Experimento`. Não são deriváveis dos arquivos.

- **Evento H = fraude latente, não observável.** As inconsistências documentais são *sinais ruidosos* de H, não o próprio H. A coluna `ground_truth_inconsistencia` rotula o sinal observável, não o alvo. A decisão do sistema é **triagem para revisão humana** (*selective prediction*), nunca concessão ou negação.
- **Métrica principal:** Brier, ECE e **precisão@top-k sob orçamento de analista** — não F1 isolado.
- **Baseline honesto:** Fellegi-Sunter / Splink (log-razão de verossimilhança por campo), não "regras simples". É bayesiano e explicável por contribuição de campo, então é o adversário real do motor proposto.
- **Região Administrativa entra na verossimilhança, não no prior.** Condicionar `P(F)` em RA é redlining algorítmico e contradiz H2. O uso correto é `P(E | ¬F, RA=r)`: onde o cadastro territorial tem cobertura baixa, a especificidade da fonte cai, a razão de verossimilhança cai, e a mesma evidência atualiza *menos* a suspeita. Isso reconcilia H2 e H3.
- **Dataset precisa ser regerado** com rótulo latente F separado das evidências observáveis, com sensibilidade/especificidade controladas por tipo de evidência e por RA.
- **Trabalho anterior a considerar antes de reivindicar ineditismo:** BayesRAG (arXiv 2601.07329), Bayesian RAG para QA financeiro (PMC12886353), propagação bayesiana de incerteza em RAG agêntico (arXiv 2607.00972), Srivastava & Shafer (funções de crença para agregação de evidência de auditoria, 1995), Fellegi-Sunter (1969) e ALICE/SOFIA/ADELE (CGU/TCU).
