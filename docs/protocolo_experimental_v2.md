# Protocolo experimental v2 (proposta, pré-registro)

Cards D2.T5 (hipóteses experimentais) e D2.T8 (revisão metodológica). Escrito em **25/11/2026,
antes de qualquer rodada da v2**, como `protocolo_experimental_v1.md` §10 e
`protocolo_versionamento.md` §3 exigem. Estado: **proposta, a revisar com a orientação**. Só vale
como pré-registro depois de revisado e commitado; alterar um critério depois de ver resultado não
é permitido, só registrar critério novo com data.

Todos os limiares marcados **[proposto]** são escolhas deste documento, sem base empírica, e devem
ser revistos antes de rodar. Nenhuma estimativa de tempo de execução aqui foi medida.

## 1. O que muda em relação à v1

A v1 (`protocolo_experimental_v1.md`) mediu só a agregação de evidências binárias sintéticas e
deixou cinco ameaças em aberto. A v2 ataca cada uma, uma por vez, para que o efeito de cada
mudança seja atribuível:

| Ameaça da v1 | Mudança na v2 | Parâmetro novo |
|---|---|---|
| Cobertura cadastral estipulada | Vetor medido (`matriz_qualidade_fontes.md`), ou, se a medição não existir, o vetor estipulado **continua rotulado como tal** e a v2 reporta isso | `COBERTURA` medida |
| `B` e `LOOKUP` usam informação que não existe na prática | `B_est`: `P(E \| ¬F, RA)` estimado numa amostra de calibração **separada da avaliação** | `n_cal` |
| Evidências independentes dado F | Correlação entre evidências por fator latente comum | `rho` |
| Evidências binárias geradas direto, sem RAG | Ruído de recuperação: cada evidência verdadeira é perdida com probabilidade `1 − recall`, e a perda depende da cobertura da RA | `recall`, `gamma` |
| Mecanismo de sub-registro já publicado | Citar e posicionar como aplicação (`correcoes_proposta_pidti.md`) | — |

**Não muda:** a fraude `F` com π idêntico em todas as RAs (é o controle), o orçamento de revisão
`K = 0,10`, as métricas (precisão@top-k, Brier, ECE, FPR entre inocentes por RA com correlação
**e** amplitude) e a regra de que achado reprovado sai do texto do resumo.

## 2. Hipóteses operacionalizadas

Enunciados copiados da proposta. Ao citar pelo número, cite também o enunciado.

| | Enunciado (proposta) | Operacionalização na v2 |
|---|---|---|
| **H1** | A integração RAG-Bayesiana gera scores de suspeita mais calibrados e rastreáveis que modelos preditivos estáticos | Calibração (ECE) do agregador bayesiano **contra o AdaBoost calibrado**, não contra o cru, com evidências vindas do módulo de recuperação com ruído. Rastreabilidade fica para a D9 e **não é medida aqui** |
| **H2** | A explicitação dos cálculos em linguagem natural aumenta a confiabilidade e reduz vieses contra populações vulneráveis | **Fora da v2.** Exige a camada XAI e estudo com usuários (D9). A v2 só mede o viés territorial de partida, agora incluindo o que entra pela recuperação |
| **H3** | Dados locais (CODEPLAN/GDF) para calibrar o prior superam modelos genéricos nacionais | Já reprovada na v1 (224/224). A v2 apenas **replica** com a cobertura medida; não reabre |

Distinção que a v1 ainda não fazia: o contra-exemplo honesto a H1 é o AdaBoost calibrado a
posteriori, que na v1 chegou perto do Naive Bayes (ECE mediano 0,0036 contra 0,0031). Se a v2 não
separar o agregador bayesiano dele, H1 não tem apoio, e isso deve ser dito.

## 3. Mecanismo gerador da v2

Módulo **novo**, `experimento/gerador_v2.py`. `gerador.py` não é alterado: os números da v1 só
continuam reproduzíveis se o gerador antigo permanecer intocado (`protocolo_versionamento.md`
§2.1). O dataset passa a `v3` e é identificado pela tupla (código, parâmetros, semente, n).

