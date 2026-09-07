# Relatório de Benchmark e Estado da Arte

**Objeto posicionado:** onde o dado territorial deve entrar em um modelo bayesiano de triagem de
inconsistências cadastrais e documentais em análise de crédito no DF/RIDE — no prior ou na
verossimilhança.

**Data da verificação:** 7 de setembro de 2026.
**Escopo do que está sendo posicionado:** a camada de agregação probabilística de evidências,
avaliada isoladamente por simulação de mecanismo. A camada de recuperação (RAG) **não foi
implementada nem avaliada** nesta etapa; ela é fase subsequente da pesquisa. A decisão do
sistema é **triagem para revisão humana** (*selective prediction*) — em nenhum ponto o sistema
concede ou nega crédito, e nenhuma afirmação deste relatório deve ser lida nesse sentido.

---

## 1. Escopo e método da revisão

### 1.1 Placar da verificação

Este relatório abre pelo placar porque a credibilidade de uma alegação de lacuna depende
inteiramente da qualidade da busca que a precedeu. Foram submetidos a verificação **39 itens**:

| Estado | Quantidade |
|---|---|
| **CONFIRMADA** — fonte aberta, identificador confere, conteúdo confere | 30 |
| **DIVERGENTE** — o trabalho existe, mas identificador, ano, título ou veículo estavam errados | 6 |
| **DESCARTADA** (não localizada / não aberta) — sai do texto | 3 |

**Descartadas, pelo nome:**

1. **Srivastava, R. P. (1995), "The belief-function approach to aggregating audit evidence",
   *International Journal of Intelligent Systems* 10(3):329–356.** Aparece em listagens de
   indexadores, mas o texto não foi aberto (Wiley respondeu HTTP 403). Não entra nas
   referências. O trabalho conjunto Srivastava & Shafer, esse sim aberto e conferido, cobre a
   mesma função argumentativa.
2. **Srivastava, R. P. (2009), "Bayesian Fraud Risk Formula for Financial Statement Audits",
   *Abacus*.** Mesma situação: listado, não aberto (Wiley 403). Descartado.
3. **Siddiqi, N., *Credit Risk Scorecards* (Wiley).** Livro real e amplamente citado como
   referência de indústria para Weight of Evidence e Information Value, mas não foi possível
   abrir o texto para conferir a atribuição específica de WoE/IV. Descartado como referência
   canônica e **substituído** por um trabalho aberto e verificável que formaliza exatamente
   essas duas quantidades (arXiv:2509.09855, item 1.4 abaixo).

### 1.2 O resultado mais importante da Fase 1

Quatro itens haviam sido registrados no `CLAUDE.md` a partir da memória de um modelo, sem
busca, e foram entregues a esta revisão com a marca **[NÃO VERIFICADO — provavelmente
inexistente]**: `BayesRAG` (arXiv 2601.07329), `Bayesian RAG` para QA financeiro
(PMC12886353), propagação bayesiana de incerteza em RAG agêntico (arXiv 2607.00972), e o
trio `RuleRAG` / `SymRAG` / `NeuSym-RAG`.

**Todos existem.** Os três identificadores numéricos abriram e correspondem exatamente ao
trabalho descrito. Isso é um resultado, e não dispensa a regra: a mesma forma de citação
plausível que aqui se confirmou é a forma que uma citação inventada assume, e o custo de
verificar foi de poucos minutos. Duas divergências reais apareceram justamente nos dois itens
que a proposta PIDTI já citava por escrito (`RuleRAG` e `SymRAG`) — ver §6.

### 1.3 Método

Cada item foi aberto na fonte primária quando possível (página `arXiv/abs`, `PMC`, repositório
GitHub e seu arquivo `LICENSE`, portal institucional oficial, API do Crossref ou do Semantic
Scholar). Buscas independentes foram feitas nos quatro eixos, e — separadamente — uma busca
dirigida por lacuna: para cada uma das quatro lacunas alegadas, procurou-se ativamente o
trabalho que a preencheria. Duas dessas buscas tiveram sucesso e reclassificaram a lacuna
(§4). Onde a fonte não abriu, o item foi descartado, não rebaixado a "provável".

---

## 2. Os quatro eixos

### Eixo 1 — Agregação probabilística de evidência

#### 1.1 Fellegi & Sunter (1969) — CONFIRMADA

*A Theory for Record Linkage*, **Journal of the American Statistical Association 64:1183–1210**,
DOI `10.1080/01621459.1969.10501049`. Volume, páginas e autoria conferidos via API do Semantic
Scholar sobre o DOI.

**O que é.** A formalização decisória do pareamento de registros. Para cada campo comparado,
define-se a razão entre a probabilidade de concordância dado que os registros são o mesmo
indivíduo (*m*) e dado que não são (*u*); o log dessa razão é o peso do campo, e os pesos
somam-se sob independência condicional para produzir um escore comparado a dois limiares, que
recortam três zonas: vínculo, não-vínculo e revisão manual.

**O que resolve.** Dá fundamento estatístico e otimalidade (sob independência condicional) a
uma prática que antes era heurística, e produz um escore aditivo cuja contribuição por campo é
inspecionável — é explicabilidade por construção, não *post hoc*.

**O que não cobre.** Não trata o caso em que a qualidade da fonte de referência varia
sistematicamente entre subpopulações; *m* e *u* são parâmetros globais do par de bases. Não
avalia calibração probabilística nem distribuição de erro entre grupos. E o evento modelado é
"estes dois registros são a mesma entidade" — um fato verificável em princípio —, não um evento
latente e não observável como fraude.

**Relação com esta pesquisa.** É o *baseline honesto* e o maquinário efetivamente usado: as três
variantes bayesianas do experimento (`A`, `B`, `C`) são Fellegi-Sunter com log-razão de
verossimilhança por campo. A variante `B` é precisamente a modificação de deixar o *u* da
evidência de endereço variar por região. Nada do aparato de agregação é novo aqui.

#### 1.2 Splink — CONFIRMADA

`https://github.com/moj-analytical-services/splink` — **licença MIT**, mantido pelo *Ministry of
Justice Analytical Services* do Reino Unido.

**O que é.** Biblioteca Python de vinculação probabilística de registros que implementa o modelo
de Fellegi-Sunter, com estimação de parâmetros por Expectation-Maximisation
(`estimate_parameters_using_expectation_maximisation`), bloqueio para escalar e ferramentas de
visualização da decomposição do escore por campo.

**O que resolve.** Torna o baseline de 1969 operacional e reprodutível em escala, sem custo de
licença, com estimação dos parâmetros a partir dos próprios dados em vez de estipulação.

**O que não cobre.** É pareamento de entidades, não triagem de suspeita: não há evento latente,
não há noção de orçamento de analista, não há métrica de equidade territorial, e não há
mecanismo para que a confiabilidade de um campo dependa da região do registro.

**Relação com esta pesquisa.** Fixa a régua: comparar contra "regras simples" seria comparar
contra adversário fraco; a régua é Fellegi-Sunter, e Splink é a prova de que ela é
implementável em produção sob licença permissiva.

#### 1.3 Srivastava & Shafer (1994) — DIVERGENTE (registrada como "~1995")

*Integrating statistical and nonstatistical audit evidence using belief functions: A case of
variable sampling*, **International Journal of Intelligent Systems 9:519–539, 1994**, DOI
`10.1002/int.4550090603`. Confirmado via Crossref e pelo manuscrito no sítio de Glenn Shafer
(`https://www.glennshafer.com/assets/downloads/articles/article51.pdf`, folha de rosto datada de
junho de 1993, autores Rajendra P. Srivastava, University of Kansas, e Glenn R. Shafer, Rutgers).

**Dado corrigido:** o ano é **1994**, não 1995; o título usa "nonstatistical" em uma palavra.

**O que é.** Aplicação de funções de crença de Dempster-Shafer à agregação de evidências de
auditoria, combinando evidência estatística (amostragem) e não estatística (controles internos,
procedimentos analíticos) sob um formalismo que distingue "evidência a favor" de "ausência de
evidência".

**O que resolve.** Endereça o desconforto de atribuir prior numérico onde não há base
frequentista, permitindo representar ignorância explicitamente em vez de forçá-la a uma
distribuição uniforme.

**O que não cobre.** Não trata território, não avalia calibração no sentido de escore próprio
(Brier/ECE) — funções de crença não são probabilidades e não admitem esse teste diretamente —,
e não trata equidade entre grupos.

**Relação com esta pesquisa.** É o caminho alternativo deliberadamente **não** tomado. A escolha
por probabilidade e não por funções de crença é o que torna a calibração testável, e a
calibração é o principal achado negativo do experimento. Registrar a alternativa é honesto:
parte do que aqui se mede não seria mensurável sob o outro formalismo.

#### 1.4 Weight of Evidence / Information Value em scorecards de crédito — CONFIRMADA

