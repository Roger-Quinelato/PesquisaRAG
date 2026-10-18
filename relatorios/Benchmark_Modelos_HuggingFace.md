# Levantamento de modelos no Hugging Face para a fase RAG

**Pergunta:** quais modelos abertos vale a pena testar em cada papel do framework RAG-Bayesiano, e
em que ordem?

**Data da consulta ao Hub:** 18 de outubro de 2026, via conector do Hugging Face. Downloads,
curtidas e licenças são os que o Hub exibia nesse dia e mudam com o tempo.

**O que este documento é e o que não é.** É um **levantamento com triagem**. Os modelos foram
filtrados por licença, porte e suporte a português. Para embeddings, foram ordenados por um
benchmark de terceiros, nativo em português brasileiro (MTEB-BR). **Nenhum modelo foi executado
nesta etapa.** O ambiente de trabalho não baixa pesos do Hub. Para LLM, reranker, extração e OCR
não existe hoje um benchmark público em pt-BR que cubra os modelos atuais. Nesses papéis, a lista
diz *o que testar*, e a ordem final sai do protocolo da §9, rodado localmente.

---

## 1. Onde entram modelos — e onde não entram

A proposta PIDTI (§6.2–6.4) fixa quatro camadas e uma restrição forte: **somente código aberto e
processamento 100% offline em servidor local via Ollama**, para que nenhum dado de cidadão saia da
máquina (LGPD, sigilo bancário). Cada camada pede um tipo diferente de modelo, ou nenhum:

| Papel | Camada da proposta | Épico (Trello / Jira) | Prazo do épico | Tipo de modelo |
|---|---|---|---|---|
| Recuperação semântica (índice FAISS) | Evidência (RAG) | D5 / RAGB-5 | 26/03/2027 | Embedding de texto |
| Reordenar os trechos recuperados | Evidência (RAG) | D5 / RAGB-5 | 26/03/2027 | Reranker (*cross-encoder*) |
| Converter trecho em evidência tipificada | Tipificação (FOL) | D5–D7 / RAGB-5, RAGB-7 | 26/03 – 18/06/2027 | Extrator de entidades **ou** LLM com saída JSON |
| Redigir o relatório explicável | Decisória (XAI) | D6, D9 / RAGB-6, RAGB-9 | 02/04 – 30/07/2027 | LLM local (Ollama) |
| Checar se o relatório é sustentado pelas evidências | Decisória (XAI) | D9 / RAGB-9 | 30/07/2027 | NLI / detector de alucinação |
| Ler documento digitalizado (se o corpus tiver) | Evidência (RAG) | D5 / RAGB-5 | 26/03/2027 | OCR / *document parsing* |
| Atualização da probabilidade de suspeita | Probabilística (Bayes) | D7 / RAGB-7 | 18/06/2027 | **Nenhum.** numpy / PyMC |
| Gerador de dados sintéticos | — | D3 / RAGB-3 | 27/11/2026 | **Nenhum.** Mecanismo causal em numpy |

As duas últimas linhas importam. O motor bayesiano e o gerador **não devem receber modelo do Hub**.
O `CLAUDE.md` já registra que um gerador ajustado a dados destruiria a verificabilidade da
calibração. E o LLM do relatório **não calcula probabilidade nenhuma**: ele só verbaliza os números
que o motor produziu. Isso vira critério de teste na §9.

Os épicos com prazo mais próximo (D2 em 30/10/2026, D3 em 27/11/2026, D4 em 18/12/2026) não
dependem de nenhum modelo daqui. Este levantamento alimenta a D5. No Relatório Parcial 1 (D4), ele
pode entrar como planejamento da fase RAG.

---

## 2. Critérios de corte (eliminatórios)

1. **Licença aprovada pela OSI** (Apache-2.0 ou MIT). A proposta afirma uso *exclusivamente open
   source*. Licença com restrição de uso, não comercial ou "comunitária" elimina o modelo.
2. **Pesos abertos sem portão** (*gated*). Se o download exige aceitar termos, a licença
   normalmente não é OSI.
