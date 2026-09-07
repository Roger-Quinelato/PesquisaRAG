# Onde o dado territorial deve entrar em um modelo bayesiano de triagem de inconsistências cadastrais

**Relatório técnico da etapa de agregação de evidência**
Pesquisa de Iniciação Científica — triagem explicável de inconsistências cadastrais e documentais
em análise de crédito no Distrito Federal e RIDE.

Este relatório sustenta, com tabelas, equações e contagens de suporte, o resumo submetido ao
Congresso de Iniciação Científica da UnB. Todos os números vêm de `relatorios/ledger_numeros.md`
e das tabelas de apoio em `relatorios/tabelas/`, que por sua vez apontam para os arquivos de
`resultados/`. A seção 6 registra o caminho de reprodução de cada um.

Duas advertências de escopo abrem o documento porque condicionam a leitura de tudo o que vem
depois. **A camada de recuperação de evidências (RAG) não foi implementada nem avaliada nesta
etapa**: o que está medido aqui é exclusivamente a camada de agregação probabilística, dadas as
evidências já extraídas. E **o sistema descrito não concede nem nega crédito**: ele ordena uma
fila de casos para revisão humana sob orçamento de analista, e todas as métricas foram escolhidas
para medir a qualidade dessa ordenação.

---

## 1. Introdução

A automação da análise de crédito enfrenta uma exigência que não é de acurácia, mas de
justificação. Um sistema que atribui suspeita a um processo precisa explicar por que a atribuiu,
em termos que um analista consiga revisar, contestar e responsabilizar. Um escore que sai de um
classificador opaco satisfaz a primeira exigência e falha na segunda. A proposta PIDTI em que
esta pesquisa se insere responde a isso com uma arquitetura em quatro camadas: recuperação de
evidências documentais em fontes oficiais, tipificação simbólica das inconsistências encontradas,
atualização bayesiana da probabilidade de suspeita e apresentação da trilha de auditoria. A
justificativa da decisão passa a ser o próprio cálculo, e não um texto acrescentado depois dele.

Antes de construir esse pipeline há uma questão anterior, e é ela o objeto desta etapa. A
proposta declara três hipóteses. A hipótese **H3** — *"o uso de dados locais (CODEPLAN/GDF) para
calibração do prior bayesiano supera modelos genéricos nacionais em relevância demográfica"* —
sustenta que calibrar a probabilidade inicial de suspeita com dados territoriais e socioeconômicos
locais produz um *prior* mais informativo do que um modelo nacional genérico. A hipótese **H2** —
*"a explicitação dos cálculos probabilísticos em linguagem natural aumenta a confiabilidade das
decisões, reduzindo vieses contra populações vulneráveis"* — promete que o sistema reduziria vieses
contra populações vulneráveis. As duas convivem mal. Um *prior* condicionado à Região
Administrativa eleva a suspeita basal de quem mora em determinadas regiões antes de qualquer
evidência sobre o caso individual, e registra essa elevação por escrito na mesma trilha de
auditoria que o projeto promete produzir. H3 e H2 apontam em direções opostas, e o documento
original não resolve o conflito porque não o enuncia.

Esta etapa transforma a contradição em desenho experimental. Se o dado territorial pode entrar no
modelo em dois lugares — no *prior*, deslocando a probabilidade basal da região, ou na
verossimilhança, ajustando o quanto cada evidência informa naquela região —, então a pergunta é
empírica e tem resposta mensurável:

> **Onde o dado territorial deve entrar em um modelo bayesiano de triagem — no *prior* ou na
> verossimilhança — e qual o efeito de cada escolha sobre a calibração, sobre a utilidade da fila
> de revisão e sobre a distribuição dos falsos positivos entre as Regiões Administrativas?**

A pergunta é respondida por simulação de mecanismo, contra uma referência não paramétrica honesta
e sob uma grade de sensibilidade ampla, com três critérios de aceitação declarados antes da
execução. Um dos três reprovou. Ele aparece neste relatório com o mesmo destaque dos dois que
passaram, na seção 3.6.

---

## 2. Metodologia

### 2.1 O mecanismo gerador

Cada caso é um par de solicitação de crédito e conjunto de conferências documentais. O evento de
interesse é a **fraude latente** `F`, não observável: nem nas bases públicas disponíveis nem no
histórico do analista existe um rótulo confiável de fraude cadastral. O que se observa são
**evidências ruidosas** — divergências entre o que o solicitante declarou e o que a fonte oficial
registra.

O gerador (`experimento/gerador.py`) especifica o processo causal completo:

**Fraude latente.** Para cada caso *i*,

$$F_i \sim \mathrm{Bernoulli}(\pi)$$

com π **idêntico em todas as Regiões Administrativas**. A Região Administrativa `r_i` é sorteada
uniformemente entre as oito do experimento e não influencia `F` por nenhum caminho.

**Evidências condicionadas à fraude.** Três evidências binárias — divergência de situação
cadastral, divergência de endereço e divergência de valor declarado, indexadas por
*j* ∈ {status, endereço, valor} — são geradas a partir de `F`:

$$E_{ij} \mid F_i = 1 \sim \mathrm{Bernoulli}(s_j), \qquad
  E_{ij} \mid F_i = 0 \sim \mathrm{Bernoulli}\big(f_j(r_i)\big)$$

com sensibilidades fixas em *s* = (0,65; 0,70; 0,60).

**O gradiente territorial.** A taxa de falso positivo é constante para status e valor,
`f_j = f_base`, e só a evidência de endereço depende da região:

$$f_{\text{endereço}}(r) = \min\big(f_{\text{base}} + \beta\,(1 - c_r),\; 0{,}95\big)$$

onde `c_r` é a **cobertura do cadastro territorial** da região *r* e β controla a inclinação do
gradiente. A justificativa substantiva é conhecida do território: em regiões com parcelamentos
não registrados e cadastro desatualizado, um endereço não localizado é evidência fraca de
irregularidade, porque a ausência de registro é o estado normal daquela base.