*An Information-Theoretic Framework for Credit Risk Modeling: Unifying Industry Practice with
Statistical Theory for Fair and Interpretable Scorecards*, **arXiv:2509.09855**.

**O que é.** Formalização das duas quantidades que estruturam o scorecard logístico de crédito
há décadas como prática de indústria. Prova que o Information Value é exatamente a divergência
de Jeffreys entre as distribuições de bons e maus sobre os mesmos *bins*, e portanto idêntico ao
PSI calculado entre esses dois grupos.

**O que resolve.** Dá fundamento teórico a uma prática que se transmitia por manual, e formula o
trade-off desempenho–equidade como problema de otimização: maximizar IV para poder preditivo
enquanto se minimiza IV sobre atributos protegidos, com fronteira de Pareto via programação
inteira mista e restrições probabilísticas de equidade por teste de hipótese.

**O que não cobre.** Trata equidade pela via clássica — existe um atributo protegido, e o
objetivo é reduzir a informação que o modelo extrai dele. Não trata o caso em que a disparidade
emerge sem que qualquer atributo protegido esteja no modelo. E o evento modelado é inadimplência
observada, não fraude latente.

**Relação com esta pesquisa.** O WoE é, matematicamente, a mesma log-razão de verossimilhança do
Eixo 1.1: o scorecard de crédito e o modelo de Fellegi-Sunter agregam evidência pelo mesmo
mecanismo. Isso reforça o ponto de §5: o maquinário não é a contribuição.

#### 1.5 Daniel (2021), Bayes vs. Dempster-Shafer em detecção de fraude — CONFIRMADA

*Bayesian and Dempster-Shafer models for combining multiple sources of evidence in a fraud
detection system*, Fabrice Daniel, **arXiv:2104.07440**.

**O que é.** Comparação direta dos dois formalismos para consolidar um escore de risco de fraude
a partir de múltiplas fontes de evidência, com o argumento de que Dempster-Shafer exige apenas
estimativas de posteriores e lida melhor com conflito entre fontes, enquanto Bayes exige prior e
verossimilhança.

**O que resolve.** Explicita o custo de cada escolha de formalismo no domínio de fraude, que é
exatamente o domínio desta pesquisa.

**O que não cobre.** Não há dimensão territorial, não há avaliação de calibração sob varredura de
parâmetros, não há métrica de equidade, e não há verdade-terreno controlada — a comparação é
conceitual e ilustrativa, não um experimento de recuperação de parâmetros conhecidos.

**Relação com esta pesquisa.** É o trabalho mais próximo do Eixo 1 em domínio; delimita bem o que
esta pesquisa acrescenta: a pergunta não é *qual formalismo*, é *onde entra o território*.

---

### Eixo 2 — RAG com camada probabilística ou simbólica

Os quatro identificadores suspeitos foram verificados primeiro; depois, uma busca independente
por "RAG + quantificação de incerteza / calibração / *selective prediction* / neuro-simbólico"
foi conduzida sem partir da lista herdada. A busca independente rendeu mais do que a lista, e
mudou a classificação de uma das lacunas (§4, G4).

#### 2.1 Lewis et al. (2020) — CONFIRMADA

*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, **arXiv:2005.11401**,
NeurIPS 2020. Autoria e veículo conferidos. É a referência de origem citada corretamente pela
proposta PIDTI. Estabelece a separação recuperação/geração com memória paramétrica e não
paramétrica. **Não cobre**: não há camada probabilística de agregação de evidência sobre um
evento latente, nem avaliação de calibração de um posterior.

#### 2.2 BayesRAG — CONFIRMADA (o identificado como "provavelmente inexistente" existe)

*BayesRAG: Probabilistic Mutual Evidence Corroboration for Multimodal Retrieval-Augmented
Generation*, **arXiv:2601.07329** (cs.CL, 12/jan/2026). Autores: Xuan Li, Yining Wang, Haocai
Luo, Shengping Liu, Jerry Liang, Ying Fu, Weihuang, Jun Yu, Junnan Zhu.

**O que é.** Framework multimodal que modela a consistência intrínseca entre candidatos
recuperados nas várias modalidades como evidência probabilística, para refinar a confiança da
recuperação — priorizando pares texto-imagem que se reforçam semântica e estruturalmente.

**O que resolve.** Recuperação em documentos visualmente ricos, onde o sinal de relevância
textual isolado é fraco.

**O que não cobre.** O objeto probabilístico é a **confiança da recuperação**, não a
probabilidade posterior de um evento do mundo. Não há evento latente, não há equidade, não há
território.

**Relação com esta pesquisa.** Ocupa o nome "RAG bayesiano" com um significado diferente do
usado aqui. Isso importa para o posicionamento: reivindicar "RAG bayesiano" como rótulo é
reivindicar algo já ocupado; a contribuição precisa ser enunciada pela pergunta, não pelo rótulo.

#### 2.3 Bayesian RAG para QA financeiro — CONFIRMADA (o "PMC provavelmente inexistente" existe)

*Bayesian RAG: uncertainty-aware retrieval for reliable financial question answering*, Lebede
Ngartera, Saralees Nadarajah, Rodoumta Koina, **Frontiers in Artificial Intelligence**,
27/jan/2026. **PMC12886353**, PMID 41676168.

**O que é.** Incorpora incerteza epistêmica à recuperação via Monte Carlo Dropout, produzindo
embeddings distribucionais e uma função de escore bayesiana que equilibra relevância semântica
contra incerteza.

**O que resolve.** Confiabilidade de QA sobre documentos financeiros: relatam 93,1% de acurácia,
ganhos de +20,6% em Precision@3, +22,7% em MRR e +25,4% em NDCG@10 sobre BM25, com 26,8% de
melhora em calibração de incerteza e 27,8% de redução de alucinação.

**O que não cobre.** A calibração avaliada é a da confiança do sistema de QA, não a de um
posterior sobre um evento latente do mundo agregado a partir de evidências tipificadas. Não há
recorte territorial nem avaliação de distribuição de erro entre grupos.

**Relação com esta pesquisa.** Estabelece que "RAG + Bayes em domínio financeiro" já está
publicado, em veículo indexado. Qualquer alegação de ineditismo desta pesquisa que se apoie
nessa combinação é insustentável — ver §5.

#### 2.4 Propagação bayesiana de incerteza em RAG agêntico — CONFIRMADA (o terceiro "inexistente" existe)

*Bayesian Uncertainty Propagation for Agentic RAG Pipelines: A Proof-of-Concept Study on
Multi-Hop Question Answering*, Louis Donaldson, Connor Walker, Koorosh Aslansefat, Yiannis
Papadopoulos, **arXiv:2607.00972** (cs.AI, 1/jul/2026).

**O que é.** Propaga sinais de incerteza através de redes bayesianas ao longo de um raciocínio
multi-etapa, avaliado em dois conjuntos de QA com modelos distintos.

**O que resolve.** O problema de a incerteza se perder entre estágios de um pipeline agêntico.

**O que não cobre.** É prova de conceito em QA multi-hop; não há evento latente de domínio,
métrica de utilidade sob orçamento, nem equidade.

**Relação com esta pesquisa.** Confirma que "propagar incerteza de forma bayesiana dentro de um
pipeline de recuperação" é território ocupado e ativo. A fase subsequente desta pesquisa — a
integração da camada de recuperação — deve partir daqui, não do zero.

#### 2.5 RuleRAG — DIVERGENTE (veículo incorreto na proposta PIDTI)

*RuleRAG: Rule-Guided Retrieval-Augmented Generation with Language Models for Question
Answering*, Zhongwu Chen, Chengjin Xu, Dingmin Wang, Zhen Huang, Yong Dou, Jian Guo,
**arXiv:2410.22353**, out/2024.

**Dado corrigido:** a proposta PIDTI cita como *"In: EMNLP 2024, Miami. Proceedings... ACL
Anthology"*. **Não foi localizado registro do trabalho nos anais do EMNLP 2024** (nem na trilha
principal nem em Findings); o item consta como preprint arXiv, com submissão em OpenReview
(`zl3nFqY8l1`). A citação da proposta precisa ser corrigida para preprint.

**O que é.** Introduz regras explícitas para guiar simultaneamente o recuperador (que documentos
buscar) e o gerador (como referir-se aos documentos recuperados), em duas variantes — uma sem
treino, por *in-context learning*. Constrói cinco benchmarks (RuleQA) a partir de grafos de
conhecimento. Reportam +89,2% em Recall@10 e +103,1% em *exact match* sobre RAG padrão.

**O que resolve.** O fato de o RAG padrão considerar apenas a consulta, sem especificar
preferência de recuperação nem instruir o gerador sobre como usar a evidência.

**O que não cobre.** As regras são de recuperação e de atribuição de resposta, não de tipificação
de evidência alimentando um motor probabilístico. Não há posterior, calibração, território ou
equidade.

