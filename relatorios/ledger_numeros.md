# Ledger de números — triagem bayesiana com dado territorial

Produto de auditoria: cada número abaixo aponta para o arquivo, as colunas e o filtro que o
reproduzem. **A manchete de cada afirmação é a mediana sobre a grade completa.** A configuração
de referência (`beta=0.55`, `pi=0.15`, `f_base=0.16`) aparece sempre rotulada como ilustração,
nunca como efeito típico.

| | |
|---|---|
| Fontes | `resultados/varredura.csv` (224 configs × 6 braços), `resultados/equidade.csv` (48 configs), `resultados/fpr_por_ra.csv` (8 RAs, config de referência) |
| Codificação | `resultados/*.csv`: vírgula, UTF-8 **sem** BOM → `encoding="utf-8"` |
| Grade de `varredura.csv` | 14 ruídos (`np.round(np.linspace(0.01,0.40,14),4)`) × 4 β (0,25/0,40/0,55/0,70) × 4 π (0,05/0,10/0,15/0,25) = 224 |
| Grade de `equidade.csv` | 3 ruídos (0,07/0,16/0,28) × 4 β × 4 π = 48 |
| Por célula | 8 sementes × 40.000 casos; `*_media` é a média entre sementes, `*_dp` o desvio-padrão entre sementes |
| Orçamento | precisão@top-10% (`K = 0.10` em `varredura.py`) |
| Tabelas de apoio | `relatorios/tabelas/resumo_por_braco.csv`, `fpr_por_ra_referencia.csv`, `equidade_por_braco.csv`, `equidade_corr_B_por_config.csv` |

Filtro-base reutilizado abaixo (`ref`): `f_base==0.16 & beta==0.55 & pi==0.15`.

---

## 1. A (bayesiano sem território) não supera a tabela empírica

**Afirmação.** O braço `A` (Fellegi-Sunter com FPR global, RA ignorada) não entrega ganho de
precisão sob orçamento sobre `LOOKUP`, o teto não paramétrico das três flags sem território.

**Valor.** `A − LOOKUP`, precisão@top-10%, em pontos percentuais:

| | mediana | mínimo | máximo |
|---|---|---|---|
| diferença com sinal | **−0,022 p.p.** | −0,297 p.p. | +0,272 p.p. |
| diferença em módulo | **0,059 p.p.** | 0,000 p.p. | 0,297 p.p. |

**Suporte.** `A` supera `LOOKUP` em **86/224** configurações — indistinguível de moeda honesta.
A mediana com sinal é negativa. O intervalo interquartílico da diferença é [−0,069; +0,048] p.p.,
inteiramente dentro do ruído amostral (o desvio-padrão entre sementes da precisão de `A` na
referência é 0,0049, ou seja **0,49 p.p.**, oito vezes a maior diferença observada na grade).

**Origem.** `resultados/varredura.csv`, coluna `prec_media`; para cada uma das 224 chaves
`(f_base, beta, pi)`, `100*(prec_media[braco=="A"] − prec_media[braco=="LOOKUP"])`.

**Ressalva.** `LOOKUP` é um teto irreal: estima `P(F | padrão de flags)` usando o rótulo latente
nos próprios dados em que é avaliado (`bracos.lookup`). Não é um competidor implantável — é a
régua da informação que 3 flags binárias carregam sem território. A leitura correta é "A atinge o
teto", não "A é ruim".

---

## 2. B (território na verossimilhança) supera A e a tabela empírica — a mediana é +0,67 p.p.

**Afirmação.** Mover a RA para a verossimilhança melhora a precisão sob orçamento, de forma
consistente em direção e modesta em tamanho.

**Valor.** Em pontos percentuais de precisão@top-10%:

| | mediana | mínimo | máximo |
|---|---|---|---|
| `B − LOOKUP` | **+0,673 p.p.** | −0,134 p.p. | +2,956 p.p. |
| `B − A` | **+0,683 p.p.** | −0,113 p.p. | +2,997 p.p. |

Quartis de `B − LOOKUP`: [+0,246; +0,673; +1,110] p.p.

**Suporte.** `B > LOOKUP` em **213/224**; `B > A` em **216/224**; `B > max(A, LOOKUP)` em
**210/224**.

**Origem.** `resultados/varredura.csv`, `prec_media`, mesma junção por
`(f_base, beta, pi)` da afirmação 1.

**Correção do número esperado.** A tarefa pedia confirmação de uma mediana de **+0,64 p.p.**
Ela **não se reproduz**: `B − LOOKUP` dá **+0,673** e `B − A` dá **+0,683**. As médias (em vez de
medianas) são +0,738 e +0,750. Nenhuma leitura de `varredura.csv` produz 0,64. Usar **+0,67 p.p.
contra a tabela empírica** ou **+0,68 p.p. contra A**, declarando qual comparação está em jogo.

