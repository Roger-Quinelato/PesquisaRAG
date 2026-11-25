# Relatório Parcial 1 — esqueleto

Cards D4.T1 a D4.T5. Prazo do épico D4: 18/12/2026. **Esqueleto:** a estrutura está montada e as
seções com conteúdo já verificado estão preenchidas a partir do repositório. O que depende de
decisão humana, de dado que não existe ainda ou da rodada de verificação está marcado
**[A PREENCHER]** ou **[A CONFIRMAR]**. Nada aqui foi escrito além do que o repositório sustenta.

Regras do projeto que valem para este relatório: nenhum número entra sem linha em
`relatorios/ledger_numeros.md`; achado reprovado aparece com o mesmo destaque dos aprovados; a
cobertura cadastral é sempre rotulada como **estipulada**, enquanto não for medida; todos os dados
são sintéticos.

## 1. Identificação

| | |
|---|---|
| Projeto | Bayes, RAs e Viés: Influência da Localidade na Triagem de Crédito (PIDTI, RAG-Bayesiano para auditoria explicável de inconsistências cadastrais em análise de crédito no DF/RIDE) |
| Coordenador | Filipe Balduino Pires Fernandes |
| Estudantes | Roger Dias Quinelato e João Victor Rikio Enomoto |
| Instituição | ESETI/UnDF; apoio de UnDF e CNPq |
| Período | Primeiro trimestre (Trello: D1 a D4, até 18/12/2026) **[A CONFIRMAR com o cronograma oficial]** |
| Versão do código | **[A PREENCHER: hash do commit de `develop` usado]** |

## 2. Resumo

Esta etapa responde a uma pergunta anterior à construção do sistema: **onde o dado territorial
deve entrar em um modelo bayesiano de triagem, no prior ou na verossimilhança?** Por simulação de
um mecanismo causal com taxa de fraude idêntica nas RAs, mostrou-se que o prior regional degrada a
calibração em toda a grade (224/224), que a disparidade territorial emerge sem nenhuma variável
demográfica (48/48) e que mover o território para a verossimilhança melhora modestamente a
precisão, mas **não** resolve a equidade (critério pré-registrado: 33/48, reprovado). A camada RAG
**não foi implementada** nesta etapa.

Números e fontes: `relatorios/Relatorio_Tecnico_RAG_Bayesiano.md` e `relatorios/ledger_numeros.md`.
**[A CONFIRMAR]** contra a rodada de verificação (seção 9).

## 3. Atividades do trimestre, por épico (D4.T3)

Estado do quadro Trello em 25/11/2026, com a evidência no repositório.

| Épico | Prazo | Cards | Evidência |
|---|---|---|---|
| **D1** Ambiente e governança | 02/10 | T1, T2, T3, T4, T5, T6 concluídos | `CONTRIBUTING.md`, `docs/protocolo_versionamento.md`, `Dockerfile`, `requirements.txt`, uso de `.venv` com uv |
| **D2** Referencial e protocolo | 30/10 (**vencido**) | T6, T7 concluídos; T1, T2 com estudo escrito; T3, T4, T5, T8 abertos | `docs/baselines_e_metricas.md`, `docs/protocolo_experimental_v1.md`, `relatorios/Estudo_LxMLS_Day_*.md`, `docs/protocolo_experimental_v2.md` (proposta) |
| **D3** Base experimental | 27/11 | T3 a T7 e T9 concluídos; T1, T2 em rascunho; T8, T10 abertos | `experimento/`, `relatorios/`, `docs/catalogo_fontes_locais.md`, `docs/matriz_qualidade_fontes.md` |
| **D4** Relatório Parcial 1 | 18/12 | este documento | — |

**[A PREENCHER]** atividades que não deixam rastro no repositório: seminários (D2.T4, D3.T8),
reuniões, leituras (D2.T3). **[A PREENCHER]** datas reais de conclusão de D1 e D2, que estão
vencidos no quadro.

## 4. Revisão bibliográfica (D4.T1)

Base: `relatorios/Relatorio_Benchmark_Estado_da_Arte.md` (997 linhas, referências verificadas
contra as fontes). Síntese do que o relatório sustenta:

- Os identificadores antes suspeitos **existem** (BayesRAG, Bayesian RAG para QA financeiro,
  RuleRAG, SymRAG, NeuSym-RAG).
- **Duas alegações de ineditismo caíram na verificação e não devem ser reivindicadas:**
  calibração de posterior agregado sob predição seletiva (FinAbstain, arXiv:2607.24875) e
  disparidade sem atributo protegido (Akpinar, Lipton e Chouldechova, FAccT 2024, arXiv:2401.08788).
- O que resta de específico: qualidade da fonte afetando a *especificidade* de uma evidência,
  granularidade intramunicipal e taxa do evento igualada por construção. O achado sobre o prior é
  *double dipping* em Bayes empírico, que tem nome conhecido.

