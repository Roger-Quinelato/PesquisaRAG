# Protocolo experimental v1

Card D2.T7 (issue #28). Consolida o desenho do experimento de simulação: hipóteses, variáveis,
cenários, sementes, métricas e critérios de comparação. Registra o protocolo **como foi executado**,
para que a versão v2 (com RAG e dados reais) parta de uma base explícita.

Documentos relacionados: [`baselines_e_metricas.md`](baselines_e_metricas.md) (D2.T6) e
[`protocolo_versionamento.md`](protocolo_versionamento.md) (D1.T5). O relatório técnico com os
resultados está em `relatorios/Relatorio_Tecnico_RAG_Bayesiano.md`.

## 1. Pergunta e escopo da v1

**Onde o dado territorial deve entrar num modelo bayesiano de triagem de inconsistências
cadastrais: no prior, na verossimilhança ou em nenhum dos dois?**

Fora do escopo da v1, e pendente para as próximas versões:

- o módulo RAG, que na v1 é substituído por evidências binárias geradas diretamente (D5);
- dados reais: a cobertura cadastral por RA é **estipulada**, não medida (D3.T1, D3.T2);
- a camada de explicação em linguagem natural (D9).

## 2. Hipóteses

Enunciados **copiados da proposta PIDTI** (seção 3). A numeração já foi invertida por engano em
documentos anteriores; ao citar pelo número, cite também o enunciado.

| | Enunciado (proposta) | O que a v1 testa |
|---|---|---|
| **H1** | A integração RAG-Bayesiana gera scores de suspeita mais calibrados e rastreáveis que modelos preditivos estáticos. | Só a parte **bayesiana** (sem RAG): calibração e precisão de `A`/`B` contra regras e contra a tabela empírica |
| **H2** | A explicitação dos cálculos probabilísticos em linguagem natural aumenta a confiabilidade das decisões, reduzindo vieses contra populações vulneráveis. | **Não testada.** Exige a camada XAI e um estudo com usuários. A v1 mede o viés territorial *de partida*, antes de qualquer explicação |
| **H3** | O uso de dados locais (CODEPLAN/GDF) para calibração do prior bayesiano supera modelos genéricos nacionais em relevância demográfica. | **Testada:** braço `C` (dado regional no prior) contra `A` (prior global) |

A formalização das hipóteses em variáveis operacionais para as versões seguintes é o card D2.T5
(#26).

## 3. Mecanismo gerador

Processo causal explícito, em `experimento/gerador.py`:

1. RA sorteada uniformemente entre 8 regiões, cada uma com uma cobertura cadastral `c_r`
   (0,97 no Plano Piloto até 0,55 em Ceilândia; valores **estipulados**).
2. Fraude latente `F ~ Bernoulli(π)`, **com π idêntico em todas as RAs**. Esse é o controle do
   experimento.
3. Três evidências `E_j` geradas a partir de `F`:
   - `P(E_j = 1 | F = 1) = s_j`, com `s = (0,65; 0,70; 0,60)`;
   - `P(E_j = 1 | F = 0) = f_base` para `status` e `valor`;
   - `P(E_endereço = 1 | F = 0, RA = r) = f_base + β·(1 − c_r)`, ou seja, o falso positivo de
     endereço cresce onde o cadastro é pior.

Consequência do desenho: como a taxa de fraude é igual por construção, **qualquer disparidade
territorial nos resultados é artefato da qualidade da fonte, nunca da população**.

Por que simulação de mecanismo, e não um gerador ajustado a dados: a calibração só pode ser
verificada se os parâmetros verdadeiros forem conhecidos. Pelo mesmo motivo, SDV, GANs e PyMC
estão fora da v1. A proposta lista PyMC no stack, mas o modelo é conjugado e fechado, e `numpy`
basta.

## 4. Variáveis

| Tipo | Variável | Valores |
|---|---|---|
| **Independente** | Braço (onde e se a RA entra) | `RULE_OR`, `RULE_CNT`, `LOOKUP`, `A`, `B`, `C` |
| **Fatores da grade** | Ruído das evidências `f_base` | 14 níveis, `np.round(np.linspace(0.01, 0.40, 14), 4)` |
| | Gradiente territorial β | 0,25 / 0,40 / 0,55 / 0,70 |
| | Prevalência π | 0,05 / 0,10 / 0,15 / 0,25 |
| **Controles** | π igual entre RAs; sensibilidades `s` fixas; vetor de cobertura fixo; orçamento fixo | — |
| **Dependentes** | Precisão@top-10%, Brier, ECE, FPR entre inocentes por RA (correlação e amplitude) | ver D2.T6 |

## 5. Cenários, amostra e sementes

| | Varredura (`varredura.py`) | Equidade (`equidade.py`) |
|---|---|---|
| Grade | 14 ruídos × 4 β × 4 π = **224** | 3 ruídos (0,07 / 0,16 / 0,28) × 4 β × 4 π = **48** |
| Sementes | `range(8)` | `range(8)` |
| Casos por semente | 40.000 | 40.000 |
| Orçamento | `K = 0,10` | `K = 0,10` |
| Saída | `resultados/varredura.csv`, `resultados/fpr_por_ra.csv` | `resultados/equidade.csv` |

**Configuração de referência** (só para figuras e para a tabela por RA): β = 0,55; π = 0,15;
ruído = 0,16. Aparece sempre rotulada como ilustração, nunca como efeito típico.

A grade de equidade é menor porque a métrica por RA exige acumular as seleções de todas as sementes.

## 6. Critérios de aceitação (pré-registrados)

Declarados **antes** da execução e verificados automaticamente por `varredura.verificar` e
`equidade.main`. Regra: **achado reprovado sai do texto do resumo**.

| Critério | Condição | Grade |
|---|---|---|
| **(i)** Prior territorial degrada | `C` pior que `A` em Brier **e** em ECE | Todas as 224 |
| **(ii-a)** A disparidade existe | `corr(cobertura, FPR inocentes) < −0,50` para `RULE_CNT` | Referência e 48 |
| **(ii-b)** A verossimilhança corrige | `corr(cobertura, FPR inocentes) ≥ −0,10` para `B` | Referência e 48 |
| **(iii)** Ganho de utilidade de `B` | `B` supera `A` **e** `LOOKUP` em precisão@top-10% | Todas as 224 |

O limiar de −0,10 em (ii-b), e não zero, tolera correlação levemente negativa por ruído amostral.

## 7. Critérios de comparação

- **Unidade de comparação:** a configuração `(f_base, β, π)`, com a média das 8 sementes. As
  diferenças entre braços são pareadas por configuração.
- **Manchete:** mediana da diferença sobre a grade, com mínimo, máximo e a contagem de
  configurações em que a diferença é favorável (por exemplo, "positiva em 213/224").
- **Critério de dominância:** um braço domina outro quando é melhor em **todas** as configurações da
  grade. Esta é a forma do critério (i).
- **Equidade:** reportar sempre correlação **e** amplitude. Inverter o sinal sem reduzir a
  amplitude não conta como correção.
- Cada número publicado precisa de uma linha em `relatorios/ledger_numeros.md`.

## 8. Resultado da v1 (resumo)

Detalhes e números no relatório técnico e no ledger. Não reabrir sem um experimento novo.

| Critério | Veredito |
|---|---|
| (i) | **Passa em 224/224.** Condicionar o prior à taxa regional observada é dupla contagem (*double dipping*) e degrada Brier e ECE. **H3 é reprovada.** |
| (ii-a) | **Passa em 48/48.** Correlação de −0,997 na referência, sem nenhuma variável demográfica no modelo |
| (ii-b) | **Falha: 33/48.** A inversão estrita de sinal ocorre em 30/48, e a amplitude de `B` é o triplo da de `A` |
| (iii) | Ganho modesto: mediana de `B − LOOKUP` = +0,673 p.p., positiva em 213/224. `B` é ligeiramente pior que `A` em calibração |

## 9. Ameaças à validade

| Ameaça | Tratamento na v1 | Pendência |
|---|---|---|
| Cobertura cadastral estipulada | Varredura de β como defesa | Medir no Geoportal/SEDUH (D3.T1) |
| `B` e `LOOKUP` usam informação indisponível na prática | Tratados como limites superiores | Estimar `P(E \| ¬F, RA)` com erro na v2 |
| Evidências independentes dado F | Simplificação declarada | Introduzir correlação entre evidências na v2 |
| Evidências binárias, sem RAG | Fora do escopo da v1 | D5 |
| Mecanismo de sub-registro diferencial já publicado | Citar Akpinar, Lipton & Chouldechova (FAccT 2024) | Posicionar como aplicação/extensão |

## 10. Mudanças previstas para a v2

- Substituir as evidências sintéticas por evidências recuperadas pelo RAG, com ruído de recuperação.
- Cobertura cadastral medida, com o registro de proveniência previsto em D1.T5.
- Estimativa de `P(E | ¬F, RA)` em amostra separada da avaliação, eliminando o caráter de teto de `B`.
- Critérios de aceitação da v2 declarados neste diretório **antes** da execução, como
  `protocolo_experimental_v2.md`.