**O vetor de cobertura é estipulado, não medido.** `COBERTURA` em `gerador.py` vale
(0,97; 0,94; 0,90; 0,84; 0,76; 0,70; 0,62; 0,55) para Plano Piloto, Águas Claras, Guará,
Taguatinga, Gama, Sobradinho, Samambaia e Ceilândia. Nenhum desses valores foi medido no
Geoportal/SEDUH nem em qualquer outra fonte. São uma ordenação plausível, escolhida para produzir
um gradiente, e **toda afirmação territorial deste relatório é condicional a eles**. A varredura
de β é a defesa parcial contra essa escolha: se a direção do resultado sobrevive a β variando de
0,25 a 0,70, ela não depende da inclinação específica que foi estipulada. Não sobrevive, porém, à
hipótese de que a ordenação das regiões esteja errada. A observação é repetida na seção 3.5, onde
os números territoriais aparecem, e na seção 5.

**A consequência do desenho.** Como π é idêntico em todas as regiões por construção e nenhuma
variável demográfica, de renda ou de escolaridade existe no modelo, **qualquer disparidade
territorial observada nos resultados é necessariamente artefato da qualidade da fonte, jamais
característica da população.** Esse é o controle central do experimento e a razão de ele ser
informativo.

### 2.2 Por que simulação de mecanismo, e não gerador ajustado a dados

Três razões, em ordem de força.

Primeira: **a fraude é latente**. Não existe corpus rotulado de fraude cadastral em análise de
crédito no DF ao qual um gerador aprendido pudesse ser ajustado. O que existiria, na melhor
hipótese, seria um registro das inconsistências *detectadas* — que é o desfecho do sistema, não a
causa que ele tenta inferir.

Segunda: **avaliar calibração exige conhecer a probabilidade verdadeira**. A pergunta desta etapa
não é apenas qual arranjo ordena melhor, mas qual arranjo produz probabilidades que significam o
que dizem. Isso só é verificável quando se conhecem os parâmetros que geraram os dados. Um
gerador que aprende sua própria estrutura a partir de dados reais destrói essa referência e, com
ela, a possibilidade de verificar se o modelo recupera a verdade.

Terceira: **o experimento precisa do controle**. Fixar π idêntico entre regiões é o que permite
atribuir a disparidade observada à fonte e não à população. Nenhum dado observacional oferece
essa garantia, porque nele as duas explicações são inseparáveis.

Pelos mesmos motivos o experimento não usa scipy, sklearn, PyMC nem geradores baseados em GAN. As
dependências são `numpy` e `matplotlib`.

### 2.3 Os seis braços

Todos os braços recebem as mesmas evidências e produzem um escore em [0, 1]. O que muda é como o
escore é construído.

| Braço | Escore | O que representa |
|---|---|---|
| `RULE_OR` | `max_j E_j` | Regra binária: sinalizado se qualquer evidência divergir |
| `RULE_CNT` | `(Σ_j E_j) / 3` | Contagem de evidências — referência ordinal justa |
| `LOOKUP` | `P̂(F = 1 \| padrão de flags)` | Tabela empírica sobre os 8 padrões possíveis |
| `A` | Fellegi-Sunter com FPR global | RA ignorada |
| `B` | Fellegi-Sunter com FPR da região | **RA na verossimilhança** |
| `C` | Fellegi-Sunter com *prior* regional | **RA no *prior*** |

**A forma bayesiana.** Os três braços `A`, `B` e `C` compartilham o formato clássico de razão de
verossimilhança por campo, na tradição de Fellegi-Sunter (1969) para pareamento de registros. A
soma das log-razões de verossimilhança é

$$\log \mathrm{LR}(E) \;=\; \sum_{j} \left[ E_j \log\frac{s_j}{f_j} \;+\; (1 - E_j)
  \log\frac{1 - s_j}{1 - f_j} \right]$$

e o escore é a probabilidade posterior obtida somando essa quantidade ao logito do *prior*:

$$\hat{p} \;=\; \sigma\!\left( \log\frac{\pi_0}{1 - \pi_0} \;+\; \log \mathrm{LR}(E) \right),
  \qquad \sigma(x) = \frac{1}{1 + e^{-x}}$$

A evidência ausente contribui tanto quanto a presente — é o que distingue a razão de
verossimilhança de uma contagem de sinais. Os três braços diferem apenas em dois pontos:

- **`A`** usa `π₀ = π` e `f_j` global. O FPR global de endereço é `f_base + β(1 − c̄)`, com `c̄` a
  média das coberturas das oito RAs: é o que enxerga um modelo que não sabe de qual região o caso
  veio.
- **`B`** usa `π₀ = π` e `f_j = f_j(r)`, o FPR de endereço específico da região. O *prior*
  permanece uniforme; o que muda é o **peso** que a evidência de endereço recebe onde a fonte é
  ruim.
- **`C`** usa `f_j` global e `π₀ = τ_r`, a **taxa de inconsistência observada na região**,
  definida como a fração de casos daquela RA com pelo menos uma evidência positiva,
  `τ_r = média(max_j E_j | RA = r)`, truncada em [0,01; 0,99]. Este é o procedimento que um
  analista adotaria naturalmente, por ser a única taxa mensurável na ausência de rótulo de fraude.

**A referência.** `LOOKUP` estima `P(F = 1 | padrão de flags)` para cada um dos oito padrões
possíveis, diretamente sobre os dados avaliados, usando o rótulo latente. **Não é um competidor
implantável** — na prática o rótulo não existe. É o **teto não paramétrico**: mede toda a
informação que três flags binárias carregam sobre a fraude, sem território, sem forma funcional
imposta. Comparar as variantes bayesianas apenas contra regras simples seria escolher adversário
fraco; `LOOKUP` é a régua honesta.

### 2.4 Métricas

**Precisão@top-10% — a métrica principal.** O sistema não decide sobre concessão de crédito: ele
ordena uma fila de revisão humana com capacidade limitada. A medida relevante é portanto a
utilidade decisória sob orçamento: entre os 10% de casos com maior escore, que fração tem fraude
latente. Empates são desfeitos aleatoriamente (`np.lexsort` com ruído em `metricas.topk`) — isso
importa, porque um escore binário empata em massa e uma ordenação estável o favoreceria
artificialmente.