**[A PREENCHER]** consolidar em texto corrido, no formato exigido pelo relatório oficial.

## 5. Metodologia (D4.T2)

Fonte: `relatorios/Relatorio_Tecnico_RAG_Bayesiano.md` §2 e `docs/protocolo_experimental_v1.md`.

- **Mecanismo causal.** Fraude latente `F ~ Bernoulli(π)` com π igual em todas as RAs; três
  evidências ruidosas geradas de `F`; falso positivo da evidência de endereço crescente onde a
  cobertura do cadastro territorial é baixa.
- **Braços.** Seis fechados (`RULE_OR`, `RULE_CNT`, `LOOKUP`, `A`, `B`, `C`) e doze treinados
  (AdaBoost, Naive Bayes, AdaBoost calibrado). Os treinados usam split 50/50 e N efetivo ≈ 20.000
  contra 40.000 dos fechados.
- **Métricas.** Precisão@top-10%, Brier, ECE e FPR entre inocentes por RA (correlação **e**
  amplitude). F1 foi deliberadamente descartado.
- **Grade.** 224 configurações (14 ruídos × 4 β × 4 π) na varredura e 48 na equidade, com 8
  sementes de 40.000 casos.
- **Critérios pré-registrados.** (i) a (iii) para os seis braços e (iv) a (xiv) para os treinados,
  declarados antes de cada rodada.

## 6. Resultados preliminares (D4.T2)

Os números abaixo são os do relatório técnico e do ledger, **[A CONFIRMAR]** contra a rodada de
verificação da seção 9. A configuração de referência é só ilustração.

| Achado | Resultado | Veredito |
|---|---|---|
| (i) Prior regional (`C`) pior que `A` em Brier e ECE | 224/224 | Aprovado |
| (ii-a) Disparidade existe (`RULE_CNT`, corr < −0,5) | 48/48 | Aprovado |
| (ii-b) `B` corrige a disparidade (corr ≥ −0,10) | **33/48** | **Reprovado** |
| (iii) `B` supera `A` e `LOOKUP` | mediana +0,673 p.p. contra `LOOKUP`, positiva em 213/224 | Aprovado, ganho modesto |
| `A` contra `LOOKUP` | mediana −0,022 p.p., positiva em 86/224 | `A` empata com a tabela |
| Amplitude da disparidade | `B` é 3,17× a de `A` | `B` troca quem paga, não reduz |

**Braços treinados:** os resultados e vereditos (iv) a (xiv) estão no `CLAUDE.md`, mas **não têm
linha no `ledger_numeros.md`**, que cobre só os seis fechados. Incluí-los no ledger é pré-requisito
para citá-los neste relatório. **[A PREENCHER]**

Conclusão que o trimestre sustenta: **não existe correção, no nível da agregação de evidências,
para a desigualdade produzida por qualidade desigual de dado.**

## 7. Limitações (declaradas)

1. É simulação: valem as direções, não os tamanhos.
2. **A cobertura cadastral por RA é estipulada, não medida.** Tentativa de medir pelo sumário do
   IPE-DF não serviu (`docs/catalogo_fontes_locais.md` §1.1). Segue como pendência prioritária.
3. A camada RAG **não foi implementada nem avaliada**.
4. Sem intervalos de confiança nos números atuais: os valores por semente só passam a existir na
   próxima rodada completa (`resultados/varredura_sementes.csv`, `experimento/intervalos.py`).
5. H1 e H2 não foram testadas; H3 foi reprovada na simulação. Cite sempre o enunciado junto do
   número da hipótese.
6. A proposta PIDTI tem incompatibilidades com os resultados (`docs/correcoes_proposta_pidti.md`).

## 8. Próximos passos

- Medir a cobertura cadastral real (D3.T1/T2) e decidir 8 ou 33 RAs.
- Revisar e fechar o protocolo v2 com a orientação (`docs/protocolo_experimental_v2.md`, D2.T8).
- Fase RAG (D5, prazo 26/03/2027), conforme `docs/plano_d5_rag.md`.
- Corrigir a proposta nos itens de licença e de hipóteses.

## 9. Evidências e verificação (D4.T3, D4.T4)

| Item | Estado |
|---|---|
| Testes (`python -m unittest discover tests`) | 27 passam no `.venv` (numpy 2.5.0, scikit-learn 1.9.1) |
| Rodada completa duas vezes, CSVs idênticos | **[A PREENCHER]** resultado da verificação |
| Números do relatório contra a rodada | **[A PREENCHER]** |
| PRs do trimestre | #46, #48, #49, #50, #51, #53, #56, #57 |

## 10. Release r1 (D4.T5)

Fechar só depois de: rodada verificada, seções **[A PREENCHER]** resolvidas, revisão (D4.T4).
Procedimento em `docs/protocolo_versionamento.md` §6: PR de `develop` para `main`, tag anotada
`r1` no commit de merge e anexos da release. **Não executado.**