1. `F ~ Bernoulli(π)`, idêntico em todas as RAs. RA sorteada uniformemente, sem influenciar `F`.
2. **Correlação.** Um fator latente `Z_i ~ N(0,1)` por caso. A evidência `j` dispara quando
   `sqrt(rho)·Z_i + sqrt(1 − rho)·e_ij` cruza o limiar que dá a taxa marginal desejada, de modo
   que as marginais `s_j` e `f_j(r)` **não mudam** com `rho`. Só a dependência muda.
3. **Recuperação.** Dada a evidência verdadeira `E_ij = 1`, ela é recuperada com probabilidade
   `recall_r = recall · (1 − gamma · (1 − c_r))`. Com `gamma = 0` a recuperação é igual em todas as
   RAs; com `gamma > 0`, cai onde a cobertura é baixa. Evidência não recuperada vira 0.
4. Sensibilidades `s = (0,65; 0,70; 0,60)` e a forma de `f_endereço(r)` como na v1.

Teste de unidade obrigatório antes de rodar: com `rho = 0`, `recall = 1`, `gamma = 0` o
`gerador_v2` reproduz **bit a bit** o `gerador` da v1 para a mesma semente.

## 4. Braços

Os seis fechados e os doze treinados da v1 continuam, mais dois novos, sempre **no fim** das
tuplas (a ordem define o consumo do rng, ver `CLAUDE.md`):

- `B_EST`: como `B`, com `P(E_endereço \| ¬F, RA)` estimado numa amostra de calibração rotulada de
  tamanho `n_cal`, separada da avaliação, com suavização de Laplace (`alpha = 1`).
- `LOOKUP_CV`: tabela empírica ajustada em metade e avaliada na outra metade, para acabar com o
  ECE zero degenerado e com o "teto na própria amostra".

Para conter o custo, a v2 pode rodar apenas um subconjunto dos treinados: `A_NB`, `B_NB`, `D_PL`
e `E_PL` **[proposto]**. Se for assim, o subconjunto é declarado aqui antes de rodar.

## 5. Grade e sementes

| Fator | Níveis |
|---|---|
| Ruído `f_base` | 0,07 / 0,16 / 0,28 |
| Gradiente β | 0,25 / 0,55 / 0,70 **[proposto]** |
| Prevalência π | 0,05 / 0,15 / 0,25 **[proposto]** |
| Correlação `rho` | 0 / 0,2 / 0,4 **[proposto]** |
| Recall de recuperação | 1,0 / 0,85 / 0,70 **[proposto]** |
| Acoplamento `gamma` | 0 / 0,5 **[proposto]** |
| `n_cal` | 200 / 2.000 **[proposto]** |

A grade completa seria 3·3·3·3·3·2·2 = 1.458 configurações. É grande demais para a v1-style de
8 sementes e 40.000 casos com 18 braços. Opções, a decidir **antes** de rodar: fatorar em
experimentos de um fator por vez (as mudanças da §1 testadas separadamente, com os demais fixos
na referência), ou reduzir níveis. **Recomendação: um fator por vez**, porque preserva a
atribuição causal. Medir o tempo de uma configuração antes de fixar a grade.

Sementes: `range(100, 108)` **[proposto]**, distintas da v1 (`range(8)`), para que nenhum resultado
da v2 compartilhe fluxo aleatório com os da v1. Casos por semente: 40.000. Orçamento `K = 0,10`.

## 6. Critérios de aceitação (declarados antes de rodar)

Cada critério vale por experimento de um fator, sobre as configurações da grade daquele
experimento. Além da contagem n/N, reportar a contagem em que o **IC t pareado por semente**
(`experimento/intervalos.py`) exclui zero, porque a v1 não tinha intervalo.