**Escore de Brier.** Erro quadrático médio da probabilidade prevista contra o rótulo,
`mean((p − y)²)`. Mede acurácia probabilística agregada.

**Erro de calibração esperado (ECE).** Média ponderada, sobre **10 bins de largura igual** em
[0, 1], do desvio absoluto entre a probabilidade média prevista e a frequência observada dentro
do bin. Responde a "quando o sistema diz 30%, acontece 30%?" — a pergunta que importa quando a
saída vai para um analista que precisa interpretar o número.

**FPR entre inocentes por RA — a métrica de equidade.** Entre os casos **sem fraude** de cada
Região Administrativa, a fração enviada à revisão humana. Mede quem paga o custo do falso
positivo. A síntese sobre as oito RAs é feita de dois modos: `corr(c_r, FPR_r)`, cujo sinal diz
se o ônus recai sobre as regiões de pior cadastro, e a **amplitude** `max_r FPR_r − min_r FPR_r`,
que diz o tamanho da disparidade independentemente da direção. Os dois são necessários: inverter
o sinal sem reduzir a amplitude apenas troca quem paga.

Note-se que F1 e acurácia foram deliberadamente abandonadas. Nenhuma das duas mede a qualidade de
uma fila ordenada sob orçamento, e ambas são insensíveis a calibração.

### 2.5 A grade de sensibilidade

| | |
|---|---|
| Ruído da evidência (`f_base`) | 14 níveis, `linspace(0,01; 0,40; 14)` |
| Gradiente territorial (β) | 0,25 / 0,40 / 0,55 / 0,70 |
| Prevalência de fraude (π) | 0,05 / 0,10 / 0,15 / 0,25 |
| **Configurações** | **14 × 4 × 4 = 224** |
| Por configuração | 8 sementes (`range(8)`) × 40.000 casos |
| Orçamento | `K = 0,10` |

A grade de equidade (`equidade.py`) usa três níveis de ruído (0,07 / 0,16 / 0,28) contra os
mesmos 4 β × 4 π, totalizando **48 configurações**, porque a métrica por RA exige acumular a
seleção de todas as sementes.

A **configuração de referência** é β = 0,55; π = 0,15; ruído = 0,16. Ela existe para as figuras e
para a tabela por RA, que só o arquivo de referência sustenta. **Sempre que aparecer neste
relatório, vem rotulada como ilustração.** Como se verá em 3.2 e 3.6, ela ora superestima, ora
subestima o efeito mediano da grade — motivo suficiente para nunca a apresentar como efeito
típico.

### 2.6 Os três critérios de aceitação pré-registrados

Declarados no plano **antes** da execução, verificados por `varredura.verificar` e por
`equidade.main`, com a regra explícita de que **achado reprovado sai do texto do resumo**:

**(i) Degradação por *prior* territorial.** `C` deve ser pior que `A` simultaneamente em Brier e
em ECE, em todas as configurações da grade.

**(ii) Direção da disparidade territorial.** Na configuração de referência e em toda a grade de
equidade, `corr(cobertura, FPR entre inocentes)` deve ser inferior a −0,50 para `RULE_CNT` (isto
é, a disparidade existe e é forte), **e deve ser maior ou igual a −0,10 para `B`** (isto é, mover
o território para a verossimilhança elimina a disparidade). O limiar de −0,10, e não de zero, foi
escolhido para tolerar correlação levemente negativa por ruído amostral.

**(iii) Ganho de utilidade de `B`.** `B` deve superar simultaneamente `A` e `LOOKUP` em
precisão@top-10%.

---

## 3. Resultados

### 3.0 Panorama

**Tabela 1 — Desempenho por braço sobre as 224 configurações.** Mediana da grade; o par
(mín; máx) delimita a grade inteira. Fonte: `relatorios/tabelas/resumo_por_braco.csv`.

| Braço | Precisão@10% (mediana) | (mín; máx) | Brier (mediana) | ECE (mediana) | Δ precisão vs. `LOOKUP` (mediana, p.p.) | Supera `LOOKUP` |
|---|---|---|---|---|---|---|
| `RULE_OR` | 0,2090 | (0,0583; 0,7942) | 0,4846 | 0,4846 | −31,29 | 0/224 |
| `RULE_CNT` | 0,5198 | (0,1401; 0,9972) | 0,1281 | 0,1640 | −0,87 | 6/224 |
| `LOOKUP` | 0,5325 | (0,1404; 0,9991) | 0,0692 | 0,0000 (degenerado) | — | — |
| `A` | 0,5322 | (0,1403; 0,9990) | 0,0692 | 0,0023 | −0,02 | 86/224 |
| `B` | **0,5459** | (0,1422; 0,9991) | **0,0689** | 0,0026 | **+0,67** | **213/224** |
| `C` | 0,5159 | (0,1316; 0,9991) | 0,1952 | 0,2934 | −0,65 | 23/224 |

![Figura 1 — Precisão sob orçamento, tamanho de efeito contra a tabela empírica e erro de calibração, ao longo do ruído da evidência.](../figuras/fig1_precisao_calibracao.png)

Duas leituras imediatas da Tabela 1 organizam o resto da seção. Na coluna de precisão, `LOOKUP`,
`A` e `B` são praticamente indistinguíveis, e a diferença entre eles é duas ordens de grandeza
menor que a distância de qualquer um deles para `RULE_OR`. Na coluna de ECE, `C` está sozinho em
outro patamar. O que separa os braços não é o uso de Bayes: é onde o território foi colocado.

### 3.1 A entrada de ECE zero da tabela empírica é degenerada e não é vantagem

Antes de qualquer comparação, uma linha da Tabela 1 precisa ser desativada. O ECE de `LOOKUP` é
0,000000 — na configuração de referência, 1,94 × 10⁻¹⁷, e no máximo 4,4 × 10⁻¹⁷ em toda a grade;
ou seja, zero até o erro de ponto flutuante. Isso **não** é evidência de que a tabela empírica
seja bem calibrada.