3. **Roda em hardware local de IC.** Três faixas: só CPU; GPU de 8 GB; GPU de 16–24 GB. Para LLM,
   é preciso haver GGUF publicado, que é o formato que o Ollama consome.
4. **Português declarado no cartão do modelo, ou medido em benchmark pt-BR.**

### Eliminados, com o motivo

| Modelo | Motivo |
|---|---|
| `meta-llama/Llama-3.1-8B-Instruct` e família Llama 3.x | Licença `llama3.1` e download com portão: não é OSI. **A proposta cita "Llama-3/Mistral".** É a mesma incompatibilidade já apontada para o SDV, e o texto precisa ser corrigido |
| `maritaca-ai/sabia-7b` | Derivado do Llama 2, licença Llama 2 |
| `PORTULAN/gervasio-8b-portuguese-ptpt-decoder` | O cartão declara MIT, mas o modelo é ajuste fino de `Llama-3.1-8B-Instruct`, e os termos da Llama continuam valendo. É também português europeu. **Exemplo de que o metadado de licença do Hub não basta: confira a base do modelo** |
| `jinaai/jina-embeddings-v3`, `jina-embeddings-v5-text-small`, `jina-reranker-v3` | CC-BY-NC-4.0 (não comercial). O v5-small é forte no MTEB-BR, mas o registro de software visa transferência ao GDF |
| `tencent/KaLM-Embedding-Gemma3-12B-2511` | Licença `other`, e 11,8 B parâmetros só para embedding |
| `google/embeddinggemma-300m` | Licença Gemma (não OSI). Ironia: é o melhor modelo pequeno do MTEB-BR. A **sucessora `embeddinggemma-2` é Apache-2.0** e entra na lista para medir |
| `allenai/Olmo-3-7B-Instruct` | Excelente em abertura (dados e código abertos), mas o cartão declara só inglês |
| `vectara/hallucination_evaluation_model` (HHEM 2.1), `ibm-granite/granitelib-guardian-r1.0` | Só inglês |

---

## 3. Embeddings — o único papel com benchmark pt-BR atual

**Fonte:** MTEB-BR (`MTEB-BR/mteb-pt-results`, arXiv 2607.04581, CC-BY-4.0). São 93 modelos
avaliados em 22 tarefas **nativas** em português brasileiro. Corpora traduzidos por máquina, como o
mMARCO, ficam de fora por construção. Uma das tarefas, **FaqBacen**, é de perguntas ao Banco
Central: o domínio mais próximo do desta pesquisa entre os benchmarks públicos.

**A média geral (`mean_22`) não é a métrica certa para RAG.** Ela mistura classificação de discurso
de ódio, clustering e similaridade. Abaixo, `rec_6` é a média das **6 tarefas de recuperação**
(MedPT, FaQuAD, Quati, FaqBacen, JurisTCU, BRTaxQA) e `rr_2` a média das **2 de reranking**. Elas
reordenam a lista: o BidirLM-1.7B cai, e o snowflake-arctic sobe.

Tabela completa, com as 8 tarefas por modelo: [`tabelas/mteb_br_embeddings_candidatos.csv`](tabelas/mteb_br_embeddings_candidatos.csv)
(`rec_6` e `rr_2` são as colunas `media_recuperacao_6` e `media_reranking_2`).

