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
- **Precisa instalar** para rodar `varredura.py`/`equidade.py`: `scikit-learn` (testado com
  1.9.1), usado só por `experimento/bracos_ml.py`.
- **Ausentes:** `openpyxl`, `scipy`, `pymc`, `faker`. Para ler o `.xlsx` sem
  openpyxl, use `zipfile` + `xml.etree.ElementTree` sobre `xl/workbook.xml`,
  `xl/sharedStrings.xml` e `xl/worksheets/sheetN.xml`.
- Repositório git inicializado, branch `main`. `resultados/` e `figuras/` são ignorados por
  serem regeneráveis, exceto as figuras do pôster (`figuras/poster_*.png` e
  `figuras/fig4_heatmap_beta_pi.png`), versionadas porque o README as exibe. `*.csv` tem
  `-text` no `.gitattributes` para preservar BOM e CRLF.
- Datasets, planilha, artigos em PDF, resumos de congresso, roteiro, parecer, `.claude/` e
  `.tlc/` ficam **só na máquina local** (estão no `.gitignore`). Marcados com *(local)* na
  tabela de Arquivos.

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
| `dataset_sintetico_v2.csv` *(local)* | **Dataset em uso.** 5.000 casos, `fraude_latente` separada das evidências observáveis — divergem em 41,5% das linhas. Regenerável com `exportar_dataset.py` |
| `dataset_sintetico_500_casos.csv` *(local)* | **Legado, defeituoso.** Ver "Dataset legado" abaixo. Não usar para comparar abordagens |
| `Proposta_PIDTI_RAG_Bayesiano2.pdf` | Proposta PIDTI: hipóteses H1–H3, arquitetura em 4 camadas, cronograma, referências |
| `fontes_oficiais.csv` *(local)* | 7 fontes oficiais (Receita Federal, Geoportal/SEDUH, BCB/SCR) com URL e uso pretendido |
| `base_paper_rag_bayesiano.xlsx` *(local)* | 4 abas: `Fontes Oficiais`, `Dataset Sintetico`, `Schema`, `Experimento` (desenho original em 7 etapas, parcialmente superado) |
| `Resumo Congresso IC UnB - Modelo Preditivo.md` *(local)* | Resumo de IC anterior (projeto de dengue). **É o modelo de formato e de registro** para qualquer resumo novo |
| `Resumo Congresso IC UnB - RAG Bayesiano.md` *(local)* | Resumo desta pesquisa |
| `README.md` | Apresentação da pesquisa com as figuras do pôster, reprodução e restrições de uso |

## Experimento

`experimento/` — `gerador.py` (mecanismo causal), `bracos.py` (as seis abordagens fechadas),
`bracos_ml.py` (os três braços AdaBoost), `metricas.py` (Brier, ECE, precisão@top-k, FPR por
RA), `varredura.py`, `equidade.py`, `figuras.py`, `figuras_relatorio.py`, `figuras_poster.py`,
`exportar_dataset.py`.

**Dependências:** o núcleo (`gerador.py`, `bracos.py`, `metricas.py`) usa **apenas `numpy`**.
**Exceção isolada:** `bracos_ml.py` depende de `scikit-learn`, decisão do autor para os braços
AdaBoost; nenhum outro módulo do experimento pode importá-lo. Os scripts de figura usam
`matplotlib`, `pandas` e `seaborn`. Continua proibido instalar scipy, PyMC, SDV ou geradores
baseados em GAN: um gerador *ajustado a dados* destruiria a verificabilidade da calibração, que
depende de conhecer os parâmetros verdadeiros que geraram os dados.

O gerador especifica um processo causal explícito: fraude latente `F` com probabilidade
**idêntica em todas as RAs** (é o controle do experimento), três evidências ruidosas geradas a
partir de `F`, e a taxa de falso-positivo da evidência de *endereço* crescendo onde a cobertura
do cadastro territorial é baixa. Como a taxa de fraude é igual por construção, **qualquer
disparidade territorial nos resultados é artefato da qualidade da fonte, nunca da população.**

Seis braços fechados: `RULE_OR` (binária), `RULE_CNT` (contagem), `LOOKUP` (tabela empírica —
teto não paramétrico sem território), `A` (Fellegi-Sunter, RA ignorada), `B` (RA na
verossimilhança), `C` (RA no prior).

Três braços AdaBoost (`bracos_ml.py`), que repetem o eixo "onde a RA entra": `D_ML` (RA ausente,
como A), `E_ML` (RA one-hot como feature, como B) e `F_ML` (taxa de inconsistência da RA como
feature, como C). Diferenças que precisam ser declaradas sempre que forem comparados aos seis:

- São **treinados** com split 50/50 dentro de cada configuração e avaliados **só no teste**:
  N efetivo ≈ 20.000 (coluna `n_efetivo` de `varredura.csv`), contra 40.000 dos fechados.
  `LOOKUP` é ajustado e avaliado na mesma amostra; uma vitória de `E_ML` sobre ele é "no pior
  caso para `E_ML`".
- `E_ML` recebe só a identidade da RA; `B` recebe o FPR verdadeiro do gerador (oráculo).
- `taxa_ra` de `F_ML` é estimada só no treino.
- `predict_proba` do AdaBoost fica em [0,1], mas **não é calibração**: os scores saem
  comprimidos em torno de 0,5, e o ECE deles mede sobretudo a forma do score do boosting.
- Hiperparâmetros fixos e pré-registrados (100 stumps, taxa de aprendizado 1,0), nunca ajustados.
- Os resultados dependem da versão do scikit-learn; o núcleo numpy não.
- A ordem de consumo do `rng` é fixa: os seis fechados primeiro, depois o bloco ML. Mudar essa
  ordem altera os números dos braços fechados.

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
- Mover a RA para a verossimilhança (`B`) melhora a acurácia de forma **modesta**: mediana de
  `B − LOOKUP` = **+0,673 p.p.** (mín −0,134; máx +2,956; positiva em **213/224**). O valor
  **+0,64 p.p.** que constava aqui estava errado e não se reproduz em nenhum recorte de
  `varredura.csv`. `B` é ligeiramente **pior** que `A` em calibração na referência
  (ECE 0,002672 contra 0,002456): o ganho é de ordenação, não de calibração.
- **Reprovado pelo critério pré-registrado:** `B` *não* corrige a inequidade de forma robusta.
  Distinga os dois números, que já foram confundidos: **33/48** é a contagem do critério
  pré-registrado (limiar `corr ≥ −0,10`); a inversão de sinal **estrita** (`corr ≥ 0`) ocorre em
  **30/48**, e em **11/48** a correlação de `B` permanece abaixo de −0,5. Falha sob ruído baixo
  com β íngreme e sob ruído alto com π alta. A amplitude de disparidade de `B` (0,054) é **o
  triplo** da de `A` (0,017). O achado foi removido do resumo.
- O ECE de `LOOKUP` é **zero degenerado** (~4,4e−17): a tabela empírica estima `P(F | padrão)`
  nos próprios dados em que é avaliada. Nunca citar como vantagem de calibração.

### Braços AdaBoost (D_ML, E_ML, F_ML) — primeira rodada, scikit-learn 1.9.1

Os seis braços fechados saíram **bit a bit idênticos** à rodada anterior (`varredura.csv`,
`fpr_por_ra.csv`, `equidade.csv`). Critérios declarados antes de rodar: (iv) `F_ML` pior que
`D_ML` em Brier e ECE; (v) `F_ML` com corr < −0,5 em toda a grade e `E_ML` sem corrigir a
disparidade de forma robusta; (vi) ganho de precisão de `E_ML` sobre `LOOKUP` maior que o de `B`.

- **O AdaBoost sem território replica o achado 1**: `D_ML − LOOKUP` tem mediana de **−0,066
  p.p.** (positiva em 83/224), como `A` (−0,022 p.p., 86/224). E a disparidade territorial
  emerge também nele: corr < 0 em **48/48** configurações. Os dois achados centrais não
  dependem de o modelo ser Fellegi-Sunter.
- **(vi) reprovado.** `E_ML − LOOKUP` tem mediana de **+0,067 p.p.** (positiva em 131/224),
  contra +0,673 p.p. de `B`; `E_ML` supera `B` em só **12/224**. A comparação favorece `B`
  (oráculo `f_true`, N inteiro, `LOOKUP` na própria amostra) contra `E_ML` (identidade da RA
  aprendida com 20.000 casos, avaliada fora da amostra). Não dá para dizer que o boosting é
  intrinsecamente pior; dá para dizer que ele não entrega o ganho que se esperava.
- **(v) para `F_ML` reprovado: a dupla contagem de `C` não se reproduz.** `F_ML` tem corr < −0,5
  em só **3/48** (corr +0,847 na referência) e se comporta como `E_ML`: diferença mediana de
  precisão de 0,009 p.p. e FPR por RA quase idêntico. Mecanismo: `taxa_ra` assume 8 valores
  distintos, ordenados pela cobertura, então funciona como codificação da própria RA; e um
  classificador supervisionado **aprende o peso** da feature a partir do rótulo, enquanto `C`
  soma a taxa como prior com peso fixo. A patologia de `C` é de plugar uma taxa derivada das
  evidências como prior sem estimar o peso dela, e não de usar informação territorial agregada.