**Relação com esta pesquisa.** É o precedente correto para a *camada de tipificação simbólica*
prevista na arquitetura — e mostra que essa camada, isoladamente, não é inédita.

#### 2.6 SymRAG — DIVERGENTE (título incorreto na proposta PIDTI)

*SymRAG: Efficient Neuro-Symbolic Retrieval Through Adaptive Query Routing*, Safayat Bin Hakim,
Muhammad Adil, Alvaro Velasquez, Houbing Herbert Song, **arXiv:2506.12981** (jun/2025, revisto
jul/2025), aceito na **NeSy 2025** (19th International Conference on Neurosymbolic Learning and
Reasoning).

**Dado corrigido:** a proposta cita o título como *"Efficient Neuro-Symbolic Retrieval-Augmented
Generation through Adaptive Query Routing"*. O título real é *"Efficient Neuro-Symbolic Retrieval
Through Adaptive Query Routing"* — sem "Augmented Generation". Corrigir também para registrar o
veículo (NeSy 2025), que a proposta omite.

**O que é.** Roteamento adaptativo de consultas por avaliação em tempo real de complexidade e
carga, escolhendo caminho simbólico, neural ou híbrido. Em 2.000 consultas de HotpotQA e DROP,
97,6–100,0% de *exact match* com 3,6–6,2% de uso de CPU e menos de 3,2 s por consulta; desativar
o roteamento adaptativo aumenta o tempo de processamento em 169–1151%.

**O que resolve.** A alocação uniforme de recurso computacional a consultas de dificuldade muito
diferente.

**O que não cobre.** O componente simbólico é de roteamento e execução, não de tipificação
probabilística de evidência. Sem posterior, calibração, território ou equidade.

#### 2.7 NeuSym-RAG — CONFIRMADA

*NeuSym-RAG: Hybrid Neural Symbolic Retrieval with Multiview Structuring for PDF Question
Answering*, Ruisheng Cao et al., **arXiv:2505.19754**, **ACL 2025** (`2025.acl-long.311`).

**O que é.** Combina recuperação neural e simbólica num processo interativo: *chunking* multi-visão
e *parsing* por esquema organizam PDF semiestruturado simultaneamente em banco relacional e em
*vectorstore*, e o agente itera até reunir contexto suficiente.

**O que resolve.** O isolamento entre os paradigmas neural e simbólico, e a perda de estrutura
(seções, tabelas) causada por *chunking* de visão única.

**O que não cobre.** Recuperação e QA sobre documento; nenhuma agregação probabilística de
evidência sobre evento latente, nenhuma calibração de posterior, nenhum recorte territorial.

**Relação com esta pesquisa.** Precedente direto e forte para a arquitetura de recuperação
prevista — inclusive para a ideia de manter representação relacional e vetorial em paralelo, que
é exatamente o que uma trilha auditável exige.

#### 2.8 O cluster de RAG seletivo e calibrado (2026) — CONFIRMADAS

Este grupo apareceu **apenas na busca independente**, não na lista herdada, e é o achado que
derruba a lacuna G4.

- **SURE-RAG** — *Sufficiency and Uncertainty-Aware Evidence Verification for Selective
  Retrieval-Augmented Generation*, Jingxi Qiu, Zeyu Han, Cheng Huang, **arXiv:2605.03534**
  (5/mai/2026). Formula a suficiência de evidência como propriedade **de conjunto**, não de
  passagem isolada: um verificador par a par produz distribuições locais de relação, que são
  agregadas em sinais interpretáveis de nível de resposta — cobertura, força de relação,
  discordância, conflito e incerteza de recuperação —, produzindo decisão de três vias e um
  **escore seletivo auditável**. Macro-F1 calibrado de 0,9075, contra 0,6516 de *mean-pooling*
  DeBERTa e 0,7284 de um juiz GPT-4o, empatando com um *cross-encoder* opaco (0,8888) mas com
  auditabilidade total.
  **Não cobre:** o evento é "a evidência sustenta esta resposta", não um evento latente do mundo;
  não há território nem equidade.
- **FinAbstain** — *Uncertainty-Calibrated Multimodal RAG for Selective Financial Forecasting*,
  Dorothy Torres, Wei Cheng, Henan Huang, **arXiv:2607.24875** (27/jul/2026). Um controlador
  prediz apenas quando a incerteza está abaixo de limiar validado; caso contrário **abstém-se,
  pede evidência, reduz exposição ou encaminha o caso para revisão humana**. Compara *temperature
  scaling*, regressão isotônica, predição conformal e um escore híbrido; avalia acurácia,
  calibração, risco–cobertura, citação, negociação, latência e custo.
  **Não cobre:** o alvo é retorno anormal e volatilidade — evento de mercado, observável *ex
  post* —, não inconsistência cadastral; nenhuma dimensão territorial ou de equidade.
- **EvidentialRAG** — *Quantifying and Mitigating Information Conflict in Multi-Source
  Retrieval-Augmented Generation via Evidential Deep Learning*, S M Asif Hossain, Ruksat Khan
  Shayoni, M. F. Mridha, **arXiv:2607.10491** (11/jul/2026). Converte trechos recuperados em
  evidência probabilística e aplica uma regra de fusão **Dempster-Shafer preservadora de
  conflito**, transferindo desacordo não resolvido para incerteza epistêmica; roteia o gerador
  para resposta direta, resposta ciente do conflito ou abstenção. Reporta **ECE de 0,122**.
  **Não cobre:** o conflito modelado é entre fontes recuperadas, não entre evidências sobre um
  evento latente de um caso; sem território, sem equidade.

**Relação conjunta com esta pesquisa.** Estes três trabalhos, somados a 2.3 e 2.4, estabelecem
que a combinação "recuperação + agregação probabilística de evidência + abstenção calibrada +
encaminhamento a revisão humana" é **prática corrente em 2026**, inclusive em domínio financeiro.
A fase subsequente desta pesquisa deve se posicionar dentro desse campo, não como fundadora dele.

---

### Eixo 3 — Auditoria pública brasileira

Verificado em portais institucionais oficiais (CGU e TCU). Registre-se uma divergência real
entre as duas instituições quanto à expansão do acrônimo ALICE.

#### 3.1 ALICE — CONFIRMADA, com divergência de acrônimo entre CGU e TCU

Fonte oficial CGU: `https://www.gov.br/cgu/pt-br/assuntos/auditoria-e-fiscalizacao/alice`.
Fonte oficial TCU: `https://portal.tcu.gov.br/imprensa/noticias/uso-de-inteligencia-artificial-aprimora-processos-internos-no-tribunal-de-contas-da-uniao`.

**Divergência:** a CGU expande ALICE como **"Analisador de Licitações, Contratos e Editais"**; o
TCU, como **"Análise de Licitações e Editais"**. Ambas as formas são oficiais, cada uma em sua
instituição. Qualquer texto que cite o acrônimo deve declarar a fonte usada.

**O que é.** Ferramenta de análise automatizada de processos de compras e contratações públicas,
que aplica mineração de texto e IA a editais e atas publicados diariamente (Portal de Compras do
Governo Federal e Diário Oficial da União), emitindo alertas de risco.

**O que resolve.** Substitui a auditoria *a posteriori* por auditoria **preventiva e contínua**:
o alerta chega antes da homologação. Em 2024, a CGU relata mais de 161 mil processos analisados e
cerca de R$ 1,25 bilhão em benefícios financeiros por atuação preventiva. Desde maio de 2024, a
CGU disponibiliza a ferramenta a estados e municípios.

**O que não cobre.** O objeto é o **documento de licitação**, não o **cadastro de uma pessoa**;
não há inferência sobre evento latente por indivíduo, não há posterior calibrado, e não há
avaliação pública de distribuição de erro por território ou por perfil de jurisdicionado. O
método declarado é mineração de texto e classificação, não agregação bayesiana explícita.

**Relação com esta pesquisa.** É o precedente institucional que legitima o **formato de saída**:
triagem que produz alerta para revisão humana, com trilha, em órgão de controle brasileiro. É
também a prova de que "sistema de IA para triagem de irregularidade no setor público brasileiro"
não é conceito novo — o que é novo é a pergunta sobre onde o território entra no cálculo.

#### 3.2 SOFIA — CONFIRMADA

**Sistema de Orientação sobre Fatos e Indícios para o Auditor** (TCU). Apoia o auditor na
elaboração de instruções, relatórios e documentação correlata — assistência ao processo de
trabalho, não escoragem de risco por caso. **Não cobre**: nenhuma inferência probabilística
sobre evento latente; nenhuma dimensão territorial.

#### 3.3 ADELE — CONFIRMADA

