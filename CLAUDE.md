# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este diretório

Pesquisa de Iniciação Científica sobre triagem explicável de inconsistências cadastrais e
documentais em análise de crédito no DF/RIDE, combinando recuperação de evidências (RAG),
tipificação simbólica e inferência bayesiana. O repositório reúne a proposta PIDTI, os dados
sintéticos, o experimento de simulação e os resumos submetidos.

O idioma de trabalho é **português do Brasil** — documentos, nomes de colunas, rótulos de
figura e mensagens de commit.

## Ambiente

- Windows 11. **PowerShell é o shell para rodar Python.**
- A ferramenta **Bash tem o PATH quebrado**: só enxerga `git`. Prefixe todo comando com
  `export PATH="/usr/bin:/bin:$PATH"` para ter `cat`, `grep`, `sed`, `ls`. Mesmo assim
  **`python` não fica acessível pelo Bash** — use PowerShell para executar scripts.
- Instalado: `numpy` 2.5.0, `matplotlib` 3.11.0, `pandas` 3.0.3, `pymupdf` (`fitz`) 1.27,
  `pypdf` 6.13, `pdfplumber` 0.11.
- **Ausentes:** `openpyxl`, `scipy`, `sklearn`, `pymc`, `faker`. Para ler o `.xlsx` sem
  openpyxl, use `zipfile` + `xml.etree.ElementTree` sobre `xl/workbook.xml`,
  `xl/sharedStrings.xml` e `xl/worksheets/sheetN.xml`.
- Repositório git inicializado, branch `main`. `resultados/` e `figuras/` são ignorados por
  serem regeneráveis; `*.csv` tem `-text` no `.gitattributes` para preservar BOM e CRLF.

## Comandos

Reproduzir o experimento inteiro (determinístico por semente; ~8 min):

```bash
python experimento/varredura.py && python experimento/equidade.py && python experimento/figuras.py
```

`varredura.py` varre 224 configurações × 8 sementes × 40.000 casos, imprime o veredito dos
critérios de aceitação e escreve `resultados/`. `equidade.py` testa o critério de equidade na
grade completa de β × π. `figuras.py` lê `resultados/` e escreve `figuras/`.

Regerar o dataset de casos com rótulo latente:

```bash
python experimento/exportar_dataset.py 5000
```

Não há build, lint nem suíte de testes. A verificação é a reexecução: rodar duas vezes e
comparar os CSVs, que devem ser idênticos.

Extrair o texto da proposta (8 páginas):

```bash
python -c "import fitz; d=fitz.open(r'C:\Pesquisa_RAG\Proposta_PIDTI_RAG_Bayesiano2.pdf'); print(chr(10).join(p.get_text() for p in d))"
```

## Convenções de dados

- CSVs usam **`;` como delimitador** e **UTF-8 com BOM** — abra com `encoding='utf-8-sig'`,
  senão a primeira chave vem como `\ufeffcase_id`.
- Decimais com **ponto**, sem separador de milhar.
- Todos os identificadores são **sintéticos**. O `README.md` proíbe explicitamente o uso para
  qualquer decisão real de crédito.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `dataset_sintetico_v2.csv` | **Dataset em uso.** 5.000 casos, `fraude_latente` separada das evidências observáveis — divergem em 41,5% das linhas |
| `dataset_sintetico_500_casos.csv` | **Legado, defeituoso.** Ver "Dataset legado" abaixo. Não usar para comparar abordagens |
| `Proposta_PIDTI_RAG_Bayesiano2.pdf` | Proposta PIDTI: hipóteses H1–H3, arquitetura em 4 camadas, cronograma, referências |
| `fontes_oficiais.csv` | 7 fontes oficiais (Receita Federal, Geoportal/SEDUH, BCB/SCR) com URL e uso pretendido |
| `base_paper_rag_bayesiano.xlsx` | 4 abas: `Fontes Oficiais`, `Dataset Sintetico`, `Schema`, `Experimento` (desenho original em 7 etapas, parcialmente superado) |
| `Resumo Congresso IC UnB - Modelo Preditivo.md` | Resumo de IC anterior (projeto de dengue). **É o modelo de formato e de registro** para qualquer resumo novo |
| `Resumo Congresso IC UnB - RAG Bayesiano.md` | Resumo desta pesquisa |
| `README.md` | Escopo do short paper e restrições de uso |

## Experimento

`experimento/` — `gerador.py` (mecanismo causal), `bracos.py` (as seis abordagens),
`metricas.py` (Brier, ECE, precisão@top-k, FPR por RA), `varredura.py`, `equidade.py`,
`figuras.py`, `exportar_dataset.py`.

**Dependências: apenas `numpy` e `matplotlib`.** Não instalar scipy, sklearn, PyMC, SDV nem
geradores baseados em GAN. Nenhum é necessário, e um gerador *ajustado a dados* destruiria a
verificabilidade da calibração, que depende de conhecer os parâmetros verdadeiros que geraram
os dados.

O gerador especifica um processo causal explícito: fraude latente `F` com probabilidade
**idêntica em todas as RAs** (é o controle do experimento), três evidências ruidosas geradas a
partir de `F`, e a taxa de falso-positivo da evidência de *endereço* crescendo onde a cobertura
do cadastro territorial é baixa. Como a taxa de fraude é igual por construção, **qualquer
disparidade territorial nos resultados é artefato da qualidade da fonte, nunca da população.**

Seis braços: `RULE_OR` (binária), `RULE_CNT` (contagem), `LOOKUP` (tabela empírica — teto não
paramétrico sem território), `A` (Fellegi-Sunter, RA ignorada), `B` (RA na verossimilhança),
`C` (RA no prior).