O mecanismo é circular por construção. `LOOKUP` estima `P(F | padrão)` como a frequência de
fraude observada dentro de cada um dos oito padrões, **nos mesmos dados em que é depois
avaliado**. O ECE compara, dentro de cada bin, a probabilidade média prevista com a frequência
observada. Como a previsão de cada padrão *é* a frequência observada daquele padrão, os dois
lados da subtração são a mesma quantidade e o resultado é zero por identidade algébrica, não por
qualidade de modelagem. Uma tabela ajustada em um conjunto e avaliada em outro não teria esse
comportamento.

Portanto: **a comparação honesta de calibração neste experimento é `A` contra `C`.** `LOOKUP`
continua servindo como teto de *precisão*, onde não há circularidade dessa natureza, mas seu ECE
não entra em nenhuma conclusão.

### 3.2 A variante bayesiana sem território não supera a tabela empírica

O primeiro resultado é negativo e é o mais instrutivo dos três.

**Tabela 2 — `A` − `LOOKUP` em precisão@top-10%, em pontos percentuais, sobre 224 configurações.**

| | mediana | mínimo | máximo |
|---|---|---|---|
| diferença com sinal | **−0,022 p.p.** | −0,297 p.p. | +0,272 p.p. |
| diferença em módulo | **0,059 p.p.** | 0,000 p.p. | 0,297 p.p. |

`A` supera `LOOKUP` em **86 das 224 configurações** — indistinguível de moeda honesta, e com
mediana com sinal negativa. O intervalo interquartílico da diferença é [−0,069; +0,048] p.p.,
inteiramente contido no ruído amostral: o desvio-padrão entre sementes da precisão de `A` na
configuração de referência é 0,0049, ou seja **0,49 p.p.**, cerca de oito vezes maior que a maior
diferença observada em toda a grade.

A interpretação correta é "`A` atinge o teto", não "`A` é ruim". Todo o aparato probabilístico,
aplicado a evidências cuja confiabilidade se supõe homogênea, apenas reproduz o que uma tabela de
oito células já entrega. O ganho da inferência bayesiana, neste problema, não vem da forma
funcional. Vem — se vier — de informação que a tabela não tem.

### 3.3 Mover o território para a verossimilhança melhora a precisão de forma consistente e modesta

Essa informação adicional é a confiabilidade regional da fonte.

**Tabela 3 — Ganho de `B` em precisão@top-10%, em pontos percentuais, sobre 224 configurações.**

| Comparação | mediana | mínimo | máximo | Suporte |
|---|---|---|---|---|
| `B` − `LOOKUP` | **+0,673 p.p.** | −0,134 p.p. | +2,956 p.p. | **213/224** |
| `B` − `A` | **+0,683 p.p.** | −0,113 p.p. | +2,997 p.p. | **216/224** |
| `B` > max(`A`, `LOOKUP`) | — | — | — | **210/224** |

Quartis de `B` − `LOOKUP`: [+0,246; +0,673; +1,110] p.p.

O efeito é **consistente em direção e modesto em tamanho**. Consistente porque 213 de 224
configurações da grade apontam no mesmo sentido; modesto porque a mediana é inferior a sete
décimos de ponto percentual, e porque o quartil inferior fica em um quarto de ponto percentual.
Dez das 11 configurações em que `B` não supera `LOOKUP` concentram-se nos cantos de ruído muito
baixo (`f_base` ∈ {0,01; 0,04; 0,10; 0,13}) ou de prevalência baixa (π ∈ {0,05; 0,10}); a
restante (`f_base` = 0,34; β = 0,25; π = 0,25) fica fora desses cantos. Em todas elas a diferença
é no máximo 0,134 p.p. — abaixo do desvio-padrão entre sementes. Não são contraexemplos
substantivos; são empates.

*Ilustração na configuração de referência (β = 0,55; π = 0,15; ruído = 0,16):* `B` − `LOOKUP` =
+1,756 p.p., mais que o dobro da mediana da grade. É exatamente o tipo de número que não deve ser
relatado como efeito típico, e por isso não é.

**Duas ressalvas acompanham obrigatoriamente este ganho.** Primeira: o número correto da
comparação precisa ser declarado. Contra a tabela empírica a mediana é **+0,67 p.p.**; contra `A`
é **+0,68 p.p.** O valor de +0,64 p.p. que circulou em versões anteriores da documentação do
projeto **não se reproduz em nenhum recorte** de `varredura.csv` — as médias, em vez das medianas,
dão +0,738 e +0,750. Segunda, e mais importante: **este ganho de acurácia não vem acompanhado de
ganho de equidade.** As seções 3.6 e 3.7 tratam disso.

![Figura 5 — Diferença de precisão contra a tabela empírica ao longo de β e de π.](../figuras/fig5_sensibilidade.png)

A Figura 5 mostra por que a direção sobrevive à varredura: em todos os oito painéis, a curva de
`B` fica acima de zero e a de `C` abaixo, ainda que a magnitude varie bastante entre células.

### 3.4 A regra binária é inservível para triagem sob orçamento — e o motivo é metodológico

`RULE_OR` tem precisão@top-10% mediana de **0,209**, contra 0,532 de `LOOKUP` e 0,546 de `B`. É o
pior dos seis braços em **224 de 224** configurações, e a margem mínima sobre ele, na grade
inteira e para o braço mais fraco entre os demais, é de +6,64 p.p.

| Braço | Δ contra `RULE_OR` (mediana, p.p.) | mín | máx | Vence `RULE_OR` |
|---|---|---|---|---|
| `RULE_CNT` | +29,67 | +6,64 | +49,83 | 224/224 |
| `LOOKUP` | +31,29 | +8,10 | +51,15 | 224/224 |
| `A` | +31,45 | +8,18 | +51,10 | 224/224 |
| `B` | **+32,17** | +8,39 | +52,91 | 224/224 |
| `C` | +29,75 | +7,06 | +48,87 | 224/224 |