**Análise de Disputa em Licitações Eletrônicas** (TCU). Evidencia a dinâmica de lances em pregões
eletrônicos, para detectar padrões anômalos de disputa. **Não cobre**: analisa comportamento de
lance em um certame, não consistência cadastral de um requerente; sem posterior calibrado, sem
recorte territorial, sem métrica de equidade.

**Nota de contexto.** O portal do TCU documenta um conjunto maior — ÁGATA (Aplicação Geradora de
Análise Textual com Aprendizado), MONICA (Monitoramento Integrado para o Controle de Aquisições),
SAO (Sistema de Análise de Orçamentos), MARINA (Mapa de Riscos nas Aquisições), CARINA (Crawler e
Analisador de Registros da Imprensa Nacional), Zello e ChatTCU. O padrão do conjunto é
consistente: **triagem automatizada com revisão humana obrigatória**, ausência de avaliação
pública de calibração, e ausência de avaliação pública de equidade territorial dos alertas.
Essa ausência é, ela própria, um dado para §4.

#### 3.4 NIST AI RMF 1.0 — CONFIRMADA

`https://www.nist.gov/itl/ai-risk-management-framework`. Publicado em **26 de janeiro de 2023**;
quatro funções centrais: *Govern*, *Map*, *Measure*, *Manage*; complementado pelo AI RMF
Playbook e pelo Generative AI Profile (julho de 2024). Referência corretamente citada na
proposta PIDTI. **Não cobre**: é framework de governança, não método; não prescreve como
posicionar covariável territorial em um modelo probabilístico.

---

### Eixo 4 — Geradores de dados sintéticos e fontes de dados

O critério de leitura deste eixo é o que consta das decisões metodológicas vigentes: um gerador
**ajustado a dados** destrói a verificabilidade da calibração, porque a avaliação de calibração
exige conhecer os parâmetros verdadeiros que geraram os dados. Isso desqualifica, *para esta
finalidade específica*, toda a família aprendida — o que não é crítica a essas ferramentas, que
resolvem outro problema.

| Ferramenta | Licença verificada | Fonte |
|---|---|---|
| **SDV (Synthetic Data Vault)** | **Business Source License 1.1** — *não* é licença aprovada pela OSI. Change license MIT, quatro anos após o *release*. *Additional Use Grant* proíbe operar a funcionalidade como oferta comercial a terceiros; uso interno permitido | `github.com/sdv-dev/SDV`, arquivo `LICENSE` |
| **synthcity** | **Apache 2.0** | `github.com/vanderschaarlab/synthcity` |
| **ydata-synthetic** | **MIT** — mas **renomeado**: o pacote passou a `fg-data-synthetic`, com migração de import de `ydata_synthetic` para `data_synthetic` | `github.com/ydataai/ydata-synthetic` |
| **DoppelGANger** | Trabalho publicado: Lin, Jain, Wang, Fanti, Sekar, *Using GANs for Sharing Networked Time Series Data*, **IMC 2020** (Best Paper Finalist), **arXiv:1909.13403**, DOI `10.1145/3419394.3423643` | `github.com/fjxmlzn/DoppelGANger` |
| **gretel-synthetics** | **Apache 2.0** (biblioteca aberta; a oferta Navigator é comercial) | `github.com/gretelai/gretel-synthetics` |
| **SynthFin** | **Custom Non-Commercial** — livre para estudo pessoal, pesquisa acadêmica e fins educacionais; **uso comercial exige licença paga**. API hospedada comercial em synthfin.com.br | `github.com/afborda/synthfin-core` |
| **Faker (pt_BR)** | **MIT** | `faker.readthedocs.io/en/stable/locales/pt_BR.html` |
| **brutils** | **MIT** | `github.com/brazilian-utils/brutils-python` |
| **DadosAbertosBrasil** | **MIT** | `github.com/GusFurtado/DadosAbertosBrasil` |
| **mercados** | **LGPL v3** | `github.com/PythonicCafe/mercados` |
| **GeCo** | Gerador de dados pessoais com corrupção configurável, Peter Christen e Dinusha Vatsalan, ANU, 2012 | `dmm.anu.edu.au/geco/flex-data-gen-manual.pdf` |

#### 4.1 SDV / CTGAN — CONFIRMADA, com consequência para a proposta

Biblioteca Python de dados tabulares sintéticos criada no Data to AI Lab do MIT em 2016 e
comercializada pela DataCebo a partir de 2020. Modelos: GaussianCopula (estatístico clássico),
CTGAN e TVAE (aprendizado profundo); suporta tabela única, multi-tabela e sequencial, com
avaliação, anonimização e restrições.

**O que resolve.** Substitui uma base real por um substituto estatisticamente semelhante quando o
original não pode circular.

**O que não cobre — duas coisas, e ambas decisivas.** Primeira: o modelo **aprende** a estrutura a
partir dos dados; não há parâmetro verdadeiro conhecido contra o qual medir calibração, e não há
rótulo de fraude no DF a partir do qual aprender. Segunda: a licença é BSL 1.1, **não** open
source pelo critério da OSI.

**Consequência direta.** A proposta PIDTI lista SDV no *stack tecnológico* (§6.4) e afirma, em
§6.1, que o produto final "utilizará **exclusivamente** tecnologias de código aberto (Open
Source)". As duas afirmações não coexistem. Ver §6.

#### 4.2 SynthFin — CONFIRMADA, e confirma a premissa de G1

Gera datasets sintéticos rotulados de fraude para o sistema financeiro brasileiro: transações
bancárias (PIX, TED, boleto, com campos BACEN — ISPB, end-to-end ID) e eventos de mobilidade,
25 padrões de fraude bancária e 11 de mobilidade, 114+ campos por registro incluindo sinais
biométricos e janelas de velocidade (1h/6h/24h/7d), escore de risco 0–100, reprodutibilidade
determinística por semente.

**Granularidade geográfica — confirmada:** **município**, via **código IBGE de 7 dígitos** e UF,
com ponderação populacional pelo Censo 2022 sobre 104 municípios e as 27 unidades federativas.

**O que resolve.** Fornece um corpus brasileiro rotulado de fraude transacional, com vocabulário
de domínio correto.

**O que não cobre.** (i) A licença é *Custom Non-Commercial*, incompatível com um projeto que se
declara exclusivamente open source e que visa transferência tecnológica ao GDF; **por isso não
foi adotado**. (ii) O objeto é **fraude transacional**, não **inconsistência cadastral e
documental**. (iii) A granularidade para no município — e no nível de município, **o Distrito
Federal é um único município**: as Regiões Administrativas simplesmente não existem nessa
representação. Este último ponto é o que sustenta a premissa de G1, e está verificado.

#### 4.3 GeCo e o gerador brasileiro de Trentin et al. — CONFIRMADAS, e enfraquecem G1

**GeCo** (Christen & Vatsalan, ANU, 2012) gera dados pessoais sintéticos com corrupção
configurável — erros de OCR, teclado, fonéticos e grafias comuns — sobre campos que incluem
nome, sobrenome, nome de nascimento, data de nascimento, **cidade e CEP**, com tabelas de
frequência para cidades e códigos postais.

**Trentin et al. (2018)**, *Synthetic data generator for testing record linkage routines in
Brazil*, **International Journal of Population Data Science 3(4)**, `ijpds.org/article/view/722`,
adapta GeCo (Python e C++) às particularidades brasileiras de formação de nome — múltiplos
sobrenomes, prenomes compostos, alta frequência de homônimos — a partir da análise de registros
reais de mortalidade do Estado do Rio de Janeiro (2013). Campos: nome, nome da mãe, sexo, data de
nascimento e **endereço**.

**O que resolve.** Existe, portanto, um gerador brasileiro de erro documental para teste de
vinculação de registros, com endereço entre os campos corrompidos.

**O que não cobre.** O escopo geográfico é estadual (RJ); a corrupção de endereço é **uniforme**,
não modulada por uma taxa de qualidade de fonte que varie por sub-região; e o rótulo é "mesmo
indivíduo", não um evento latente como fraude. Não há avaliação de calibração nem de equidade.

**Relação com esta pesquisa.** É o trabalho que mais aproxima do gerador aqui usado, e por isso
reclassifica G1 — ver §4.

#### 4.4 Kaggle `mlg-ulb/creditcardfraud` — CONFIRMADA

Confirmado via API do OpenML (`openml.org/api/v1/json/data/42175`, *CreditCardFraudDetection*,
licence "Public"): **284.807 transações** de cartão de crédito de portadores europeus, setembro
de 2013, dois dias, **492 fraudes (0,172%)**. **As features V1–V28 são componentes de PCA**; as
**únicas** não transformadas são `Time` (segundos desde a primeira transação) e `Amount`. O alvo
é `Class`. A própria documentação recomenda AUPRC dada a assimetria de classes.

**O que resolve.** É o *benchmark* padrão de detecção de fraude com forte desbalanceamento.