| Id | Critério | Experimento |
|---|---|---|
| **V2-i** | **Replicação de H3:** `C` pior que `A` em Brier **e** ECE em todas as configurações | cobertura medida |
| **V2-ii** | **Disparidade existe:** `corr(cobertura, FPR inocentes) < −0,50` para `RULE_CNT` em todas | cobertura medida |
| **V2-iii** | **`B` sem oráculo:** `B_EST − A` em precisão@10% tem mediana > 0 e é positiva em mais da metade das configurações com `n_cal = 2.000`. Reportar também `B − B_EST` (custo de não ter o oráculo) | `n_cal` |
| **V2-iv** | **Equidade de `B_EST`:** `corr ≥ −0,10` em pelo menos 90% das configurações **[proposto]**. Na v1, `B` com oráculo atendeu 33/48 (69%); portanto o limiar é mais exigente que o resultado conhecido e pode reprovar, o que é informativo | `n_cal` |
| **V2-v** | **Dependência custa calibração:** ECE de `A` com `rho = 0,4` é maior que com `rho = 0` em pelo menos 90% das configurações **[proposto]** | `rho` |
| **V2-vi** | **A recuperação desigual entra pelo RAG:** com `gamma = 0,5`, a amplitude do FPR de `A` é maior que com `gamma = 0` em pelo menos 90% das configurações **[proposto]** | `gamma` |
| **V2-vii** | **H1 contra o contra-exemplo honesto:** ECE mediano de `A_NB` menor que o de `D_PL` com recuperação ruidosa (`recall < 1`) em mais da metade das configurações. Se **não** for, H1 não tem apoio e é relatado como tal | `recall` |
| **V2-viii** | **`LOOKUP_CV`:** precisão@10% de `A` ainda empata com `LOOKUP_CV` (|diferença mediana| < 0,1 p.p.), reproduzindo o achado "Bayes sem território não supera a tabela" fora da própria amostra | cobertura medida |

Regra de leitura: critério reprovado **não é reescrito**. O resultado entra no relatório com o
mesmo destaque dos aprovados. V2-iv e V2-vii são os que mais provavelmente reprovam e foram
escritos assim de propósito.

## 7. Reprodutibilidade e auditoria

- Cada número publicado ganha linha em `relatorios/ledger_numeros.md`, com arquivo, coluna e
  filtro; número que não se reproduz vai para a seção de não sustentados.
- Rodar o pipeline **duas vezes** e comparar os CSVs byte a byte; registrar a versão do
  scikit-learn (os braços treinados dependem dela).
- `resultados/varredura_sementes.csv` e `experimento/intervalos.py` são a base dos intervalos.
- O ambiente é o `.venv` com as versões de `requirements.txt` (ver `CONTRIBUTING.md`).

## 8. Ameaças à validade da v2

| Ameaça | Tratamento | Pendência |
|---|---|---|
| A cobertura medida é um proxy (regularidade fundiária, não achar o endereço) | Declarado em `matriz_qualidade_fontes.md` §1 | Validar com amostra de endereços reais se um dia houver acesso |
| `gamma` e `recall` são parâmetros inventados até haver módulo RAG real | Varridos, nunca tratados como estimativa | Substituir por valores medidos na D5/D6 |
| O fator latente `Z` é só uma forma de correlação | Declarado; outras estruturas ficam para depois | Comparar com dependência por par |
| Poucas sementes (8) | IC t e contagem n/N | Aumentar sementes onde o IC for largo |
| Grade grande | Experimentos de um fator por vez | Medir o tempo antes de fixar |
| Tudo continua sendo simulação | Só as direções valem, não os tamanhos | Gold set real na D6 (estratégia iv da proposta) |

## 9. Ordem de execução proposta

1. Revisar este documento com a orientação (D2.T8) e fechar os itens **[proposto]**.
2. Decidir 8 ou 33 RAs e medir a cobertura (`catalogo_fontes_locais.md`).
3. Implementar `gerador_v2.py` com o teste de equivalência bit a bit com a v1.
4. Medir o tempo de uma configuração e fixar a grade.
5. Rodar uma vez, depois uma segunda vez, e comparar os CSVs.
6. Preencher o ledger e escrever o relatório com os vereditos, aprovados ou não.