## Achados verificados

Não reabrir sem novo experimento. Todos saem de `resultados/`.

- A variante bayesiana sem território **não supera** a tabela empírica: diferença mediana de
  **0,059 p.p.** na precisão sob orçamento, máximo 0,297 p.p.
- Condicionar o **prior** à taxa observada da região é dominado em **224/224** configurações,
  em Brier *e* em ECE (0,0025 → 0,2255 na referência). O mecanismo é dupla contagem: a taxa
  observada da região é produzida pelas mesmas evidências que depois entram na verossimilhança.
- Com taxa de fraude idêntica por construção e **nenhuma variável demográfica no modelo**, a
  discriminação territorial emerge sozinha: correlação **−0,997** entre cobertura cadastral e
  falsos positivos entre inocentes, em **48/48** configurações.
- Mover a RA para a verossimilhança (`B`) melhora a acurácia de forma **modesta**: mediana
  **+0,64 p.p.**, máximo +2,96.
- **Reprovado pelo critério pré-registrado:** `B` *não* corrige a inequidade de forma robusta —
  inverte o sinal da correlação em apenas **33/48** configurações, falhando sob ruído baixo e
  gradiente territorial íngreme, e sua amplitude de disparidade (0,054) é **o triplo** da de
  `A` (0,017). O achado foi removido do resumo.

## Decisões metodológicas vigentes

Fixadas em revisão crítica e por experimento. Substituem partes do PDF e da aba `Experimento`,
e não são deriváveis dos arquivos.

- **Evento H = fraude latente, não observável.** As inconsistências documentais são *sinais
  ruidosos* de H, não o próprio H. A decisão do sistema é **triagem para revisão humana**
  (*selective prediction*), nunca concessão ou negação de crédito.
- **Métrica principal:** Brier, ECE e **precisão@top-k sob orçamento de analista** — não F1.
- **Baseline honesto:** Fellegi-Sunter / Splink (log-razão de verossimilhança por campo).
  Comparar apenas contra "regras simples" é comparar contra um adversário fraco.
- **Região Administrativa nunca entra no prior.** Está verificado que isso degrada calibração
  e amplifica a disparidade territorial. Não é apenas eticamente problemático: é
  estatisticamente incorreto.
- **A verossimilhança tampouco resolve a equidade.** A hipótese de que `P(E | ¬F, RA=r)`
  reconciliaria H2 e H3 foi testada e **reprovada**. `B` pode ser usado para ganho de acurácia,
  desde que a ressalva de robustez seja declarada — mas não deve ser apresentado como solução
  de equidade.
- **Conclusão que orienta as próximas fases:** não existe correção, no nível da agregação de
  evidências, para a desigualdade produzida por qualidade desigual de dado. Enquanto a cobertura
  cadastral variar entre RAs, qualquer sistema que use endereço como evidência penalizará quem
  mora onde o registro é pior — inclusive os construídos para serem neutros. Medir e publicar a
  cobertura cadastral por RA é requisito de governança, não detalhe técnico.
- **Pendência prioritária:** o vetor `COBERTURA` em `gerador.py` é **estipulado, não medido**.
  Obter o dado real no Geoportal/SEDUH é o maior ganho por esforço disponível, e o resumo
  declara essa limitação explicitamente.
- **Trabalho anterior a considerar antes de reivindicar ineditismo:** BayesRAG (arXiv
  2601.07329), Bayesian RAG para QA financeiro (PMC12886353), propagação bayesiana de incerteza
  em RAG agêntico (arXiv 2607.00972), Srivastava & Shafer (funções de crença para agregação de
  evidência de auditoria, 1995), Fellegi-Sunter (1969), ALICE/SOFIA/ADELE (CGU/TCU) e SynthFin
  (gerador de fraude transacional brasileira; licença non-commercial, não adotar).

## Dataset legado — por que `dataset_sintetico_500_casos.csv` não serve

Três fatos medidos sobre os 500 casos:

1. `ground_truth_inconsistencia == OR(evidencia_status, evidencia_endereco, evidencia_valor)`
   em **500/500 linhas**, sem exceção.
2. As flags `evidencia_*` reproduzem a comparação bruta dos campos em 469/500. As 31 exceções
   são exatamente os casos `tipo_cenario == 'ambiguo'`.
3. Nos casos `ambiguo`, `|valor_declarado − valor_referencia|` fica entre **R$ 0,01 e R$ 1,94**;
   nos casos com `evidencia_valor == 1`, entre **R$ 156,74 e R$ 10.519,61**. Duas ordens de
   grandeza de separação.

**Consequência:** a regra `endereço≠ OR status≠ OR |Δvalor| > 2` atinge F1 = 1,000 e
Brier = 0,000. O braço de regras satura e nenhum ganho de RAG ou de Bayes é mensurável.

O substituto (`dataset_sintetico_v2.csv`) tem 41,5% de divergência entre `OR(evidencias)` e
`fraude_latente`. Ao regerar qualquer dataset, confirme que essa fração é substancial — se der
0%, o gerador novo repetiu o defeito do antigo:

```bash
python -c "import csv; r=list(csv.DictReader(open(r'C:\Pesquisa_RAG\dataset_sintetico_v2.csv',encoding='utf-8-sig'),delimiter=';')); n=sum(1 for x in r if (int(x['evidencia_status'])+int(x['evidencia_endereco'])+int(x['evidencia_valor'])>0)!=int(x['fraude_latente'])); print(n,'divergencias em',len(r))"
```