**O que não cobre — e é por isso que ele não serve aqui.** A anonimização por PCA **destrói a
identidade dos campos**: não existe "evidência de endereço" nem "evidência de situação
cadastral", só V7 e V14. Um método cuja tese é *explicabilidade por campo* e cuja pergunta é
*onde entra a variável territorial* não pode ser avaliado numa base onde os campos foram
dissolvidos e nenhuma variável geográfica sobreviveu. A ausência de qualquer atributo geográfico
é, sozinha, discriminante.

#### 4.5 Utilitários brasileiros — CONFIRMADAS, com duas divergências de identificação

- **Faker** com locale `pt_BR` (MIT) gera CPF, CNPJ, RG e endereços em formato nacional. Gera
  *forma* válida, não *estrutura causal*: um CPF do Faker é sintaticamente válido e
  estatisticamente vazio.
- **brazilian-utils — DIVERGENTE.** O repositório `brazilian-utils/brazilian-utils` é
  **JavaScript/TypeScript**, distribuído via npm. O equivalente **Python** é **`brutils`**
  (`github.com/brazilian-utils/brutils-python`, MIT): valida, formata e gera CPF, CNPJ, CEP
  (com consulta ViaCEP), telefone, e-mail, placa, título de eleitor, processo judicial e
  passaporte. Citar "brazilian-utils" como biblioteca Python é impreciso.
- **DadosAbertosBrasil — DIVERGENTE.** O repositório é **`GusFurtado/DadosAbertosBrasil`** (MIT),
  não a autoria presumida na lista herdada. Módulos: IBGE, IPEA, Câmara, Senado, Bacen, mais uma
  classe UF que consolida dados por unidade federativa. Requer Python 3.10+.
- **mercados** (PythonicCafe, **LGPL v3**) acessa CVM, B3, BCB, STN e IBGE. Cobre **mercado
  financeiro**, não cadastro territorial ou documental — fora do escopo desta pesquisa, e sob
  licença copyleft, que exige atenção em um projeto que planeja registro de software.

---

## 3. Tabela comparativa

Legenda: **Lat.** = o evento modelado é latente/não observável (L) ou observável (O);
**Terr.** = granularidade territorial; **Calib.** = calibração probabilística avaliada;
**Equid.** = equidade entre grupos avaliada; **Expl.** = explicabilidade por campo/evidência.

| Trabalho | Lat. | Granularidade territorial | Calibração avaliada | Equidade avaliada | Explicab. por campo | Licença |
|---|---|---|---|---|---|---|
| Fellegi & Sunter (1969) | O (mesmo indivíduo) | ausente | não | não | **sim** (peso por campo) | artigo (Taylor & Francis) |
| Splink (MoJ UK) | O | ausente | não | não | **sim** (waterfall por campo) | **MIT** |
| Srivastava & Shafer (1994) | L (erro material) | ausente | não aplicável (funções de crença) | não | **sim** (por item de evidência) | artigo (Wiley) |
| WoE/IV formalizado (2509.09855) | O (inadimplência) | ausente | parcial (IV = Jeffreys) | **sim** (via atributo protegido) | **sim** (WoE por bin) | arXiv |
| Daniel (2021) | L (fraude) | ausente | não | não | **sim** (por fonte) | arXiv |
| Lewis et al. (2020) — RAG | não aplicável | ausente | não | não | parcial (documento citado) | arXiv/NeurIPS |
| BayesRAG (2601.07329) | não aplicável | ausente | confiança de recuperação | não | parcial | arXiv |
| Bayesian RAG financeiro (PMC12886353) | não aplicável | ausente | **sim** (incerteza do QA) | não | parcial | Frontiers (acesso aberto) |
| Bayesian Uncert. Propagation (2607.00972) | não aplicável | ausente | **sim** (propagada) | não | parcial | arXiv |
| RuleRAG (2410.22353) | não aplicável | ausente | não | não | **sim** (regra explícita) | arXiv (preprint) |
| SymRAG (2506.12981) | não aplicável | ausente | não | não | parcial (rota escolhida) | arXiv/NeSy 2025 |
| NeuSym-RAG (2505.19754) | não aplicável | ausente | não | não | **sim** (consulta SQL) | arXiv/ACL 2025 |
| SURE-RAG (2605.03534) | O (suficiência) | ausente | **sim** (escore seletivo) | não | **sim** (sinais agregados) | arXiv |
| FinAbstain (2607.24875) | O (retorno *ex post*) | ausente | **sim** (4 métodos) | não | **sim** (citação) | arXiv |
| EvidentialRAG (2607.10491) | O (resposta correta) | ausente | **sim** (ECE 0,122) | não | **sim** (conflito por fonte) | arXiv |
| ALICE (CGU/TCU) | L (irregularidade) | jurisdição/órgão | não publicada | não publicada | **sim** (alerta tipificado) | ferramenta de Estado |
| SOFIA (TCU) | não aplicável | ausente | não publicada | não publicada | parcial | ferramenta de Estado |
| ADELE (TCU) | L (conluio em lance) | certame | não publicada | não publicada | parcial | ferramenta de Estado |
| SDV / CTGAN | não aplicável (gerador) | o que houver na base ajustada | **não** (parâmetro verdadeiro desconhecido) | não | não | **BSL 1.1** |
| synthcity | não aplicável (gerador) | idem | **não** | métricas de *fairness* incluídas | não | **Apache 2.0** |
| gretel-synthetics | não aplicável (gerador) | idem | **não** | não | não | **Apache 2.0** |
| DoppelGANger | não aplicável (gerador) | metadados de série | **não** | não | não | artigo + código aberto |
| SynthFin | L (fraude, rotulada) | **município (IBGE, 7 díg.)** | não | não | parcial (escore 0–100) | **Custom Non-Commercial** |
| GeCo (ANU, 2012) | O (mesmo registro) | cidade + CEP (corrupção uniforme) | não | não | não | ferramenta acadêmica |
| Trentin et al. (2018) | O (mesmo indivíduo) | **estado (RJ)** | não | não | não | IJPDS (CC BY-NC-ND) |
| Kaggle creditcardfraud | O (chargeback) | **nenhuma** (PCA) | não | não | **não** (campos dissolvidos) | DbCL / "Public" |
| Akpinar et al. (2024) | O | ausente (grupos por uso de serviço) | não | **sim** | não | FAccT / arXiv |
| Saxena et al. (2403.14040) | — (posição) | localização como proxy | não | **sim** | não | arXiv |
| **Esta pesquisa (camada de agregação)** | **L (fraude latente)** | **Região Administrativa (intramunicipal, DF) — cobertura *estipulada*, não medida** | **sim (Brier + ECE, 224 config.)** | **sim (FPR por RA, 48 config.)** | **sim (log-razão por campo)** | numpy + matplotlib |

---

## 4. Diferencial e brechas

Para cada lacuna, procurou-se ativamente o trabalho que a preencheria. Duas foram reclassificadas
por essa busca, e uma delas **cai**. Isso é o resultado do método, não uma falha dele.

### G1 — Gerador de inconsistência cadastral-documental com estrutura territorial intramunicipal

**Onde procurei.** Repositório e licença do SynthFin; a família aprendida (SDV/CTGAN, synthcity,
ydata-synthetic/fg-data-synthetic, DoppelGANger, gretel-synthetics); a família de vinculação de
registros (GeCo/Febrl, com o manual do ANU); e uma busca dirigida por "gerador sintético com
estrutura geográfica sub-municipal / de bairro para erro de registro", que trouxe o gerador
brasileiro de Trentin et al. (2018) no IJPDS.

**O que a busca encontrou.** A premissa central **está confirmada**: SynthFin para no código IBGE
de 7 dígitos, granularidade em que o DF é um único município e as Regiões Administrativas
inexistem. Mas GeCo já corrompe **cidade e CEP** com tabelas de frequência, e Trentin et al. já
construíram um gerador **brasileiro** de erro documental incluindo o campo endereço.

**Classificação: lacuna de aplicação.** "Gerador sintético de erro documental com campo de
endereço, no Brasil" existe. O que não foi localizado é o componente estreito e específico: um
gerador em que a **taxa de falso-positivo de uma evidência varie por sub-região municipal como
função declarada e conhecida da cobertura cadastral**, de modo que a disparidade observada nos
resultados seja atribuível por construção à fonte e não à população. Esse componente é a
contribuição real, e é modesto — é uma escolha de parametrização do mecanismo causal, não um
artefato de software novo. O relatório deve dizê-lo nesses termos, e citar GeCo e Trentin et al.
como antecedentes em vez de omiti-los.

### G2 — A escolha entre prior e verossimilhança para o dado territorial, posta como experimento