**Ressalva.** As 11 configurações em que `B` não supera `LOOKUP` concentram-se nos cantos de ruído
muito baixo (`f_base` ∈ {0,01; 0,04; 0,10; 0,13}) ou prevalência baixa (`pi` ∈ {0,05; 0,10}), e
lá a diferença é ≤ 0,134 p.p. — abaixo do desvio-padrão entre sementes. A lista é reproduzível em
`varredura.csv` pelo filtro `prec_media[braco=="B"] <= prec_media[braco=="LOOKUP"]` dentro de cada
chave `(f_base, beta, pi)`. **Este ganho de acurácia não vem acompanhado de ganho de
equidade** — ver afirmações 6 e 7.

*Ilustração na referência:* `B − LOOKUP` = **+1,756 p.p.** — mais que o dobro da mediana. É
exatamente o número que não deve ser relatado como efeito típico.

---

## 3. C (território no prior) é dominado por A em Brier e em ECE, sem exceção

**Afirmação.** Condicionar o prior à taxa de inconsistência observada da região degrada
calibração em toda a grade.

**Valor.**

| | mediana | mínimo | máximo |
|---|---|---|---|
| `C − A` em Brier | **+0,1133** | +0,0011 | +0,5531 |
| `C − A` em ECE | **+0,2912** | +0,0152 | +0,7359 |
| razão Brier `C/A` | **2,43×** | 1,03× | 12,88× |
| razão ECE `C/A` | **129×** | 9,5× | 478× |

**Suporte.** `C` pior que `A` em Brier: **224/224**. Em ECE: **224/224**. Nas duas
simultaneamente: **224/224**. Nenhuma exceção na grade.

**Origem.** `resultados/varredura.csv`, colunas `brier_media` e `ece_media`; contagem de chaves
`(f_base, beta, pi)` com `brier_media[C] > brier_media[A]` e `ece_media[C] > ece_media[A]`.
Mesmo teste executado por `varredura.verificar`, critério (i).

**Ressalva.** O mecanismo é dupla contagem, não um defeito numérico: em `bracos.calcular`,
`taxa_ra` é a média de `E.max(axis=1)` na região — produzida pelas mesmas evidências que depois
entram na verossimilhança. A degradação portanto não desaparece com mais dados; é estrutural.

*Ilustração na referência:* ECE de `A` = 0,00246 → ECE de `C` = 0,22551 (ver afirmação 9).

---

## 4. RULE_OR é inservível para triagem sob orçamento

**Afirmação.** A regra binária (`OR` das evidências) não ordena casos, e por isso perde para
todos os demais braços em precisão sob orçamento.

**Valor.** Precisão@top-10% de `RULE_OR`: mediana **0,209** (mín 0,058; máx 0,794).
Diferenças dos demais braços **contra** `RULE_OR`, em p.p.:

| braço | mediana | mínimo | máximo | vence RULE_OR |
|---|---|---|---|---|
| `RULE_CNT` | +29,67 | +6,64 | +49,83 | 224/224 |
| `LOOKUP` | +31,29 | +8,10 | +51,15 | 224/224 |
| `A` | +31,44 | +8,18 | +51,10 | 224/224 |
| `B` | **+32,17** | +8,39 | +52,91 | **224/224** |
| `C` | +29,75 | +7,06 | +48,87 | 224/224 |

**Suporte.** `RULE_OR` é o **pior dos seis braços em 224/224** configurações. A margem mínima
sobre ele, na grade inteira e para o braço mais fraco, é +6,64 p.p. — duas ordens de grandeza
acima do efeito discutido nas afirmações 1 e 2.

**Origem.** `resultados/varredura.csv`, `prec_media`, `braco=="RULE_OR"` contra cada outro braço,
mesma junção por `(f_base, beta, pi)`.

**Ressalva.** O número é grande **por construção da métrica**, não por descoberta: um score
binário empata em massa, e `metricas.topk` desfaz empates aleatoriamente (`np.lexsort` com ruído).
A precisão de `RULE_OR` no topo-10% é essencialmente a prevalência de fraude entre os casos
sinalizados. O achado é metodológico — *triagem sob orçamento exige score, não rótulo* — e não
uma comparação esportiva. Comparar apenas contra `RULE_OR` seria escolher adversário fraco;
por isso a régua deste ledger é `LOOKUP`.