O número é grande **por construção da métrica**, não por descoberta. Um escore binário empata em
massa, e o desempate aleatório converte a precisão no topo-10% em pouco mais que a prevalência de
fraude entre os casos sinalizados. O achado é metodológico e vale enunciá-lo assim: **triagem sob
orçamento exige escore, não rótulo.** Uma regra que apenas marca "suspeito" não informa por onde a
fila começa. Nada além disso deve ser extraído da comparação — em particular, ela não sustenta
afirmação alguma sobre qualidade de modelagem, e é por isso que a régua deste relatório é
`LOOKUP` e não `RULE_OR`.

Registro de consistência: em `RULE_OR`, Brier e ECE coincidem em 224/224 configurações. Não é
erro. Para um escore que só assume 0 e 1, as duas métricas colapsam na mesma quantidade.

### 3.5 O *prior* territorial degrada a calibração em toda a grade, sem exceção

O segundo resultado é categórico.

**Tabela 4 — `C` contra `A` em calibração, sobre 224 configurações.**

| | mediana | mínimo | máximo |
|---|---|---|---|
| `C` − `A` em Brier | **+0,1133** | +0,0011 | +0,5531 |
| `C` − `A` em ECE | **+0,2912** | +0,0152 | +0,7359 |
| razão Brier `C`/`A` | **2,43×** | 1,03× | 12,88× |
| razão ECE `C`/`A` | **129×** | 9,5× | 478× |

**`C` é pior que `A` em Brier em 224/224 configurações, em ECE em 224/224, e nas duas
simultaneamente em 224/224.** Nenhuma exceção na grade.

*Ilustração na configuração de referência:* ECE de `A` = 0,0024564 (desvio-padrão entre sementes
0,00066) contra ECE de `C` = 0,2255115 (desvio-padrão 0,00223), razão de 91,8×. Brier na mesma
célula: 0,0799 contra 0,1520, razão 1,90×. Note-se que aqui a referência **subestima** o efeito
mediano da grade, que é 129× em ECE.

![Figura 3 — Diagrama de confiabilidade dos quatro braços probabilísticos na configuração de referência.](../figuras/fig3_confiabilidade.png)

A Figura 3 mostra a forma da falha: as curvas de `LOOKUP`, `A` e `B` acompanham a diagonal de
calibração perfeita, enquanto a de `C` se afasta dela sistematicamente. O ECE anotado na figura
foi recomputado do zero, regerando as predições por caso e replicando o binning de
`metricas.ece`; bate com `varredura.csv` até o último bit, com diferença absoluta de 0,00 × 10⁰
para os quatro braços.

**O mecanismo é dupla contagem, não um defeito numérico.** A taxa `τ_r` que alimenta o *prior* de
`C` é a fração de casos da região com ao menos uma evidência positiva — produzida pelas **mesmas
evidências** que em seguida entram na verossimilhança. O mesmo sinal é contado duas vezes, e o
resultado é superconfiança sistemática — visível na Figura 3 como o afastamento persistente da
diagonal. A degradação portanto não desaparece com mais dados; é estrutural. **O *prior* territorial não é apenas
eticamente problemático — é estatisticamente incorreto.**

Isso responde diretamente à hipótese H3 da proposta — a do *prior* calibrado com dados locais —
na forma em que ela estava enunciada. Um
*prior* calibrado na taxa de inconsistência observada da região não é mais informativo: é
enviesado, de modo previsível e mensurável.

### 3.6 A discriminação territorial emerge sem nenhuma variável demográfica no modelo

O terceiro resultado é o mais relevante para política pública, e depende inteiramente do vetor de
cobertura **estipulado** descrito em 2.1 — a ordenação das regiões abaixo é uma hipótese de
trabalho, não uma medição.

**Tabela 5 — Fração de inocentes enviada à revisão humana, por Região Administrativa.**
*Configuração de referência (β = 0,55; π = 0,15; ruído = 0,16), média de 8 sementes.* **Cobertura
cadastral estipulada, não medida.** Fonte: `relatorios/tabelas/fpr_por_ra_referencia.csv`.

| Região Administrativa | Cobertura (estipulada) | `RULE_OR` | `RULE_CNT` | `LOOKUP` | `A` | `B` | `C` |
|---|---|---|---|---|---|---|---|
| Plano Piloto | 0,97 | 7,285% | 2,874% | 3,238% | 3,300% | 5,088% | 0,460% |
| Águas Claras | 0,94 | 7,631% | 3,021% | 3,425% | 3,401% | 5,212% | 0,473% |
| Guará | 0,90 | 7,904% | 3,398% | 3,413% | 3,441% | 5,329% | 1,462% |
| Taguatinga | 0,84 | 8,413% | 3,748% | 3,631% | 3,672% | 2,612% | 2,612% |
| Gama | 0,76 | 9,080% | 4,406% | 3,770% | 3,794% | 2,586% | 2,586% |
| Sobradinho | 0,70 | 9,304% | 4,602% | 4,041% | 4,157% | 2,640% | 5,617% |
| Samambaia | 0,62 | 9,881% | 5,125% | 4,282% | 4,273% | 2,587% | 7,556% |
| Ceilândia | 0,55 | 10,903% | 5,580% | 4,659% | 4,544% | 2,715% | 12,601% |
| **corr(cobertura, FPR)** | | −0,993 | **−0,997** | −0,988 | **−0,992** | **+0,801** | −0,946 |
| **amplitude (máx − mín)** | | 0,0362 | 0,0271 | 0,0142 | **0,0124** | 0,0274 | **0,1214** |

![Figura 2 — Inocentes enviados à revisão contra a cobertura cadastral da região.](../figuras/fig2_equidade_territorial.png)

A leitura é direta. A taxa de fraude é idêntica nas oito regiões por construção. O modelo não
contém renda, escolaridade, cor ou qualquer atributo demográfico. Ainda assim, em todos os braços
exceto `B`, quem mora onde o cadastro é pior recebe mais falso positivo, com correlação próxima
de −1. Na regra por contagem, o inocente de Ceilândia é encaminhado à revisão em 5,58% dos casos
contra 2,87% no Plano Piloto — razão de 1,94×. Sob o *prior* territorial, o efeito é amplificado
para 12,60% contra 0,46%, razão de **27,4×**.