**Onde procurei.** Literatura bayesiana de seleção/triagem de covariáveis e de informação de
grupo; Fellegi-Sunter e Splink (onde o território simplesmente não é tratado como dimensão);
literatura de funções de crença em auditoria; e uma busca dirigida ao **mecanismo** por trás do
achado, sob o nome que a estatística lhe dá: reuso do dado para estimar o prior.

**O que a busca encontrou.** O mecanismo tem nome e é reconhecido: em Bayes empírico, o "double
dipping" — usar o mesmo conjunto de dados primeiro para estimar os parâmetros do prior e depois
para computar a estatística de interesse — é problema conhecido e discutido, com propostas
explícitas de mitigação por redução do contato direto do prior com o dado observado. Não localizei
uma citação canônica aberta a incluir nas referências, de modo que **nada entra na lista por esta
via**; mas a informação existe e obriga uma ressalva.

**Classificação: lacuna real, estreita — com o mecanismo já conhecido sob outro nome.** Não foi
localizado trabalho que ponha a **posição** da covariável territorial (prior versus
verossimilhança) como *variável experimental*, varrida sistematicamente e avaliada
simultaneamente por calibração (Brier, ECE) e por distribuição de falsos positivos entre
sub-regiões. A contribuição, portanto, **não é o mecanismo** — que é o double dipping de Bayes
empírico, conhecido — mas a **demonstração de que ele é o modo de falha dominante da escolha de
projeto que um analista faria naturalmente** neste domínio, e a quantificação do dano (dominância
em 224/224 configurações, ECE de 0,0025 para 0,2255 na referência). Enunciada assim, a alegação
se sustenta; enunciada como "descoberta de um mecanismo", não.

### G3 — Disparidade emergindo sem variável demográfica, a partir da qualidade desigual da fonte

**Onde procurei.** Busca dirigida por equidade algorítmica decorrente de qualidade de dado e de
erro de medição diferencial, sem atributo protegido; e por "spatial fairness" / redlining
geográfico em crédito.

**O que a busca encontrou — e este é o resultado que mais enfraquece a alegação original.**

**Akpinar, Lipton & Chouldechova (2024)**, *The Impact of Differential Feature Under-reporting on
Algorithmic Fairness*, **FAccT 2024**, **arXiv:2401.08788**, estuda exatamente o mecanismo geral:
o sub-reporte diferencial de features entre subpopulações como **motor** de disparidade em decisão
algorítmica, mostrando que o sub-reporte tipicamente **agrava** disparidades em dados reais e que
métodos padrão de dado faltante **não** mitigam o viés nesse cenário. As subpopulações são
definidas por maior dependência de serviços públicos, não por atributo protegido formal.

Em contraste, **Saxena, Horn, Zhang & Shahabi**, *Spatial Fairness: The Case for its Importance,
Limitations of Existing Work, and Guidelines for Future Research*, **arXiv:2403.14040**,
representa a via clássica e **não** cobre o caso: argumenta que a localização é problemática
porque **correlaciona com características protegidas** — é o enquadramento de proxy de redlining,
exatamente o que esta pesquisa **não** está afirmando.

**Classificação: lacuna de aplicação — G3 enfraquecida.** O mecanismo geral está publicado, em
veículo de primeira linha, dois anos antes. Reivindicar que "a disparidade emerge da qualidade
desigual da fonte, sem variável protegida" como observação original **não passaria em banca**.
Resta o que Akpinar et al. não fazem: o caso em que a qualidade desigual afeta a
**especificidade** de uma evidência (a taxa de falso-positivo de "endereço não localizado" cresce
onde o cadastro é pior) e não a **presença** do dado; a granularidade intramunicipal; a aplicação
a triagem cadastral no DF; e a demonstração com **taxa do evento idêntica por construção**, que é
o controle que permite atribuir toda a disparidade à fonte. O resumo e o *short paper* devem
**citar Akpinar et al. (2024)** e posicionar-se como aplicação e extensão, não como descoberta.

### G4 — Calibração do posterior agregado sob *selective prediction* em RAG

**Onde procurei.** Busca dirigida por RAG + *selective prediction* + calibração + abstenção +
ECE + agregação de evidência.

**O que a busca encontrou.** Um campo ativo e recente, inteiramente ausente da lista herdada:
SURE-RAG (arXiv:2605.03534) formula a suficiência de evidência como propriedade de conjunto e
produz um escore seletivo auditável calibrado; FinAbstain (arXiv:2607.24875) faz predição seletiva
com quatro métodos de calibração, curvas risco–cobertura e **encaminhamento explícito para revisão
humana**, em domínio financeiro; EvidentialRAG (arXiv:2607.10491) funde evidência de múltiplas
fontes por regra Dempster-Shafer preservadora de conflito e **reporta ECE** como métrica de
avaliação. Somam-se a eles 2.3 e 2.4.

**Classificação: lacuna aparente — G4 derrubada.** A afirmação de que "avaliação de RAG mede
qualidade de recuperação e a calibração do posterior agregado sob selective prediction não é
prática corrente" **é falsa em 2026**. Ela pode ter sido verdadeira quando a proposta foi
redigida; não é mais. G4 deve ser removida de qualquer texto submetido. Em seu lugar, a fase
subsequente da pesquisa ganha algo melhor do que uma lacuna: um conjunto de baselines concretos e
um vocabulário estabelecido (risco–cobertura, escore seletivo, abstenção) contra os quais se
posicionar.

### Síntese do diferencial, após as reclassificações

O que sobrevive à busca é mais estreito e mais defensável do que a formulação original:

1. **A pergunta.** Onde a covariável territorial deve entrar — prior ou verossimilhança — posta
   como experimento controlado, com critérios de aceitação pré-registrados e a regra declarada de
   que achado reprovado sai do texto. Um dos três critérios foi de fato reprovado e o achado
   correspondente foi removido; isso é o que dá crédito aos outros dois.
2. **A granularidade.** Região Administrativa do DF é **intramunicipal**, e nenhum recurso
   verificado neste relatório — SynthFin, GeCo, Trentin et al., a família aprendida — opera abaixo
   do município. No nível de município, o objeto de estudo desaparece.
3. **O controle.** Taxa do evento **idêntica por construção** entre regiões, o que transforma
   qualquer disparidade observada em atribuição causal à qualidade da fonte, e não em correlação
   a interpretar.
4. **A conjunção de métricas.** Calibração (Brier, ECE) **e** distribuição de falsos positivos por
   sub-região, medidas na mesma varredura. Cada uma isoladamente é padrão; a tabela de §3 mostra
   que nenhum trabalho verificado mede as duas com recorte territorial.
5. **O resultado negativo.** A demonstração de que **não há correção, no nível da agregação de
   evidências**, para desigualdade produzida por qualidade desigual de dado — incluindo a
   reprovação da hipótese de que mover o território para a verossimilhança resolveria o problema.

---

## 5. O que NÃO é inédito

Esta seção não é concessão retórica. É o que dá crédito às alegações de §4, e sua ausência é o
que faz um relatório de benchmarking ser lido como autoelogio.

- **A agregação bayesiana por razão de verossimilhança é de 1969.** Fellegi & Sunter, JASA 64.
  As variantes `A`, `B` e `C` do experimento são esse modelo. A implementação de referência
  existe, é madura e é MIT (Splink). Nenhuma linha do motor probabilístico é contribuição desta
  pesquisa.
- **A mesma matemática já governa o scorecard de crédito.** O Weight of Evidence é a log-razão de
  verossimilhança por *bin*; arXiv:2509.09855 formaliza a equivalência. Um scorecard logístico com
  WoE e um modelo de Fellegi-Sunter agregam evidência pelo mesmo mecanismo.
- **Combinar RAG com inferência bayesiana já está publicado — e verificado.** *Bayesian RAG:
  uncertainty-aware retrieval for reliable financial question answering* (Frontiers in Artificial
  Intelligence, jan/2026, PMC12886353) está em veículo indexado, em **domínio financeiro**.
  Somam-se BayesRAG (arXiv:2601.07329) e a propagação bayesiana de incerteza em RAG agêntico
  (arXiv:2607.00972). O rótulo "RAG bayesiano" está ocupado.
- **RAG neuro-simbólico com tipificação por regra já está publicado.** RuleRAG (arXiv:2410.22353),
  SymRAG (NeSy 2025), NeuSym-RAG (ACL 2025). A camada de tipificação simbólica prevista na
  arquitetura não é, isoladamente, novidade.
- **Predição seletiva calibrada com encaminhamento a revisão humana já é prática corrente.**
  SURE-RAG, FinAbstain, EvidentialRAG — todos de 2026, um deles em domínio financeiro, com ECE,
  abstenção e curvas risco–cobertura. Ver G4.
- **O mecanismo do achado sobre o prior não é novo.** Estimar o prior a partir dos mesmos dados que
  depois entram na verossimilhança é o "double dipping" reconhecido em Bayes empírico. O que é
  contribuição é a demonstração de que ele domina — em 224/224 configurações — a escolha de
  projeto que um analista adotaria naturalmente na ausência de rótulo de fraude.