Nota de consistência: em `RULE_OR`, `brier_media == ece_media` em **224/224** configurações. Não é
erro — para um score que só assume 0 e 1, as duas métricas colapsam na mesma quantidade.

*Ilustração na referência:* `RULE_OR` prec = 0,2525 contra `LOOKUP` 0,6766 e `B` 0,6941.

---

## 5. Correlação cobertura × falso positivo entre inocentes, na configuração de referência

**Afirmação.** Com taxa de fraude **idêntica em todas as RAs por construção** e nenhuma variável
demográfica no modelo, quem mora onde o cadastro é pior recebe mais falso positivo — em todos os
braços exceto `B`.

**Valor.** `corr(cobertura, FPR entre inocentes)` sobre as 8 RAs:

| braço | correlação | amplitude (máx−mín) |
|---|---|---|
| `RULE_OR` | −0,993 | 0,0362 |
| `RULE_CNT` | **−0,997** | 0,0271 |
| `LOOKUP` | −0,988 | 0,0142 |
| `A` | **−0,992** | 0,0124 |
| `B` | **+0,801** | 0,0274 |
| `C` | −0,946 | **0,1214** |

**Suporte.** n = 8 RAs, uma correlação por braço. **Esta é a configuração de referência, não a
grade** — a versão sobre a grade completa é a afirmação 6.

**Origem.** `resultados/fpr_por_ra.csv` (**ler com `encoding="utf-8"`**, senão "Águas Claras" e
"Guará" corrompem); `np.corrcoef(cobertura, coluna_do_braco)`. Reproduzido em
`relatorios/tabelas/fpr_por_ra_referencia.csv`.

**Ressalva.** O vetor `COBERTURA` em `gerador.py` é **estipulado, não medido** — toda esta
afirmação é condicional a ele. A varredura de β é a defesa parcial contra essa escolha.
Anomalia registrada: em Taguatinga e Gama, `B` e `C` têm FPR **exatamente igual** (0,026115 e
0,025862, iguais até a precisão de máquina). Recomputado: as seleções globais de `B` e `C` diferem
em todas as 8 sementes, mas **dentro dessas duas RAs os conjuntos selecionados coincidem**
(431 e 364 indivíduos, os mesmos). Coincidência estrutural do corte de top-10% sobre padrões de
flag, não erro de escrita do CSV.

---

## 6. Sinal da correlação na grade completa de equidade

**Afirmação.** A correlação negativa é universal para `RULE_CNT`, `A` e `C`. `B` inverte o sinal
na maior parte da grade, mas **não de forma robusta** — e falha exatamente onde mais importaria.

**Valor e suporte** (N = 48 configurações):

| braço | corr mediana | mín | máx | corr < 0 | corr < −0,5 | corr ≥ 0 | corr ≥ −0,10 (critério) |
|---|---|---|---|---|---|---|---|
| `RULE_OR` | −0,992 | −0,999 | −0,911 | **48/48** | 48/48 | 0/48 | 0/48 |
| `RULE_CNT` | −0,997 | −1,000 | −0,946 | **48/48** | 48/48 | 0/48 | 0/48 |
| `LOOKUP` | −0,992 | −0,999 | −0,705 | **48/48** | 48/48 | 0/48 | 0/48 |
| `A` | −0,993 | −1,000 | −0,617 | **48/48** | 48/48 | 0/48 | 0/48 |
| `B` | +0,437 | −0,970 | +0,931 | 18/48 | 11/48 | **30/48** | **33/48** |
| `C` | −0,938 | −0,995 | −0,788 | **48/48** | 48/48 | 0/48 | 0/48 |

**Origem.** `resultados/equidade.csv`, colunas `corr_<braco>`; contagens diretas sobre as 48
linhas. Tabela completa em `relatorios/tabelas/equidade_por_braco.csv`; caso a caso em
`equidade_corr_B_por_config.csv`. Figura: `figuras/fig4_heatmap_beta_pi.png`.

**Correção do número esperado.** O "33/48" está correto **sob o critério pré-registrado
`corr_B ≥ −0,10`** (o teste de `equidade.py`), que tolera correlação levemente negativa.
**Inversão estrita de sinal (`corr_B ≥ 0`) ocorre em 30/48.** Os dois números devem ser usados com
o rótulo do seu critério; escrever "inverte o sinal em 33/48" é impreciso. Em **11/48** a
correlação de `B` continua abaixo de −0,5, ou seja fortemente negativa.

**Ressalva — onde `B` falha.** As 18 falhas de sinal não são aleatórias, formam duas faixas:
- **ruído baixo com gradiente íngreme** (`f_base=0,07`, β ≥ 0,40, π ≤ 0,10): corr entre −0,71 e
  −0,97, as piores da grade;
