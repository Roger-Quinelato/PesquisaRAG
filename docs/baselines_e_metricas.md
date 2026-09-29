# Baselines e métricas

Card D2.T6 (issue #27). Define contra o que a abordagem bayesiana é comparada e como a comparação é
medida. A implementação está em `experimento/bracos.py` e `experimento/metricas.py`; este documento
fixa o **porquê** de cada escolha e os cuidados de interpretação.

## 1. A tarefa que está sendo medida

O sistema **não concede nem nega crédito**. Ele ordena uma fila de casos para revisão humana, e essa
fila tem capacidade limitada (*selective prediction*). O evento de interesse é a **fraude latente
F**, que não é observável. As inconsistências documentais são sinais ruidosos de F, não o próprio F.

Daí saem dois requisitos para qualquer métrica:

1. medir a **qualidade da ordenação sob orçamento**, e não a de um rótulo binário;
2. medir a **calibração**, porque o analista vai ler a probabilidade como probabilidade.

## 2. Baselines

Seis braços. Todos recebem as mesmas três evidências binárias (`status`, `endereço`, `valor`) e,
quando aplicável, a Região Administrativa (RA).

| Braço | Tipo | O que faz | Papel na comparação |
|---|---|---|---|
| `RULE_OR` | Regra binária | 1 se qualquer evidência dispara | Mostra que triagem sob orçamento exige escore. Um rótulo binário empata em massa |
| `RULE_CNT` | Regra ordinal | Nº de evidências / 3 | Baseline ordinal justo: é o que um analista faria sem modelo |
| `LOOKUP` | Tabela empírica | `P(F \| padrão das 3 flags)`, estimado nos dados | **Teto não paramétrico sem território.** Usa o rótulo latente, que não existe na prática |
| `A` | Fellegi-Sunter | Prior global + soma das log-razões de verossimilhança, com FPR global | **Baseline honesto.** Bayesiano, RA ignorada |
| `B` | Bayesiano, RA na verossimilhança | Como `A`, mas com `P(E_endereço \| ¬F, RA)` específico da região | Candidato a ganho de acurácia |
| `C` | Bayesiano, RA no prior | Prior = taxa observada de inconsistência na região | O padrão "natural" que se quer testar e que produz *redlining* |

### Por que estes e não outros

- **Comparar só contra regras simples é comparar contra um adversário fraco.** O baseline de
  referência é Fellegi-Sunter (`A`), o modelo clássico de *record linkage* com log-razão de
  verossimilhança por campo (a mesma família do Splink). Um ganho sobre `RULE_CNT` que não sobrevive
  contra `A` não é ganho.
- **`LOOKUP` é teto, não concorrente.** Ele responde a "quanta informação as três flags carregam,
  no máximo, sem território?". Se `A` empata com `LOOKUP`, a forma paramétrica não está perdendo
  nada, e é isso que se observa: diferença mediana de 0,059 p.p.
- **`C` está presente para ser reprovado ou aprovado com evidência**, não por hipótese. Ele
  implementa a hipótese H3 da proposta (calibrar o prior com dado local). Confira sempre o
  enunciado no PDF, porque a numeração já foi invertida por engano.

### Cuidados de interpretação

- **O ECE de `LOOKUP` é zero degenerado** (~4,4e−17). A tabela estima `P(F | padrão)` nos mesmos
  dados em que é avaliada. Nunca cite isso como vantagem de calibração.
- `LOOKUP` e `B` usam informação que o sistema real não tem: o rótulo latente e o FPR verdadeiro por
  RA, respectivamente. São **limites superiores** do que cada estratégia poderia entregar. No
  sistema real, `P(E | ¬F, RA)` teria de ser estimado, com erro.
- `RULE_OR` e `RULE_CNT` não são probabilidades. Entram em Brier e ECE só para completar a tabela;
  a comparação que importa para eles é a de precisão.

## 3. Métricas

### 3.1 Principal: precisão@top-k sob orçamento

Entre os `k·n` casos de maior escore, que fração tem F = 1. **k = 10%** (`K = 0.10`).

- Os empates são desfeitos **aleatoriamente** (`metricas.topk`, `np.lexsort` com ruído). Isso é
  essencial: com ordenação estável, um escore binário seria favorecido artificialmente pela ordem
  de chegada.
- A diferença entre braços é reportada em **pontos percentuais**, como **mediana sobre a grade**,
  com mínimo, máximo e contagem de configurações em que é positiva.

### 3.2 Calibração: Brier e ECE

| Métrica | Definição | Pergunta que responde |
|---|---|---|
| Brier | `mean((p − y)²)` | Acurácia probabilística agregada |
| ECE | Média ponderada, sobre **10 bins de largura igual** em [0, 1], de `\|freq. observada − p médio\|` no bin | "Quando o sistema diz 30%, acontece 30%?" |

As duas são reportadas juntas: Brier mistura calibração com discriminação, e ECE isola a
calibração.

### 3.3 Equidade: FPR entre inocentes por RA

Entre os casos **sem fraude** de cada RA, a fração enviada à revisão. Mede quem paga o custo do
falso positivo. A síntese sobre as 8 RAs é feita de dois modos, e **os dois são obrigatórios**:

| Síntese | O que diz |
|---|---|
| `corr(cobertura_r, FPR_r)` | A **direção**: negativa quer dizer que o ônus recai onde o cadastro é pior |
| amplitude `max_r FPR_r − min_r FPR_r` | O **tamanho** da disparidade, qualquer que seja a direção |

Inverter o sinal sem reduzir a amplitude só troca quem paga. Foi exatamente o que aconteceu com `B`,
cuja amplitude é o triplo da de `A`.

### 3.4 Métricas deliberadamente descartadas

| Métrica | Por que não |
|---|---|
| F1 / acurácia | Não medem uma fila ordenada sob orçamento e são insensíveis à calibração. Com o dataset legado, F1 = 1,000 era trivial |
| AUC-ROC | Integra sobre todos os limiares, inclusive os que o orçamento nunca usa |
| Paridade demográfica | Não há variável demográfica no modelo; a disparidade é territorial e vem da qualidade da fonte |

## 4. Como reportar

- **Manchete = mediana sobre a grade completa** (224 configurações na varredura, 48 na equidade).
  A configuração de referência (β = 0,55; π = 0,15; ruído = 0,16) aparece só como ilustração.
- Cada número publicado precisa de uma linha em `relatorios/ledger_numeros.md`.
- Dispersão entre sementes: as colunas `*_dp` de `varredura.csv` trazem o desvio-padrão entre as
  8 sementes.

## 5. Referências de código

| Item | Onde |
|---|---|
| Braços | `experimento/bracos.py` → `calcular` |
| Log-razão de verossimilhança | `experimento/bracos.py` → `log_lr` |
| Brier, ECE, top-k, FPR por RA | `experimento/metricas.py` |
| Testes das métricas | `tests/test_experimento.py` → `TestMetricas` |