Esse último número precisa vir com suas duas etiquetas sempre que aparecer: **configuração de
referência** e **cobertura estipulada**. Ele é de uma única célula da grade, e sua magnitude
depende diretamente de valores que ninguém mediu. O que sobrevive à grade inteira é o sinal
(3.7) e a amplitude (3.8).

Registro de anomalia verificada: em Taguatinga e Gama, `B` e `C` apresentam FPR **exatamente
igual** (0,026115 e 0,025862, iguais até a precisão de máquina). A verificação mostrou que as
seleções globais dos dois braços diferem em todas as 8 sementes, mas que dentro dessas duas RAs
os conjuntos selecionados coincidem — 431 e 364 indivíduos, os mesmos. É coincidência estrutural
do corte de top-10% sobre padrões de flag, não erro de escrita do arquivo.

### 3.7 Sinal da disparidade na grade completa — e a reprovação do critério (ii)

**Tabela 6 — `corr(cobertura, FPR entre inocentes)` sobre as 48 configurações da grade de
equidade.** Fonte: `relatorios/tabelas/equidade_por_braco.csv`.

| Braço | corr mediana | mín | máx | corr < 0 | corr < −0,5 | **corr ≥ 0** (inversão estrita) | **corr ≥ −0,10** (critério pré-registrado) |
|---|---|---|---|---|---|---|---|
| `RULE_OR` | −0,992 | −0,999 | −0,911 | **48/48** | 48/48 | 0/48 | 0/48 |
| `RULE_CNT` | −0,997 | −1,000 | −0,946 | **48/48** | 48/48 | 0/48 | 0/48 |
| `LOOKUP` | −0,992 | −0,999 | −0,705 | **48/48** | 48/48 | 0/48 | 0/48 |
| `A` | −0,993 | −1,000 | −0,617 | **48/48** | 48/48 | 0/48 | 0/48 |
| `B` | +0,437 | −0,970 | +0,931 | 18/48 | 11/48 | **30/48** | **33/48** |
| `C` | −0,938 | −0,995 | −0,788 | **48/48** | 48/48 | 0/48 | 0/48 |

A correlação negativa é **universal** para cinco dos seis braços: 48/48, sempre abaixo de −0,5.
A parte do critério (ii) que exigia `corr(RULE_CNT) < −0,5` passa sem margem para dúvida — a
disparidade existe, é forte e não depende de β nem de π.

**A parte do critério (ii) que exigia `corr(B) ≥ −0,10` reprovou.** `B` satisfaz esse limiar em
**33 das 48** configurações, e falha em 15. A reprovação é o resultado desta seção e o motivo de
o achado correspondente ter sido retirado do resumo submetido.

**Os dois números não são a mesma coisa e a distinção é o ponto.** Sob o critério pré-registrado,
que tolera correlação levemente negativa (`corr ≥ −0,10`), o suporte é **33/48**. Sob inversão
**estrita** de sinal (`corr ≥ 0`), o suporte é **30/48**. Escrever "`B` inverte o sinal em 33/48"
mistura o enunciado de um com a contagem do outro, e é impreciso. Onde este relatório citar um
dos dois, cita o rótulo do critério junto. Em **11 das 48** configurações a correlação de `B`
permanece **abaixo de −0,5**, ou seja, fortemente negativa: nesses casos `B` não apenas deixa de
corrigir a disparidade, ele a mantém no mesmo patamar dos braços que ignoram o território.

**As falhas não são aleatórias.** Dez das 18 configurações com correlação negativa caem em duas
faixas identificáveis em `relatorios/tabelas/equidade_corr_B_por_config.csv` — as oito restantes
ficam dispersas, com correlações mais próximas de zero:

- **ruído baixo com gradiente íngreme** (`f_base` = 0,07; β ≥ 0,40; π ≤ 0,10): correlação entre
  −0,71 e −0,97, as piores de toda a grade;
- **ruído alto com prevalência alta** (`f_base` = 0,28; β ≥ 0,55; π ≥ 0,15): correlação até −0,91.

Ou seja: `B` falha precisamente onde o gradiente territorial é mais acentuado e onde a fraude é
rara — as condições em que a correção de equidade seria mais necessária.

![Figura 4 — Sinal da correlação de B na grade β × π, por nível de ruído. Células reprovadas com borda.](../figuras/fig4_heatmap_beta_pi.png)

### 3.8 Inverter o sinal não reduz a disparidade: `B` é três vezes pior que `A` em amplitude

O resultado mais desconfortável fecha a seção. Ainda que `B` inverta o sinal da correlação na
maior parte da grade, ele **não reduz a desigualdade** — apenas a redistribui.

**Tabela 7 — Amplitude (máx − mín) do FPR entre inocentes sobre as 8 RAs, mediana nas 48
configurações.**

| Braço | mediana | mínimo | máximo |
|---|---|---|---|
| `LOOKUP` | 0,0168 | 0,0015 | 0,0503 |
| `A` | **0,0171** | 0,0018 | 0,0498 |
| `RULE_CNT` | 0,0266 | 0,0041 | 0,0651 |
| `RULE_OR` | 0,0299 | 0,0137 | 0,0752 |
| `B` | **0,0543** | 0,0046 | 0,1209 |
| `C` | 0,0882 | 0,0031 | 0,2275 |

A razão das medianas `B`/`A` é **3,17×**. A variante que move o território para a verossimilhança
espalha o custo do falso positivo entre as regiões **mais** do que a variante que simplesmente
ignora o território — apenas em outra direção. Trocar quem paga não é reduzir o que se paga.

*Ilustração na configuração de referência:* as amplitudes são menores (`A` = 0,0124;
`B` = 0,0274; razão 2,20×) — mais um caso em que a referência subestima o efeito típico da grade.
`C` permanece o pior braço em amplitude, com mediana 5,2 vezes a de `A`.

### 3.9 Veredito dos três critérios