| Modelo | Parâm. | Licença | `rec_6` | `rr_2` | FaqBacen | `mean_22` | Situação |
|---|---|---|---|---|---|---|---|
| *gemini-embedding-001 (referência fechada)* | — | comercial | *0,686* | *0,605* | *0,753* | *0,682* | teto de API paga |
| `Qwen/Qwen3-Embedding-8B` | 7,6 B | Apache-2.0 | **0,676** | 0,595 | 0,705 | 0,670 | ✅ melhor aberto |
| `Octen/Octen-Embedding-8B` | 7,6 B | Apache-2.0 | 0,668 | 0,589 | 0,717 | 0,667 | ✅ (ajuste do Qwen3-8B) |
| `tencent/KaLM-Embedding-Gemma3-12B-2511` | 11,8 B | other | 0,657 | 0,579 | 0,730 | 0,670 | ❌ licença |
| `google/embeddinggemma-300m` | 308 M | gemma | 0,654 | 0,536 | 0,695 | 0,649 | ❌ licença |
| `Qwen/Qwen3-Embedding-4B` | 4,0 B | Apache-2.0 | 0,647 | 0,576 | 0,655 | 0,662 | ✅ GGUF oficial |
| `jinaai/jina-embeddings-v5-text-small` | 596 M | CC-BY-NC | 0,641 | 0,591 | 0,687 | 0,644 | ❌ licença |
| `Snowflake/snowflake-arctic-embed-l-v2.0` | 568 M | Apache-2.0 | **0,636** | **0,595** | 0,699 | 0,620 | ✅ melhor < 1 B |
| `BAAI/bge-m3` | 568 M | MIT | **0,635** | 0,576 | 0,672 | 0,616 | ✅ denso + esparso |
| `microsoft/harrier-oss-v1-0.6b` | 596 M | MIT | 0,620 | 0,569 | 0,651 | 0,634 | ✅ |
| `BidirLM/BidirLM-1.7B-Embedding` | 1,7 B | Apache-2.0 | 0,608 | 0,556 | 0,673 | 0,651 | ✅ (cai fora da média geral) |
| `ibm-granite/granite-embedding-311m-multilingual-r2` | 312 M | Apache-2.0 | 0,607 | 0,557 | 0,681 | 0,590 | ✅ mais leve |
| `Qwen/Qwen3-Embedding-0.6B` | 596 M | Apache-2.0 | 0,604 | 0,547 | 0,632 | 0,623 | ✅ |
| `intfloat/multilingual-e5-large-instruct` | 560 M | MIT | 0,599 | 0,576 | 0,692 | 0,641 | ✅ |
| `intfloat/multilingual-e5-large` | 560 M | MIT | 0,575 | 0,549 | 0,651 | 0,591 | ✅ |
| `PORTULAN/serafim-100m-portuguese-pt-sentence-encoder-ir` | 100 M | MIT | 0,519 | 0,487 | 0,581 | 0,569 | ✅ nativo PT, fraco aqui |
| `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | 278 M | Apache-2.0 | 0,420 | 0,442 | 0,464 | 0,528 | ⚠️ evitar |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 118 M | Apache-2.0 | **0,023** | 0,168 | 0,020 | 0,248 | ⛔ não usar |

### O que a tabela diz

- **Com GPU, o melhor aberto fica a 1 p.p. da API paga.** `Qwen3-Embedding-8B` tem `rec_6` = 0,676
  contra 0,686 do Gemini. O motivo de soberania de dados da proposta não custa quase nada em
  qualidade de recuperação.
- **Só com CPU, `snowflake-arctic-embed-l-v2.0` e `bge-m3` empatam** (0,636 contra 0,635).
  A diferença está abaixo de qualquer intervalo de confiança razoável. O desempate é funcional:
  o `bge-m3` produz vetor denso, esparso e multivetorial na mesma passada. Isso dá **busca híbrida**
  (semântica + lexical) sem um segundo modelo, o que ajuda com CPF, CEP, número de processo e nome
  de RA, onde a correspondência exata pesa.
- **O modelo mais baixado não serve.** `paraphrase-multilingual-MiniLM-L12-v2` tem 652 milhões de
  downloads e é o primeiro resultado de qualquer busca por embedding em português. Ele tira 0,023
  em recuperação, praticamente acaso. O valor é tão baixo que pode ter um artefato de avaliação
  (o modelo trunca em 128 tokens). Mas o `mpnet` da mesma família, com outro limite, também fica
  em 0,42. **Escolher pelo tutorial seria o erro mais caro desta camada.**
- **"Nativo em português" não é vantagem por si.** O `serafim-100m-…-ir` (PORTULAN) perde para
  modelos multilíngues do mesmo porte.
- **`embeddinggemma-2`** (Apache-2.0, 744 M, publicado em set/2026) ainda não está no MTEB-BR.
  A antecessora, de licença restritiva, era a melhor pequena da tabela. Medir.

### Baseline lexical obrigatório

**BM25** (sem modelo) entra como braço de controle. É a mesma lógica do `baselines_e_metricas.md`:
comparar recuperação densa só contra outro modelo denso é comparar contra adversário escolhido.
Em consultas com identificadores exatos, o BM25 costuma ganhar.

---

## 4. Rerankers

Os rerankings do MTEB-BR avaliam *modelos de embedding* fazendo reranking, não *cross-encoders*.
Não há tabela pt-BR para estes; a ordem sai da §9.

| Modelo | Parâm. | Licença | Observação |
|---|---|---|---|
| `BAAI/bge-reranker-v2-m3` | 568 M | Apache-2.0 | Par natural do `bge-m3`; GGUF de terceiros disponível |
| `Qwen/Qwen3-Reranker-0.6B` | 596 M | Apache-2.0 | Par natural do `Qwen3-Embedding` |
| `Qwen/Qwen3-Reranker-4B` | 4,0 B | Apache-2.0 | Só com GPU |
| `Alibaba-NLP/gte-multilingual-reranker-base` | 306 M | Apache-2.0 | Mais leve; `pt` declarado |

Dados públicos para medir: `MTEB-BR/quati-reranking` e a tarefa JurisTCU do MTEB-BR.

**Excluído:** `jinaai/jina-reranker-v3` (CC-BY-NC).

---

## 5. LLM local (Ollama): extração estruturada e redação do relatório

**Não há benchmark pt-BR atual para LLMs.** O Open Portuguese LLM Leaderboard
(`eduagarcia/open_pt_llm_leaderboard`) foi **arquivado**: última avaliação em 01/09/2025, antes de
Qwen3.5, Gemma 4, Granite 4.2 e Ministral 3. A lista abaixo foi triada por licença, porte,
português declarado e GGUF disponível. A ordem sai do teste local.

| Modelo | Parâm. | Licença | PT | GGUF | Faixa |
|---|---|---|---|---|---|
| `mistralai/Ministral-3-3B-Instruct-2512` | ~3 B | Apache-2.0 | declarado | oficial | CPU |
| `Qwen/Qwen3.5-4B` | 4,7 B | Apache-2.0 | multilíngue | `unsloth/Qwen3.5-4B-GGUF` | CPU / 8 GB |
| `google/gemma-4-E4B-it` | 8,0 B (efetivos ~4 B) | Apache-2.0 | multilíngue | oficial (QAT q4_0) | CPU / 8 GB |
| `ibm-granite/granite-4.2-3b` / `-8b` | 3,7 / 8,8 B | Apache-2.0 | declarado | oficial | CPU / 8 GB |
| `mistralai/Ministral-3-8B-Instruct-2512` | 8,9 B | Apache-2.0 | declarado | oficial | 8 GB |
| `Qwen/Qwen3.5-9B` | 9,7 B | Apache-2.0 | multilíngue | `unsloth/Qwen3.5-9B-GGUF` | 8–12 GB |
| `google/gemma-4-12B-it` | 12,0 B | Apache-2.0 | multilíngue | oficial (QAT q4_0) | 12–16 GB |
| `openai/gpt-oss-20b` | 20,9 B (MoE) | Apache-2.0 | multilíngue | `ggml-org/gpt-oss-20b-GGUF` | 16 GB: teto local |
| `Polygl0t/Tucano2-qwen-3.7B-Instruct` | 3,8 B | Apache-2.0 | **nativo pt** | não encontrado | controle "modelo brasileiro" |

Com GPU de 24 GB, também cabem `google/gemma-4-26B-A4B-it` e `Qwen/Qwen3.6-35B-A3B` (MoE, Apache-2.0).

**Sugestão para a proposta.** Trocar "Ollama + Llama-3/Mistral" por "Ollama + modelos sob
Apache-2.0 (ex.: Ministral 3, Qwen3.5, Gemma 4)". O nome "Mistral" pode ficar: a família Ministral 3
é Apache-2.0. "Llama-3" não pode.

**O LLM tem dois papéis, com exigências diferentes:**

1. **Extração (camada FOL).** Ler o trecho recuperado e devolver JSON com as entidades que as regras
   em Python puro vão tipificar. Exige saída estruturada válida, não eloquência. Modelos de 3–4 B
   tendem a bastar, e o extrator da §6 pode substituir o LLM aqui.
2. **Relatório XAI.** Transformar a decomposição do posterior (pesos, fontes, variações) em texto
   para o gestor. O risco aqui é **o modelo alterar um número**. Um relatório que diz "a suspeita
   subiu 12%" quando o motor calculou 21% invalida a explicação, e com ela o teste de H2. Por isso
   a métrica principal desse papel é **fidelidade numérica** (§9), não fluência.

---

## 6. Extração de entidades sem LLM

A proposta pede classificação "determinística e inspecionável por especialistas". Um extrator
dedicado atende melhor que um LLM gerativo: é menor, mais rápido e não inventa campo.

| Modelo | Parâm. | Licença | Uso |
|---|---|---|---|
| `fastino/gliner2-multi-v1` | 307 M | Apache-2.0 | Extração por esquema (entidades, relações, JSON); `pt` declarado |
| `fastino/gliner2.5-multi-v1` | 287 M | Apache-2.0 | Sucessor (out/2026); multilíngue |
| `urchade/gliner_multi_pii-v1` | — | Apache-2.0 | PII: nome, documento, endereço; `pt` declarado |
| `fastino/gliner2-privacy-filter-PII-multi` | 307 M | Apache-2.0 | PII; útil para **anonimizar logs** (LGPD) |
| `OpenMed/privacy-filter-multilingual` | 1,4 B | Apache-2.0 | PII multilíngue, mais pesado |

**Baseline obrigatório: expressões regulares.** CPF, CNPJ, CEP, datas e valores monetários têm
formato fixo, com dígito verificador no caso de CPF e CNPJ. Nenhum modelo deve ser usado onde uma
regex com validação resolve. O modelo entra para o que não tem formato: nome de logradouro, nome
de órgão, tipo de documento citado em texto livre.

---

## 7. Verificação de fundamentação

Serve para a camada XAI marcar frase do relatório que **não é sustentada** por nenhuma evidência
recuperada. Liga-se ao "tratamento de baixa confiança" da D9.

| Modelo | Parâm. | Licença | Observação |
|---|---|---|---|
| `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | 279 M | MIT | NLI multilíngue com `pt`; par (evidência, frase) → implica / neutro / contradiz |
| LLM-juiz de **família diferente** do gerador | — | Apache-2.0 | Evita que o modelo julgue a própria saída |