- **ruído alto com prevalência alta** (`f_base=0,28`, β ≥ 0,55, π ≥ 0,15): corr até −0,91.

É a evidência que reprova `B` como solução de equidade. `B` pode ser reivindicado para acurácia
(afirmação 2), com esta ressalva declarada.

---

## 7. Amplitude da disparidade — B é três vezes pior que A

**Afirmação.** Inverter o *sinal* da correlação não reduz a disparidade: `B` espalha o custo do
falso positivo entre regiões **mais** que `A`, apenas em outra direção.

**Valor.** Amplitude (máx − mín) do FPR entre inocentes sobre as 8 RAs, mediana nas 48 configs:

| braço | mediana | mínimo | máximo |
|---|---|---|---|
| `LOOKUP` | 0,0168 | 0,0015 | 0,0503 |
| `A` | **0,0171** | 0,0018 | 0,0498 |
| `RULE_CNT` | 0,0266 | 0,0041 | 0,0651 |
| `RULE_OR` | 0,0299 | 0,0137 | 0,0752 |
| `B` | **0,0543** | 0,0046 | 0,1209 |
| `C` | 0,0882 | 0,0031 | 0,2275 |

**Suporte.** 48/48 configurações entram em cada mediana. `B/A` = **3,18×** na razão das medianas.

**Origem.** `resultados/equidade.csv`, colunas `amplitude_<braco>`; mediana, mínimo e máximo sobre
as 48 linhas.

**Confirmação do número esperado.** Os valores esperados (`A` ≈ 0,017; `B` ≈ 0,054)
**se confirmam**: 0,0171 e 0,0543.

**Ressalva.** Na configuração de referência isolada as amplitudes são menores (`A` = 0,0124,
`B` = 0,0274, razão 2,20×) — mais um caso em que a referência subestima o efeito típico. `C`
continua sendo o pior braço em amplitude, com mediana 5,2× a de `A`.

---

## 8. Ceilândia contra Plano Piloto na configuração de referência

**Afirmação.** Fração de **inocentes** enviados à revisão humana, nas duas RAs extremas da
cobertura estipulada (0,55 contra 0,97), com prevalência de fraude idêntica por construção.

**Valor.**

| braço | Plano Piloto (cob. 0,97) | Ceilândia (cob. 0,55) | diferença | razão |
|---|---|---|---|---|
| `RULE_CNT` | 2,874% | 5,580% | **+2,71 p.p.** | **1,94×** |
| `C` | 0,460% | 12,601% | **+12,14 p.p.** | **27,4×** |

Para contexto, os demais braços na mesma célula: `A` 3,300% → 4,544% (1,38×);
`B` 5,088% → 2,715% (0,53×, sinal invertido); `LOOKUP` 3,238% → 4,659% (1,44×).

**Suporte.** n = 1 configuração (a de referência), média de 8 sementes. **Este é o único bloco do
ledger que é intrinsecamente pontual** — `fpr_por_ra.csv` só existe para a referência.

**Origem.** `resultados/fpr_por_ra.csv`, linhas `Plano Piloto` e `Ceilândia`, colunas `RULE_CNT` e
`C`. Cópia em `relatorios/tabelas/fpr_por_ra_referencia.csv`.

**Ressalva.** Números de uma célula da grade; a versão defensável sobre a grade é a afirmação 7
(amplitude) e a 6 (sinal). A razão 27,4× de `C` é dramática e por isso perigosa: depende do vetor
`COBERTURA` estipulado e da célula escolhida. Se aparecer no texto, tem de vir com as duas
etiquetas — "configuração de referência" e "cobertura estipulada".

---

## 9. ECE de A e de C na configuração de referência

**Afirmação.** Na configuração de referência, o erro de calibração esperado de `C` é quase duas
ordens de grandeza maior que o de `A`.

**Valor.**

| braço | ECE (referência) | dp entre sementes |
|---|---|---|
| `A` | **0,0024564** | 0,00066 |
| `C` | **0,2255115** | 0,00223 |
| razão `C/A` | **91,8×** | — |

Brier na mesma célula: `A` 0,07990, `C` 0,15203 (razão 1,90×).

**Suporte.** n = 1 configuração, 8 sementes. Sobre a grade completa a razão mediana de ECE é
**129×** (mín 9,5×; máx 478×) — ver afirmação 3. **A referência subestima o efeito mediano.**

**Origem.** `resultados/varredura.csv`, filtro `ref`, coluna `ece_media` para `braco` em
{`A`, `C`}; `ece_dp` para a dispersão.