- **O mecanismo do achado sobre equidade não é novo.** Akpinar, Lipton & Chouldechova, FAccT 2024.
  Ver G3.
- **As métricas de equidade são padrão.** Taxa de falso-positivo por grupo é métrica estabelecida
  da literatura de *fairness*.
- **Triagem automatizada com revisão humana no setor público brasileiro não é conceito novo.**
  ALICE opera desde antes desta pesquisa, com resultados publicados pela CGU, e foi disponibilizada
  a estados e municípios em 2024.
- **Simulação de mecanismo com parâmetros conhecidos é método clássico**, não inovação
  metodológica. É a escolha correta aqui — por razões declaradas: fraude é latente, não há corpus
  rotulado, e avaliar calibração exige conhecer a verdade que gerou o dado —, mas é uma escolha
  padrão.

**O que resta, dito com precisão:** o inédito está na **pergunta** e no **desenho que a responde**,
não no maquinário. A pergunta é onde o dado territorial entra; o desenho é uma varredura com taxa
do evento igualada por construção, em granularidade intramunicipal, medindo calibração e
distribuição de falsos positivos juntas, com critérios de aceitação declarados antes da execução —
um dos quais reprovou.

---

## 6. Correções recomendadas à proposta PIDTI

### 6.1 A afirmação de "exclusivamente open source" está incorreta como redigida

A §6.1 da proposta afirma que o produto final "utilizará **exclusivamente** tecnologias de código
aberto (Open Source)". A §6.4 lista, no *stack tecnológico*, o **SDV (Synthetic Data Vault)**. O
arquivo `LICENSE` do repositório oficial do SDV é a **Business Source License 1.1** — licença
*source-available*, **não** aprovada pela OSI, com *change license* MIT apenas quatro anos após
cada *release* e um *Additional Use Grant* que proíbe expressamente operar a funcionalidade como
oferta comercial a terceiros. As duas afirmações da proposta são incompatíveis.

**Correção recomendada.** Escolher uma das três saídas, e apenas uma:

- **(a)** Remover SDV do stack. É a saída coerente com a decisão metodológica vigente, que já
  descarta geradores ajustados a dados por destruírem a verificabilidade da calibração — e com o
  fato de que a camada de agregação já foi implementada com um gerador causal próprio sobre
  `numpy`, sem dependência alguma de SDV. Se for necessário um substituto de prateleira,
  **synthcity é Apache 2.0**.
- **(b)** Manter SDV e **substituir** "exclusivamente open source" por formulação verificável —
  por exemplo, "sem custo de licença para uso acadêmico e sem dependência de créditos de nuvem",
  que é o que a proposta de fato quer dizer e que a BSL de fato permite.
- **(c)** Manter as duas afirmações e assumir a inconsistência. Não é recomendável em documento
  que será avaliado.

**Ponto correlato — SynthFin.** A licença é **Custom Non-Commercial** (confirmada no repositório):
livre para pesquisa acadêmica, uso comercial mediante licença paga. Um projeto que visa registro
de software no NIT/UnDF e plano de transferência tecnológica ao GDF não pode incorporá-la sem
resolver essa cláusula. **A decisão de não adotar SynthFin está correta e deve ser mantida** — e a
proposta deve registrá-la explicitamente, porque uma decisão de licenciamento documentada é
argumento de maturidade técnica, não confissão de limitação.

**Ponto a verificar, não afirmado aqui.** A proposta prevê inferência local via Ollama com
Llama-3/Mistral. As licenças dos **pesos** desses modelos não foram verificadas neste relatório e
não são objeto dele; recomenda-se submetê-las ao mesmo critério antes de repetir a palavra
"exclusivamente".

### 6.2 A contradição entre hipóteses precisa ser reescrita como desenho experimental

**Correção de identificação, antes da correção de conteúdo.** A numeração usada informalmente no
projeto inverteu as hipóteses. No PDF, o texto é:

- **H2:** "A explicitação dos cálculos probabilísticos em linguagem natural aumenta a
  confiabilidade das decisões, **reduzindo vieses contra populações vulneráveis**."
- **H3:** "O uso de dados locais (CODEPLAN/GDF) para **calibração do prior bayesiano** supera
  modelos genéricos nacionais em relevância demográfica."

Ou seja: é **H3** que propõe o prior regional, e **H2** que promete a redução de viés — o inverso
do que se vinha repetindo. A correção importa porque a hipótese que o experimento **reprovou** é
H3, e citá-la pelo número errado inutiliza a correção.

**A contradição, enunciada.** H3 eleva a suspeita basal de quem mora em determinadas Regiões
Administrativas e registra isso por escrito na própria trilha de auditoria que H2 promete usar
para reduzir viés. As duas hipóteses apontam em direções opostas, e o experimento mostrou que H3
não apenas conflita com H2 como é **estatisticamente incorreta**: condicionar o prior à taxa
observada da região é dominado em Brier e em ECE em 224/224 configurações, por dupla contagem do
mesmo sinal.

**Reescrita recomendada.** Substituir H3 por uma hipótese que seja testável e que o experimento
efetivamente tenha respondido, transformando a contradição em pergunta de pesquisa:

> **H3 (reescrita):** *A posição em que o dado territorial entra no modelo — prior ou
> verossimilhança — determina simultaneamente a calibração do escore de suspeita e a distribuição
> do custo do falso positivo entre as Regiões Administrativas. Condicionar o prior à taxa
> observada da região degrada a calibração por dupla contagem de evidência e concentra falsos
> positivos onde a cobertura do cadastro é menor.*

E acrescentar a ressalva, verificada e obrigatória:

> **Ressalva sobre a tentativa de reconciliar H3 com H2.** A hipótese de que mover o dado
> territorial para a verossimilhança reconciliaria acurácia e equidade **foi testada e
> reprovada**. Os dois números precisam ser distinguidos: a inversão **estrita** do sinal da
> correlação ocorre em **30 de 48** configurações, e o critério pré-registrado
> (`corr ≥ −0,10`) é atendido em **33 de 48**. A falha se concentra em duas faixas — ruído
> baixo com gradiente territorial íngreme, e **ruído alto com prevalência alta** —, e a
> amplitude de disparidade dessa variante é o triplo da variante que ignora o território. A
> variante pode ser usada para ganho modesto de acurácia, desde que a ressalva de robustez seja
> declarada — mas **não deve ser apresentada como solução de equidade**. Os valores de cobertura
> cadastral por Região Administrativa que sustentam esse resultado são **estipulados, não
> medidos** (ver Anexo).

### 6.3 Correções bibliográficas na §8 da proposta

- **CHEN, Z. et al. RuleRAG.** A proposta cita como *"In: EMNLP 2024, Miami. Proceedings... ACL
  Anthology"*. Não foi localizado registro nos anais do EMNLP 2024. Corrigir para preprint:
  *arXiv:2410.22353, 2024*.
- **HAKIM, S. B. et al. SymRAG.** Título incorreto. O correto é *"SymRAG: Efficient Neuro-Symbolic
  Retrieval Through Adaptive Query Routing"* — sem "Augmented Generation". Acrescentar o veículo:
  **NeSy 2025**.
- **LEWIS, P. et al.** e **NIST AI RMF 1.0** estão corretos; recomenda-se apenas completar com
  arXiv:2005.11401 e com a data de publicação do framework (26/jan/2023).

### 6.4 Duas observações de coerência interna, sem valor de correção obrigatória

- A proposta lista **PyMC (v5+)** no stack e na Etapa 3. A camada de agregação de evidências, tal
  como executada, não requer PyMC — o cálculo é log-razão de verossimilhança fechada — e as
  decisões metodológicas vigentes desaconselham a dependência. Vale alinhar a Etapa 3 ao que foi
  efetivamente executado, ou declarar PyMC como previsto apenas para fases posteriores.
- A proposta acerta em um ponto que merece ser preservado e destacado, porque é justamente onde
  muitos trabalhos do gênero erram: declara que os dados públicos são tratados "como evidência
  contextual auditável, **não como ground truth de fraude**", e que o sistema "não automatiza
  concessões ou negações, mas emite pareceres técnicos". Ambas as afirmações estão alinhadas com o
  que o experimento assume e com o que este relatório sustenta.

---

## 7. Referências

Apenas itens **CONFIRMADOS** ou **DIVERGENTES com o dado já corrigido**. As três descartadas
(§1.1) não aparecem aqui.

**Eixo 1 — Agregação probabilística de evidência**

1. FELLEGI, I. P.; SUNTER, A. B. A Theory for Record Linkage. *Journal of the American Statistical
   Association*, v. 64, p. 1183–1210, 1969. DOI 10.1080/01621459.1969.10501049.
   https://doi.org/10.1080/01621459.1969.10501049