**Tabela 8 — Critérios de aceitação declarados antes da execução.**

| Critério | Enunciado | Resultado | Veredito |
|---|---|---|---|
| **(i)** | `C` pior que `A` em Brier **e** em ECE, em toda a grade | 224/224 em Brier; 224/224 em ECE; 224/224 nas duas | **APROVADO** |
| **(ii-a)** | `corr(cobertura, FPR)` de `RULE_CNT` < −0,50 em toda a grade | 48/48 | **APROVADO** |
| **(ii-b)** | `corr(cobertura, FPR)` de `B` ≥ −0,10 em toda a grade | **33/48** sob o critério; 30/48 sob inversão estrita | **REPROVADO** |
| **(iii)** | `B` supera `A` **e** `LOOKUP` em precisão@top-10% | 210/224; mediana +0,673 p.p. contra `LOOKUP` | **APROVADO** |

O critério (ii-b) foi declarado com a mesma antecedência e a mesma seriedade dos outros três, e
reprovou. A consequência foi aplicada: a hipótese de que mover o território para a verossimilhança
reconciliaria H3 com H2 **foi retirada do resumo submetido**, e `B` não é apresentado como solução
de equidade em nenhum documento do projeto. Ele pode ser reivindicado para ganho de acurácia
(3.3), desde que a ressalva de robustez de 3.7 e 3.8 venha declarada junto.

---

## 4. Conclusão

**A posição do dado territorial no modelo importa mais do que o emprego da inferência bayesiana
em si.** É a síntese do experimento, e cada uma de suas três partes tem suporte próprio.

Aplicar Bayes a evidências tratadas como homogêneas não produz ganho mensurável: `A` e `LOOKUP`
são estatisticamente indistinguíveis, com mediana de −0,022 p.p. e suporte de 86/224 — moeda
honesta. Colocar o território no *prior* degrada a calibração de forma robusta, em 224/224
configurações, por um mecanismo de dupla contagem que não desaparece com mais dados, e concentra
o custo do falso positivo nas regiões de cadastro precário. Colocar o território na
verossimilhança melhora modestamente a utilidade da fila — mediana de +0,67 p.p. contra a tabela
empírica, com suporte de 213/224 —, mas **não constitui solução de equidade**: inverte o sinal da
correlação em 30/48 configurações sob o critério estrito, falha sob gradiente íngreme com fraude
rara **e também sob ruído alto com prevalência alta**, e amplia a amplitude da disparidade a
3,17 vezes a da variante que ignora o território.

A implicação prática é desconfortável, e converge com o que outra etapa do mesmo grupo já havia
observado em domínio inteiramente distinto — vigilância de arboviroses no DF —, onde a maior
parte das configurações de modelo não superou uma referência simples e o obstáculo se revelou ser
a qualidade do dado, não a escolha do método. Aqui vale a mesma forma de conclusão, com um
enunciado mais forte:

> **Não existe correção, no nível da agregação de evidências, para a desigualdade produzida por
> qualidade desigual de dado.**

Enquanto a cobertura do cadastro territorial variar entre as Regiões Administrativas, qualquer
sistema que use endereço como evidência penalizará quem mora onde o registro é pior — **inclusive
os sistemas construídos para serem neutros**. O experimento mostra isso da forma mais limpa
possível: taxa de fraude idêntica por construção, nenhuma variável demográfica no modelo, e a
disparidade emerge de todo modo, em 48/48 configurações, para cinco dos seis braços.

O corolário é de governança, não de engenharia. **Medir e publicar a cobertura cadastral por
Região Administrativa deixa de ser detalhe técnico e passa a ser requisito** para qualquer
aplicação de análise de risco no território do Distrito Federal. Sem esse dado, nem sequer é
possível saber o quanto um sistema está distribuindo desigualmente o ônus da revisão — que é
exatamente a situação em que este experimento se encontra, e que a seção seguinte declara.

Duas recomendações operacionais decorrem diretamente dos resultados. Primeira: **não condicionar
o *prior* à taxa de inconsistência observada da região**, em nenhuma variante do sistema. É a
recomendação mais firme deste relatório, com 224/224 de suporte. Segunda: se `B` for adotado pelo
ganho de acurácia, **auditar a distribuição do FPR entre inocentes por região como métrica de
primeira classe**, com a mesma periodicidade da métrica de precisão — porque o ganho de acurácia
e a disparidade territorial se movem de forma independente, e o primeiro não é evidência sobre a
segunda.

---

## 5. Limitações

As limitações abaixo delimitam o que pode ser afirmado. Duas delas já apareceram no corpo do
texto, no ponto exato em que os números que elas condicionam foram apresentados.

**O estudo é de simulação.** As magnitudes relatadas são consequência dos parâmetros adotados.
Sensibilidades fixadas em (0,65; 0,70; 0,60), oito RAs, três evidências binárias e casos
independentes são um modelo do problema, não o problema. **Apenas as direções, verificadas na
grade de sensibilidade completa, devem ser lidas como resultado** — e é por isso que cada efeito
neste relatório vem com sua contagem *n/N*. Um número como "razão de 27,4×" não é uma estimativa
do mundo; é o comportamento de um mecanismo conhecido sob parâmetros escolhidos.

**O vetor de cobertura cadastral é estipulado, não medido.** Já declarado em 2.1 e repetido em
3.6, onde os números territoriais aparecem. Nenhum valor de `COBERTURA` foi obtido do
Geoportal/SEDUH ou de qualquer fonte oficial: a ordenação das oito RAs é uma hipótese de
trabalho. Toda afirmação territorial deste relatório — as Tabelas 5, 6 e 7 e as Figuras 2 e 4 —
é condicional a ela. A varredura de β protege contra a inclinação estipulada, não contra uma
ordenação equivocada das regiões. **Obter esse dado real é a pendência prioritária da pesquisa**,
e é o maior ganho por esforço disponível: transformaria o resultado territorial de demonstração
de mecanismo em estimativa sobre o DF.