**Verificação independente.** O ECE foi recomputado do zero em
`experimento/figuras_relatorio.py` (regerando as predições por caso com `Params(pi=0.15,
f_base=0.16, beta=0.55)`, `N=40.000`, sementes `range(8)`, e replicando o binning de
`metricas.ece`). Bate com `varredura.csv` até o último bit: `|dif| = 0,00e+00` para `LOOKUP`,
`A`, `B` e `C`.

**Ressalva.** O ECE de `LOOKUP` é **0,000000 e degenerado** — `bracos.lookup` estima
`P(F | padrão)` no próprio conjunto em que é avaliado, então a calibração é perfeita por
construção. Não pode ser citado como vantagem de calibração da tabela empírica. A comparação
honesta de calibração é `A` contra `C`.

---

## Números que NÃO puderam ser sustentados

Esta seção não ficou vazia.

1. **"Mediana de +0,64 p.p. para B contra LOOKUP"** — não se reproduz. `B − LOOKUP` dá mediana
   **+0,673 p.p.**; `B − A` dá **+0,683 p.p.**; as médias dão +0,738 e +0,750. Nenhum recorte de
   `varredura.csv` produz 0,64. O número de CLAUDE.md precisa ser corrigido para +0,67 (contra a
   tabela empírica) ou +0,68 (contra `A`), com a comparação declarada.

2. **"B inverte o sinal da correlação em 33/48"** — verdadeiro apenas sob o critério
   pré-registrado `corr ≥ −0,10`. Inversão estrita (`corr ≥ 0`) é **30/48**. Enunciar sem o
   critério é impreciso.

3. **Qualquer intervalo de confiança, erro-padrão da mediana ou teste de significância.** Os CSVs
   guardam apenas média e desvio-padrão entre 8 sementes por célula; os valores por semente não
   são persistidos. Não é possível construir intervalo para nenhuma das medianas de grade sem
   reexecutar `varredura.py` com escrita por semente. Nenhum número deste ledger vem com p-valor,
   e nenhum deve receber um por interpolação.

4. **Incerteza das correlações de `equidade.csv`.** `corr_<braco>` é calculada sobre a **média**
   das 8 sementes (`equidade.py`: `np.mean(acc[b], axis=0)` antes de `np.corrcoef`), com n = 8 RAs.
   Não há dispersão amostral da correlação no arquivo. As contagens `n/N` são a única medida de
   robustez disponível — e são a razão de este ledger insistir nelas.

5. **FPR por RA fora da configuração de referência.** `fpr_por_ra.csv` cobre uma única célula
   (`varredura.py` só acumula `fpr_ref` quando β, π e ruído batem com a referência). As
   afirmações 5 e 8 são, portanto, pontuais por limitação do arquivo, não por escolha de
   apresentação. Só a amplitude e o sinal sobrevivem à grade (afirmações 6 e 7).

6. **Cobertura cadastral real por RA.** O vetor `COBERTURA` de `gerador.py` é **estipulado**.
   Toda afirmação territorial (5, 6, 7, 8) é condicional a ele. Nenhum número deste ledger mede
   cobertura cadastral do DF; medir isso no Geoportal/SEDUH continua sendo a pendência prioritária.

7. **Precisão de RULE_OR como comparação substantiva.** O número existe (afirmação 4) mas não
   sustenta afirmação sobre qualidade de modelagem: é consequência de um score binário sob
   desempate aleatório. Serve como argumento metodológico, não como tamanho de efeito.

---

## Figuras produzidas

| Arquivo | Conteúdo | Verificação |
|---|---|---|
| `figuras/fig3_confiabilidade.png` | Diagrama de confiabilidade de `LOOKUP`, `A`, `B`, `C` na referência, 10 bins de largura igual idênticos aos de `metricas.ece`, com diagonal de calibração perfeita | ECE anotado bate com `ece_media` de `varredura.csv`, `\|dif\| = 0` |
| `figuras/fig4_heatmap_beta_pi.png` | Sinal da correlação de `B` em β × π, três painéis de ruído, mapa divergente centrado em zero; células reprovadas com borda | 33/48 pelo critério, 30/48 estrito, anotados no título |
| `figuras/fig5_sensibilidade.png` | Diferença de precisão contra `LOOKUP` (p.p.), quatro painéis variando β e quatro variando π | direção de `B` (acima de zero) e de `C` (abaixo) preservada em todos os oito painéis |

Geradas por `experimento/figuras_relatorio.py` (não altera `figuras.py`). Duas execuções
consecutivas produzem PNGs de hash SHA-256 idêntico.