Os detectores especializados (HHEM 2.1, Granite Guardian) são só inglês e ficam fora.

---

## 8. OCR e leitura de documentos (condicional)

Só entra se o corpus da D5 tiver documentos digitalizados. Hoje os dados são sintéticos e tabulares,
e as fontes oficiais (`fontes_oficiais.csv`) são portais e bases estruturadas. **Prioridade baixa.**

| Modelo | Parâm. | Licença | Observação |
|---|---|---|---|
| `ibm-granite/granite-docling-258M` | 258 M | Apache-2.0 | Layout, tabelas, formulários; cartão declara só `en` |
| `lightonai/LightOnOCR-3-1B` | 1,0 B | Apache-2.0 | Formulários e tabelas (out/2026) |
| `allenai/olmOCR-2-7B-1025` | 8,3 B | Apache-2.0 | Mais pesado; cartão declara só `en` |

Nenhum declara português. Testar em uma amostra de documentos reais antes de qualquer escolha.

---

## 9. Protocolo do benchmark próprio (rodar localmente, épicos D5–D6)

Os números das §3–4 são de terceiros e de outro domínio. A escolha final precisa ser medida no
corpus do projeto. Princípios, alinhados a `docs/protocolo_versionamento.md`:

**Pré-registro.** Os critérios de escolha ficam escritos antes de rodar. Proposta: *escolher o
menor modelo cuja métrica principal fique a até 1 p.p. do melhor*. O custo de rodar offline em
hardware de IC é parte do produto.

