# Correções a levar à proposta PIDTI

A proposta (`Proposta_PIDTI_RAG_Bayesiano2.pdf`) é um PDF e não é editada neste repositório. Este
documento lista, com o trecho de origem, o que ficou **incompatível com o que a pesquisa
estabeleceu** e a redação sugerida, para decisão do coordenador. Nada aqui altera a proposta
submetida.

Os trechos citados foram lidos no PDF em 25/11/2026. Os fatos sobre licenças e resultados vêm de
`CLAUDE.md`, de `relatorios/Benchmark_Modelos_HuggingFace.md` e do relatório técnico.

## 1. Incompatibilidades que precisam de decisão

| # | Trecho da proposta | Problema | Redação sugerida |
|---|---|---|---|
| 1 | §6.1: "utilizará exclusivamente tecnologias de código aberto (Open Source)" e §6.4: stack com "SDV (Synthetic Data Vault)" | O SDV está sob Business Source License 1.1, que não é aprovada pela OSI. As duas afirmações são incompatíveis | Retirar o SDV do stack. O gerador é um processo causal em `numpy` (ver `protocolo_experimental_v1.md` §3). Alternativa OSI, se for preciso: `synthcity` (Apache-2.0) |
| 2 | §6.3, Etapa 1: "Ollama + Llama-3/Mistral" | A licença Llama 3.x não é aprovada pela OSI e o download tem portão | "Ollama + modelos sob Apache-2.0 (por exemplo Ministral 3, Qwen3.5, Gemma 4)". Triagem por papel em `Benchmark_Modelos_HuggingFace.md` |
| 3 | §6.3, Etapa 1: "Digital Twins de dados cadastrais, calibrados estatisticamente pela PDAD/CODEPLAN" | Contradiz a regra do projeto: gerador **ajustado a dados** destrói a verificabilidade da calibração, que depende de conhecer os parâmetros verdadeiros | Descrever como "dados sintéticos gerados por mecanismo causal explícito, com parâmetros estipulados ou medidos em fontes oficiais, mas nunca ajustados por aprendizado" |
| 4 | §4.2 e §6.4: "motor bayesiano (PyMC)" | O modelo da etapa de agregação é conjugado e de forma fechada; `numpy`/scikit-learn bastam. PyMC só se justificaria para estimar `P(E \| ¬F, RA)` com incerteza (hierárquico) na fase D7 | Manter PyMC como **opcional da D7**, condicionado a essa necessidade, e dizer que a etapa já executada não o usa |
| 5 | §3, H3: prior calibrado com dados locais "supera modelos genéricos nacionais" | Testada por simulação e **reprovada**: prior condicionado à taxa observada da região piora Brier e ECE em 224/224 configurações (dupla contagem) | Reformular H3 para o que o resultado sustenta (ver §2 abaixo). Não apresentar o prior regional como contribuição |
| 6 | §5: "inédito no contexto local" e §6.2 sobre mitigação de vieses | A disparidade sem atributo protegido tem mecanismo já publicado (Akpinar, Lipton e Chouldechova, FAccT 2024, arXiv:2401.08788), e a predição seletiva calibrada em finanças também (FinAbstain, arXiv:2607.24875) | Posicionar como **aplicação e extensão** no DF, com granularidade intramunicipal e taxa de evento igualada por construção. Não reivindicar ineditismo do mecanismo |

## 2. Hipóteses: o que foi testado

Numeração e enunciados copiados da proposta. A numeração já foi invertida por engano em
documentos anteriores; ao citar pelo número, cite também o enunciado.

| | Enunciado (proposta) | Estado |
|---|---|---|
| H1 | A integração RAG-Bayesiana gera scores de suspeita mais calibrados e rastreáveis que modelos preditivos estáticos | **Não testada.** A etapa mede só a agregação bayesiana, sem RAG. Resultado parcial: o AdaBoost calibrado a posteriori chega perto do Naive Bayes (ECE mediano 0,0036 contra 0,0031), então a calibração, por si só, não distingue o Bayes de um modelo preditivo calibrado |
| H2 | A explicitação dos cálculos em linguagem natural aumenta a confiabilidade e reduz vieses contra populações vulneráveis | **Não testada.** Exige a camada XAI e estudo com usuários. A etapa mede o viés territorial de partida |
| H3 | Dados locais (CODEPLAN/GDF) para calibrar o prior superam modelos genéricos nacionais | **Reprovada** na simulação (224/224) |

Resultado que sobra e que a proposta poderia absorver: **não existe correção, no nível da
agregação de evidências, para a desigualdade produzida por qualidade desigual de dado**, e medir e
publicar a cobertura cadastral por RA é requisito de governança.

## 3. Referências a acrescentar

- Fellegi e Sunter (1969), "A theory for record linkage", JASA 64: base dos braços A, B e C.
- Akpinar, Lipton e Chouldechova (2024), FAccT, arXiv:2401.08788.
- Torres, Cheng e Huang (2026), FinAbstain, arXiv:2607.24875.

A lista completa e verificada contra as fontes está em
`relatorios/Relatorio_Benchmark_Estado_da_Arte.md`.

## 4. O que não precisa mudar

Arquitetura em quatro camadas, human-in-the-loop (o sistema ordena fila de revisão, não concede nem
nega crédito) e uso de FAISS e LangChain. O cronograma da proposta é por trimestre; a conciliação
dele com as datas dos épicos no Trello (D5 em 26/03/2027, D7 em 18/06/2027, D10 em 17/09/2027)
**não foi verificada** e fica para a revisão com a orientação.