**A camada de recuperação de evidências não foi implementada nem avaliada.** Esta etapa mede a
agregação probabilística isoladamente, assumindo as evidências como dadas. Nada neste relatório
sustenta afirmação sobre o desempenho de RAG, sobre qualidade de recuperação em fontes oficiais
ou sobre a integração entre as duas camadas. Isso constitui a fase subsequente.

**Não há intervalo de confiança construível a partir dos resultados persistidos.** Os arquivos de
`resultados/` guardam apenas a **média** e o **desvio-padrão** entre as 8 sementes por célula; os
valores por semente não são gravados. Não é possível construir intervalo para nenhuma das
medianas de grade, nem erro-padrão da mediana, nem teste de significância, sem reexecutar
`varredura.py` com escrita por semente. **Nenhum número deste relatório vem com p-valor, e nenhum
deve receber um por interpolação.** As contagens *n/N* são a medida de robustez disponível, e é
essa a razão de o relatório insistir nelas. Limitação análoga vale para as correlações de
`equidade.csv`: cada `corr` é calculada sobre a média das 8 sementes, com n = 8 RAs, e o arquivo
não guarda dispersão amostral da correlação.

**As métricas por RA existem apenas na configuração de referência.** `varredura.py` só acumula o
FPR por região quando β, π e ruído coincidem com a referência, de modo que `fpr_por_ra.csv` cobre
uma única célula da grade. A Tabela 5 e a razão de 27,4× são, portanto, pontuais por limitação do
arquivo e não por escolha de apresentação. Da métrica territorial, apenas o **sinal** (Tabela 6)
e a **amplitude** (Tabela 7) sobrevivem à grade completa.

**A comparação contra `RULE_OR` não é um tamanho de efeito.** Como registrado em 3.4, a distância
de 29 a 32 pontos percentuais decorre do desempate aleatório sobre um escore binário. Serve como
argumento metodológico sobre o que triagem sob orçamento exige, e não como medida de qualidade
relativa de modelagem.

---

## 6. Reprodutibilidade

**Ambiente.** Windows 11, PowerShell. Dependências: `numpy` e `matplotlib` apenas. O experimento
é determinístico por semente: duas execuções produzem CSVs idênticos, e as figuras do relatório
produzem PNGs de hash SHA-256 idêntico.

**Comandos.** Da raiz do repositório (`C:\Pesquisa_RAG`), em ordem, tempo total aproximado de
8 minutos:

```powershell
python experimento/varredura.py      # -> resultados/varredura.csv, resultados/fpr_por_ra.csv
python experimento/equidade.py       # -> resultados/equidade.csv
python experimento/figuras.py        # -> figuras/fig1_*.png, fig2_*.png
python experimento/figuras_relatorio.py   # -> figuras/fig3_*.png, fig4_*.png, fig5_*.png
```

`varredura.py` imprime, ao final, o veredito dos critérios (i), (ii) na configuração de referência
e (iii). `equidade.py` imprime o veredito de (ii) na grade de 48 configurações — é ali que a
reprovação de (ii-b) aparece na saída do console.

**Sementes.** `range(8)`, isto é, `np.random.default_rng(0)` a `default_rng(7)`, em ambos os
scripts. Cada semente gera 40.000 casos independentes por configuração.

**Codificação dos arquivos.** Os CSVs de `resultados/` e de `relatorios/tabelas/` usam vírgula
como delimitador e UTF-8 **sem** BOM: leia com `encoding="utf-8"`. Ler `fpr_por_ra.csv` com outra
codificação corrompe "Águas Claras" e "Guará". Já os datasets da raiz do repositório
(`dataset_sintetico_v2.csv`) usam `;` e UTF-8 **com** BOM: `encoding="utf-8-sig"`.

**Origem de cada afirmação.**

| Seção | Afirmação | Arquivo e recorte |
|---|---|---|
| 3.0 | Tabela 1 | `relatorios/tabelas/resumo_por_braco.csv` |
| 3.1 | ECE de `LOOKUP` degenerado | `varredura.csv`, `ece_media`, `braco=="LOOKUP"`; mecanismo em `bracos.lookup` |
| 3.2 | `A` − `LOOKUP` | `varredura.csv`, `prec_media`, junção por `(f_base, beta, pi)` |
| 3.3 | `B` − `LOOKUP` e `B` − `A` | `varredura.csv`, `prec_media`, mesma junção |
| 3.4 | `RULE_OR` contra os demais | `varredura.csv`, `prec_media`, mesma junção |
| 3.5 | `C` contra `A` em Brier e ECE | `varredura.csv`, `brier_media` e `ece_media`; mesmo teste de `varredura.verificar`, critério (i) |
| 3.6 | FPR por RA | `resultados/fpr_por_ra.csv`, cópia em `relatorios/tabelas/fpr_por_ra_referencia.csv` |
| 3.7 | Sinal da correlação na grade | `resultados/equidade.csv`, colunas `corr_<braco>`; sínteses em `equidade_por_braco.csv`, caso a caso em `equidade_corr_B_por_config.csv` |
| 3.8 | Amplitude da disparidade | `resultados/equidade.csv`, colunas `amplitude_<braco>` |
| 3.9 | Vereditos | saída de console de `varredura.py` e `equidade.py` |

**Verificação independente do ECE.** Os valores de ECE da configuração de referência foram
recomputados do zero em `experimento/figuras_relatorio.py`, regerando as predições por caso com
`Params(pi=0.15, f_base=0.16, beta=0.55)`, `N = 40.000`, sementes `range(8)`, e replicando o
binning de `metricas.ece`. A diferença absoluta contra `varredura.csv` é 0,00 × 10⁰ para
`LOOKUP`, `A`, `B` e `C`.

**Auditoria dos números.** `relatorios/ledger_numeros.md` registra, para cada número deste
relatório, o arquivo, a coluna e o filtro que o reproduzem, além de uma seção explícita com os
números que **não** puderam ser sustentados. Este relatório não introduz nenhum número que não
esteja no ledger.

---

*Todos os identificadores e dados deste estudo são sintéticos. Nada aqui deve ser usado para
qualquer decisão real de crédito.*