**Gold set.** São 100–200 consultas com o trecho correto rotulado à mão sobre o corpus da D5. É a
estratégia (iv) da validação da proposta, §6.3. Sanidade externa: `MTEB-BR/quati-50k` e
`MTEB-BR/quati-reranking`.

| Papel | Métrica principal | Métricas de apoio |
|---|---|---|
| Embedding | nDCG@10 | Recall@5, Recall@20, MRR; latência e RAM em CPU |
| Reranker | ganho de nDCG@10 sobre o embedding sozinho | latência por consulta |
| Extração | F1 por campo contra o gold | % de JSON válido; % de campo inventado |
| Relatório XAI | **fidelidade numérica**: todo número do texto igual ao do motor (tolerância zero) | % de evidências citadas; % de frases não sustentadas (NLI); legibilidade julgada por humanos |
| Verificador | F1 em pares (evidência, frase) rotulados | — |

**Equidade também na recuperação.** O achado central da pesquisa é que a qualidade desigual do
cadastro territorial produz disparidade. O mesmo pode acontecer **antes** do motor: se o retriever
encontra pior a evidência de endereço de RAs com cobertura baixa, a desigualdade entra pela camada
RAG. Reportar Recall@k **por RA**, com a mesma correlação contra cobertura usada em `equidade.py`.

