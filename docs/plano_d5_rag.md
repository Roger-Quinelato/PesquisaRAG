# Plano da fase RAG (D5)

Prazo do épico D5: 26/03/2027 (Trello). Este plano **segue** `relatorios/Benchmark_Modelos_HuggingFace.md`
(§9 e §10) e o torna operacional. **Nenhum modelo foi executado e nenhum critério abaixo foi
rodado.** Os critérios são declarados agora, antes de qualquer rodada, e só mudam por registro
datado em novo documento, como em `protocolo_versionamento.md` §3. Status: **proposta, a validar
com a orientação.**

## 1. Pergunta e escopo

Pergunta: dado um caso de crédito, o retriever encontra a evidência certa nas fontes oficiais, e
**encontra igualmente bem para todas as RAs**?

A segunda metade é o achado central da pesquisa levado para a camada RAG: se o retriever acha pior
a evidência de endereço onde a cobertura cadastral é baixa, a desigualdade entra **antes** do motor
bayesiano. Por isso a equidade da recuperação é critério de primeira classe, e não apêndice.

Fora do escopo da D5: motor bayesiano (D7), explicação em linguagem natural (D9), OCR (só se o
corpus tiver documentos digitalizados; hoje não tem).

## 2. Pré-requisitos (bloqueiam a D5)

1. **Corpus.** Definir o que é indexado. Hoje os dados são sintéticos e tabulares, e as fontes
   oficiais (`fontes_oficiais.csv`, local) são portais e bases estruturadas. Sem decidir se o
   corpus são normas, manuais de cadastro ou registros, o gold set não existe.
2. **Cobertura cadastral medida** (D3.T1/T2, ver `catalogo_fontes_locais.md`). Sem ela, "recall por
   RA contra cobertura" correlaciona com um vetor estipulado.
3. **8 ou 33 RAs** (decisão pendente, `catalogo_fontes_locais.md` §2).
4. **Hardware.** Definir qual faixa de teste (CPU, GPU de 8 GB ou de 16 a 24 GB). Muda a lista de
   candidatos.
5. **Corrigir a proposta** nos itens de licença (`correcoes_proposta_pidti.md`, itens 1 a 4), para
   que os modelos escolhidos não contradigam "exclusivamente open source".

## 3. Experimentos

Em todos: revisão (SHA do Hub) de cada modelo fixada, quantização exata, temperatura 0, semente
declarada, pesos fora do git, resultados no ledger.

| Exp. | Papel | Candidatos (ordem do benchmark §10) | Controle obrigatório | Métrica principal |
|---|---|---|---|---|
| E1 | Embedding | CPU: `BAAI/bge-m3`, `Snowflake/snowflake-arctic-embed-l-v2.0`, `google/embeddinggemma-2`. GPU: `Qwen/Qwen3-Embedding-4B`, `Qwen/Qwen3-Embedding-8B` | **BM25** | nDCG@10 |
| E2 | Reranker | `BAAI/bge-reranker-v2-m3`, `Qwen/Qwen3-Reranker-0.6B`, `Alibaba-NLP/gte-multilingual-reranker-base` | sem reranker | ganho de nDCG@10 sobre o embedding sozinho |
| E3 | Extração | `fastino/gliner2-multi-v1`; LLM de 3 a 4 B com JSON | **regex com validação** (CPF, CNPJ, CEP, datas, valores) | F1 por campo |
| E4 | Verificador | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`; LLM-juiz de outra família | — | F1 em pares (evidência, frase) |

O relatório XAI (D9) e o LLM que o redige ficam fora da D5; o benchmark os trata na §9 e o
controle ali é "template sem LLM".

## 4. Critérios declarados antes de rodar

Gold set: 100 a 200 consultas com o trecho correto rotulado à mão sobre o corpus da D5. Sanidade
externa em `MTEB-BR/quati-50k` e `MTEB-BR/quati-reranking`.

| Id | Critério | Leitura se falhar |
|---|---|---|
| R1 | O melhor embedding denso supera o BM25 em nDCG@10 | Se não supera, a camada densa não se justifica para identificadores exatos; usar BM25 ou híbrido |
| R2 | Escolha do modelo: o **menor** cuja nDCG@10 fique a até 1 p.p. do melhor | Regra de desempate já registrada no benchmark §9; custo offline faz parte do produto |
| R3 | O reranker melhora nDCG@10 sobre o embedding sozinho em pelo menos 1 p.p. | Se não, não entra no pipeline |
| R4 | **Equidade:** `corr(cobertura_r, Recall@5_r) ≥ −0,10` e amplitude de `Recall@5` entre RAs ≤ 5 p.p. | Se falha, o retriever reproduz a disparidade territorial, e isso entra no relatório com o mesmo destaque dos achados que passaram |
| R5 | Extração: F1 do modelo supera a regex nos campos **sem formato fixo** (logradouro, órgão, tipo de documento), e **não** a substitui nos campos com formato fixo | Onde a regex resolve, não usar modelo |
| R6 | JSON inválido ≤ 1% e campo inventado ≤ 1% na extração com LLM | Reprovado, o LLM não entra na camada FOL |

Os limiares de R3, R4, R5 e R6 são **propostas deste documento**, sem base empírica ainda; devem ser
revistos com a orientação antes de rodar. O de R2 vem do benchmark.

Reportar R4 com os mesmos dois números do experimento de simulação (correlação **e** amplitude),
porque inverter o sinal sem reduzir a amplitude só troca quem paga.

## 5. Ameaças à validade

- Os números de embedding do benchmark são de terceiros e de outro domínio (o FaqBacen é FAQ
  institucional, não documento cadastral); só o gold set próprio decide.
- Gold set pequeno: diferenças abaixo de ~1 p.p. são empate.
- Se o corpus for sintético, o ganho do RAG fica condicionado ao gerador e não generaliza.
- A licença lida do metadado do Hub não basta: abrir o `LICENSE` e conferir o modelo-base antes
  de adotar (caso Gervásio, benchmark §2).