- **(iv) passa (224/224), mas não pela dupla contagem.** `E_ML` também é pior que `D_ML` em
  Brier e ECE em 224/224, e `F_ML − E_ML` no ECE tem mediana de +0,0009, contra +0,29 de
  `C − A`. A piora vem de acrescentar qualquer feature territorial com metade dos dados de
  treino. Não citar (iv) como evidência de dupla contagem no AdaBoost.
- **(v) para `E_ML`: a hipótese "não corrige de forma robusta" passa.** `E_ML` atende ao limiar
  corr ≥ −0,10 em **40/48** (B: 33/48); inversão estrita de sinal em **38/48** (B: 30/48); corr
  < −0,5 em 4/48 (B: 11/48). É mais robusto que `B`, mas não em toda a grade, e a amplitude
  mediana (**0,0315**) é 1,8× a de `D_ML` (0,0180): como `B`, redistribui o custo do falso
  positivo em vez de eliminá-lo (na referência, Plano Piloto 4,70% contra Ceilândia 2,74%).
- **Nenhum braço AdaBoost é calibrado.** ECE mediano de 0,152 (`D_ML`) a 0,170 (`E_ML`/`F_ML`),
  contra 0,0023 de `A`; Brier 0,096–0,101 contra 0,069. Os scores saem comprimidos em torno de
  0,5. Para triagem que exige probabilidade interpretável, o AdaBoost precisaria de calibração
  posterior (Platt ou isotônica), o que seria um experimento novo, não feito.

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
- **Numeração das hipóteses — já foi invertida por engano, confira sempre no PDF.** No texto da
  proposta: **H2** = a explicitação em linguagem natural reduz vieses contra populações
  vulneráveis; **H3** = calibrar o *prior* com dados locais (CODEPLAN/GDF) supera modelos
  nacionais. Ou seja, **H3 é a hipótese do prior regional e é a que o experimento reprovou.**
  Ao citar pelo número, cite também o enunciado.
- **A verossimilhança tampouco resolve a equidade.** A hipótese de que `P(E | ¬F, RA=r)`
  reconciliaria H3 com H2 foi testada e **reprovada**. `B` pode ser usado para ganho de acurácia,
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
- **Trabalho anterior — verificado contra a fonte, não citar de memória.** Os identificadores
  antes marcados como suspeitos **existem**: BayesRAG (arXiv 2601.07329), Bayesian RAG para QA
  financeiro (PMC12886353), incerteza em RAG agêntico (arXiv 2607.00972), RuleRAG/SymRAG/
  NeuSym-RAG. Ver `relatorios/Relatorio_Benchmark_Estado_da_Arte.md` para o placar completo.
- **Duas alegações de ineditismo caíram na verificação. Não reivindicar:**
  - *Calibração de posterior agregado sob selective prediction é inédita* — **falso.** FinAbstain
    (arXiv 2607.24875) faz predição seletiva calibrada em domínio financeiro, com curvas
    risco–cobertura e encaminhamento explícito a revisão humana. Ver também SURE-RAG
    (2605.03534) e EvidentialRAG (2607.10491, reporta ECE).
  - *Disparidade sem atributo protegido é mecanismo novo* — **não é.** Akpinar, Lipton &
    Chouldechova, "The Impact of Differential Feature Under-reporting on Algorithmic Fairness",
    FAccT 2024 (arXiv 2401.08788), publicou o mecanismo geral. **Precisa ser citado**; a
    posição desta pesquisa é aplicação/extensão, não descoberta.
- O que sobra de específico: qualidade da fonte afetando a *especificidade* de uma evidência
  (não a presença do dado), granularidade **intramunicipal**, e taxa do evento igualada por
  construção. O achado sobre o prior tem nome conhecido — *double dipping* em Bayes empírico;
  a contribuição é mostrar que ele domina a escolha que um analista faria naturalmente (224/224).
- **Licenças:** SynthFin é Custom Non-Commercial e **SDV está sob Business Source License 1.1** —
  nenhuma das duas é open source pela OSI. A proposta PIDTI lista SDV no stack e afirma uso
  "exclusivamente open source": as duas coisas são incompatíveis e a proposta precisa ser
  corrigida. Alternativa OSI: `synthcity` (Apache 2.0). Nada disso é necessário — o gerador
  causal roda em numpy.

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