2. MINISTRY OF JUSTICE (UK). **Splink** — probabilistic record linkage em Python. Licença MIT.
   https://github.com/moj-analytical-services/splink
3. SRIVASTAVA, R. P.; SHAFER, G. Integrating statistical and nonstatistical audit evidence using
   belief functions: A case of variable sampling. *International Journal of Intelligent Systems*,
   v. 9, p. 519–539, 1994. DOI 10.1002/int.4550090603.
   https://www.glennshafer.com/assets/downloads/articles/article51.pdf
   *(Registrado anteriormente como "~1995"; ano correto: 1994.)*
4. An Information-Theoretic Framework for Credit Risk Modeling: Unifying Industry Practice with
   Statistical Theory for Fair and Interpretable Scorecards. arXiv:2509.09855.
   https://arxiv.org/abs/2509.09855
5. DANIEL, F. Bayesian and Dempster-Shafer models for combining multiple sources of evidence in a
   fraud detection system. arXiv:2104.07440, 2021. https://arxiv.org/abs/2104.07440

**Eixo 2 — RAG com camada probabilística ou simbólica**

6. LEWIS, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS,
   2020. arXiv:2005.11401. https://arxiv.org/abs/2005.11401
7. LI, X. et al. BayesRAG: Probabilistic Mutual Evidence Corroboration for Multimodal
   Retrieval-Augmented Generation. arXiv:2601.07329, 2026. https://arxiv.org/abs/2601.07329
8. NGARTERA, L.; NADARAJAH, S.; KOINA, R. Bayesian RAG: uncertainty-aware retrieval for reliable
   financial question answering. *Frontiers in Artificial Intelligence*, 27 jan. 2026.
   PMC12886353. https://pmc.ncbi.nlm.nih.gov/articles/PMC12886353/
9. DONALDSON, L.; WALKER, C.; ASLANSEFAT, K.; PAPADOPOULOS, Y. Bayesian Uncertainty Propagation
   for Agentic RAG Pipelines: A Proof-of-Concept Study on Multi-Hop Question Answering.
   arXiv:2607.00972, 2026. https://arxiv.org/abs/2607.00972
10. CHEN, Z. et al. RuleRAG: Rule-Guided Retrieval-Augmented Generation with Language Models for
    Question Answering. arXiv:2410.22353, 2024. https://arxiv.org/abs/2410.22353
    *(Preprint; não localizado nos anais do EMNLP 2024, ao contrário do que consta na §8 da
    proposta PIDTI.)*
11. HAKIM, S. B.; ADIL, M.; VELASQUEZ, A.; SONG, H. H. SymRAG: Efficient Neuro-Symbolic Retrieval
    Through Adaptive Query Routing. NeSy 2025. arXiv:2506.12981.
    https://arxiv.org/abs/2506.12981 *(Título corrigido: sem "Augmented Generation".)*
12. CAO, R. et al. NeuSym-RAG: Hybrid Neural Symbolic Retrieval with Multiview Structuring for PDF
    Question Answering. ACL 2025. arXiv:2505.19754. https://arxiv.org/abs/2505.19754
13. QIU, J.; HAN, Z.; HUANG, C. SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification
    for Selective Retrieval-Augmented Generation. arXiv:2605.03534, 2026.
    https://arxiv.org/abs/2605.03534
14. TORRES, D.; CHENG, W.; HUANG, H. FinAbstain: Uncertainty-Calibrated Multimodal RAG for
    Selective Financial Forecasting. arXiv:2607.24875, 2026. https://arxiv.org/abs/2607.24875
15. HOSSAIN, S. M. A.; SHAYONI, R. K.; MRIDHA, M. F. EvidentialRAG: Quantifying and Mitigating
    Information Conflict in Multi-Source Retrieval-Augmented Generation via Evidential Deep
    Learning. arXiv:2607.10491, 2026. https://arxiv.org/abs/2607.10491

**Eixo 3 — Auditoria pública brasileira e governança**

16. CONTROLADORIA-GERAL DA UNIÃO. **ALICE** — Analisador de Licitações, Contratos e Editais.
    https://www.gov.br/cgu/pt-br/assuntos/auditoria-e-fiscalizacao/alice
17. TRIBUNAL DE CONTAS DA UNIÃO. Uso de inteligência artificial aprimora processos internos no
    Tribunal de Contas da União. *(Fonte oficial para SOFIA — Sistema de Orientação sobre Fatos e
    Indícios para o Auditor — e ADELE — Análise de Disputa em Licitações Eletrônicas; o TCU expande
    ALICE como "Análise de Licitações e Editais", divergindo da CGU.)*
    https://portal.tcu.gov.br/imprensa/noticias/uso-de-inteligencia-artificial-aprimora-processos-internos-no-tribunal-de-contas-da-uniao
18. NIST. Artificial Intelligence Risk Management Framework (AI RMF 1.0), 26 jan. 2023.
    https://www.nist.gov/itl/ai-risk-management-framework

**Eixo 4 — Geradores sintéticos, fontes e utilitários**

19. SDV — Synthetic Data Vault. **Business Source License 1.1** (change license MIT, quatro anos).
    https://github.com/sdv-dev/SDV
20. **synthcity** (van der Schaar Lab). Apache 2.0. https://github.com/vanderschaarlab/synthcity
21. **ydata-synthetic** / **fg-data-synthetic**. MIT. *(Pacote renomeado; import migrado de
    `ydata_synthetic` para `data_synthetic`.)* https://github.com/ydataai/ydata-synthetic
22. LIN, Z.; JAIN, A.; WANG, C.; FANTI, G.; SEKAR, V. Using GANs for Sharing Networked Time Series
    Data: Challenges, Initial Promise, and Open Questions. **IMC 2020** (Best Paper Finalist). DOI
    10.1145/3419394.3423643. arXiv:1909.13403. https://github.com/fjxmlzn/DoppelGANger
23. **gretel-synthetics** (Gretel.ai). Apache 2.0. https://github.com/gretelai/gretel-synthetics
24. **SynthFin-Core**. **Custom Non-Commercial License**. Granularidade geográfica: município,
    código IBGE de 7 dígitos, ponderado pelo Censo 2022 (104 municípios, 27 UFs).
    https://github.com/afborda/synthfin-core
25. CHRISTEN, P.; VATSALAN, D. *A flexible data generator for privacy-preserving data mining and
    record linkage* (**GeCo**), Release 0.1. Australian National University, 3 jun. 2012.
    https://dmm.anu.edu.au/geco/flex-data-gen-manual.pdf
26. TRENTIN, D. et al. Synthetic data generator for testing record linkage routines in Brazil.
    *International Journal of Population Data Science*, v. 3, n. 4, 2018.
    https://ijpds.org/article/view/722
27. **Faker** — locale `pt_BR`. MIT. https://faker.readthedocs.io/en/stable/locales/pt_BR.html
28. **brutils** (brazilian-utils). MIT. *(Biblioteca Python; o repositório
    `brazilian-utils/brazilian-utils` é JavaScript/TypeScript.)*
    https://github.com/brazilian-utils/brutils-python
29. FURTADO, G. **DadosAbertosBrasil**. MIT. https://github.com/GusFurtado/DadosAbertosBrasil
30. PYTHONIC CAFE. **mercados**. LGPL v3. https://github.com/PythonicCafe/mercados
31. Credit Card Fraud Detection (`mlg-ulb/creditcardfraud`). 284.807 transações, 492 fraudes
    (0,172%); **V1–V28 são componentes de PCA**; apenas `Time` e `Amount` não transformadas.
    Registro verificado no OpenML: https://www.openml.org/api/v1/json/data/42175

**Equidade e qualidade de dado**

32. AKPINAR, N.-J.; LIPTON, Z. C.; CHOULDECHOVA, A. The Impact of Differential Feature
    Under-reporting on Algorithmic Fairness. **FAccT 2024**. arXiv:2401.08788.
    https://arxiv.org/abs/2401.08788
33. SAXENA, N. A.; HORN, A. L.; ZHANG, W.; SHAHABI, C. Spatial Fairness: The Case for its
    Importance, Limitations of Existing Work, and Guidelines for Future Research. arXiv:2403.14040.
    https://arxiv.org/abs/2403.14040

---

## Anexo — Limitação declarada que este relatório não pode resolver

O vetor `COBERTURA` do gerador é **estipulado, não medido**. Nenhuma das fontes verificadas neste
relatório fornece cobertura do cadastro territorial por Região Administrativa do DF; obter esse
dado junto ao Geoportal/SEDUH permanece a pendência de maior retorno por esforço, e o resumo
declara essa limitação explicitamente. Enquanto ela persistir, as **magnitudes** relatadas são
consequência dos parâmetros adotados, e apenas as **direções**, verificadas em toda a grade de
sensibilidade, devem ser lidas como resultado.