**Reprodutibilidade.** Fixar a revisão (SHA do commit no Hub) de cada modelo, a quantização exata
(ex.: `Q4_K_M`), temperatura 0 e semente. Registrar no ledger como os demais números. Os pesos
ficam fora do git, como os datasets.

---

## 10. Lista curta: o que testar primeiro

| Papel | 1ª opção | 2ª opção | 3ª opção | Controle |
|---|---|---|---|---|
| Embedding (CPU) | `BAAI/bge-m3` | `Snowflake/snowflake-arctic-embed-l-v2.0` | `google/embeddinggemma-2` (medir) | BM25 |
| Embedding (GPU) | `Qwen/Qwen3-Embedding-4B` | `Qwen/Qwen3-Embedding-8B` | — | BM25 |
| Reranker | `BAAI/bge-reranker-v2-m3` | `Qwen/Qwen3-Reranker-0.6B` | `Alibaba-NLP/gte-multilingual-reranker-base` | sem reranker |
| Extração | `fastino/gliner2-multi-v1` | LLM 3–4 B com JSON | — | regex com validação |
| LLM do relatório | `Qwen/Qwen3.5-4B` | `google/gemma-4-E4B-it` | `mistralai/Ministral-3-8B-Instruct-2512` | template sem LLM |
| Verificador | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | LLM-juiz de outra família | — | — |
| OCR (se preciso) | `ibm-granite/granite-docling-258M` | `lightonai/LightOnOCR-3-1B` | — | — |

**Controle "template sem LLM".** A proposta já descreve o relatório XAI por *templates
estruturados*. Um template preenchido direto pelo motor tem fidelidade numérica 100% por
construção. O LLM só se justifica se ganhar em legibilidade **sem perder fidelidade**, e esse é o
ablation que testa H2 de forma honesta.

---

## 11. Limitações

- **Nenhum modelo foi executado.** Os números de embedding são do MTEB-BR (terceiro), reproduzidos
  da matriz pública sem os intervalos de confiança. Diferenças abaixo de ~1 p.p. devem ser lidas
  como empate.
- **Licença lida do metadado do Hub.** Antes de adotar um modelo, abra o arquivo `LICENSE` do
  repositório e confira o modelo-base (caso Gervásio, §2).
- **Downloads e curtidas medem popularidade, não qualidade.** O caso do
  `paraphrase-multilingual-MiniLM-L12-v2` (§3) mostra o quanto podem divergir.
- **O domínio das tarefas públicas não é o desta pesquisa.** O FaqBacen é o mais próximo, e mesmo
  assim é FAQ institucional, não documento cadastral. O gold set da §9 é insubstituível.
