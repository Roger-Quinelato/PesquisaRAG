# Parecer do CTO de pesquisa

**Documentos sob revisão**
`relatorios/Relatorio_Tecnico_RAG_Bayesiano.md` e `relatorios/Relatorio_Benchmark_Estado_da_Arte.md`

**Fontes abertas na revisão**
`resultados/varredura.csv`, `equidade.csv`, `fpr_por_ra.csv`; `relatorios/tabelas/*.csv` (4);
`relatorios/ledger_numeros.md` (integral); `experimento/varredura.py`;
`Proposta_PIDTI_RAG_Bayesiano2.pdf` (seção 3); `Resumo Congresso IC UnB - RAG Bayesiano.md`;
`figuras/fig4_heatmap_beta_pi.png`; 6 URLs.

## Veredito: REPROVADO

O relatório técnico está, na prática, aprovado — 20 números amostrados reproduziram na origem e
a disciplina de tamanho de efeito é exemplar. A reprovação é **do pacote** e tem causa única e
bloqueante: o relatório de benchmark escreve, em §6.2, exatamente a frase que o técnico dedica um
parágrafo a condenar. Dois documentos que vão à mesma banca se contradizem sobre o número que
sustenta o único achado reprovado do projeto.

---

## Critério 1 — Rastreabilidade numérica: APROVADO (ambos)

Os CSVs foram reabertos e os valores recomputados; nada foi aceito por constar do ledger.

**Relatório técnico — 20 números amostrados:**

| Número | Local | Recomputado da origem |
|---|---|---|
| `B−LOOKUP` mediana +0,673; mín −0,134; máx +2,956; 213/224 | Tab. 3, l. 322 | 0,6734 / −0,1344 / 2,9563 / 213 |
| `B−A` +0,683; 216/224 | l. 323 | 0,6828 / 216 |
| `B > max(A, LOOKUP)` 210/224 | l. 324 | 210 |
| Quartis [+0,246; +0,673; +1,110] | l. 326 | 0,2461 / 0,6734 / 1,1102 |
| `A−LOOKUP` −0,022; \|dif\| 0,059; máx 0,297; 86/224 | Tab. 2 | −0,0219 / 0,0594 / 0,2969 / 86 |
| IQR [−0,069; +0,048]; dp 0,0049 | l. 304–306 | confere |
| `C−A` Brier +0,1133; ECE +0,2912 | Tab. 4 | idênticos |
| Razão ECE 129× (9,5; 478); 224/224 em Brier e ECE | l. 388–390 | 129,2 / 9,5 / 477,7 |
| ECE ref `A` 0,0024564 / `C` 0,2255115 | l. 393 | idênticos |
| Tabelas 5, 6 e 7 integrais | l. 425–518 | conferidas linha a linha |

**Relatório de benchmark — 8 números:** sete conferem; o oitavo falha e é o problema P-1.

## Critério 2 — Integridade das citações: APROVADO COM RESSALVA

Seis URLs abertas, todas resolvem e o conteúdo confere: BayesRAG (arXiv 2601.07329), SURE-RAG
(2605.03534), EvidentialRAG (2607.10491, ECE 0,122), PMC12886353 (Frontiers in AI),
SymRAG (arXiv 2506.12981 — sem "Augmented Generation", confirmando a correção proposta à
proposta PIDTI) e Sudjianto & Burakov (2509.09855).

A conduta de §1.1 — descartar Srivastava 1995, Srivastava 2009 e Siddiqi por não abrirem, em vez
de rebaixá-los a "provável" — é a correta.

**Ressalva:** 22 das 33 referências não foram reabertas nesta revisão.

## Critério 3 — Coerência com os critérios pré-registrados: REPROVADO (benchmark)

Fonte: `experimento/varredura.py`, l. 92–123, com o literal
`'PASSA' if c_b >= -0.1 else 'FALHA'`.

O técnico rotula o reprovado como **(ii-b)** — numeração correta do script — e distingue os dois
números em §3.7. O benchmark, §6.2 l. 849, chama 33/48 de "inversão do sinal". É exatamente a
mistura que o técnico proíbe.

## Critério 4 — Escopo do sistema: APROVADO (ambos)

Busca por `conced|nega|aprova` não retorna nenhuma frase decisória.

## Critério 5 — RAG não implementado nem avaliado: APROVADO (ambos)

Declarado no cabeçalho de ambos e repetido em Limitações. Nenhuma métrica de recuperação nas
tabelas de resultado.

## Critério 6 — Parâmetros estipulados declarados: APROVADO (técnico) / RESSALVA (benchmark)

O técnico declara em §2.1, no **cabeçalho da Tabela 5**, na coluna "Cobertura (estipulada)" e em
§5. O benchmark só no Anexo — problema P-4.

## Critério 7 — Disciplina de tamanho de efeito: APROVADO

Procurou-se ativamente a repetição do erro "1,7 a 2,4 p.p.". **Não existe.** O número que o
reproduziria (+1,756 p.p. na referência) está rotulado como ilustração e seguido de "não deve ser
relatado como efeito típico". A política é declarada antes dos resultados e aplicada também
quando desfavorece a tese. Não há p-valor nem intervalo de confiança; onde caberia
"significativo", o texto usa contagem `n/N`.

## Critério 8 — Consistência com o resumo submetido: 6 DIVERGÊNCIAS

O resumo **não foi editado** — estas divergências são reportadas para decisão do autor.

| # | O que o resumo diz | O que a origem diz | Gravidade |
|---|---|---|---|
| D-1 | "mediana de **seis décimos** de p.p." | +0,673 → sete décimos | relevante |
| D-2 | "inversão de sinal em **33 das 48**" | 30/48 estrito; 33/48 é o limiar do critério | **bloqueante** |
| D-3 | ECE "chega a **sessenta e quatro centésimos**" | o máximo de ECE de `C` na grade é **0,7374** | relevante |
| D-4 | "O **terceiro** critério foi reprovado" | (iii) é o de utilidade e **passou** (210/224); o reprovado é o (ii) | **bloqueante** |
| D-5 | regra binária "atinge **um quarto** da precisão das demais" | 0,2525 / 0,6688 = **37,8%** | relevante |
| D-6 | "quase **noventa** vezes" | 91,8× — é mais de noventa | menor |

O resumo também omite a segunda faixa de falha de `B`: ruído alto com π alta, onde a correlação
chega a −0,9063.

**Conferem e passam:** 0,059 / 0,297; −0,997; 48/48; 5,58% contra 2,87%; 12,601% / 0,460% = 27,4×;
224 configurações, 14 níveis de ruído, 8 sementes, 40.000 casos; cobertura declarada como
estipulada; RAG declarado como não avaliado.

---

## Problemas nos relatórios

**P-1 — BLOQUEANTE.** Benchmark §6.2. Apresenta 33/48 como inversão de sinal (é 30/48),
contradizendo o técnico. *Correção:* "a inversão estrita do sinal ocorre em 30 de 48
configurações, e o critério pré-registrado (`corr ≥ −0,10`) é atendido em apenas 33 de 48".

**P-2 — RELEVANTE.** Benchmark §6.2, cabeçalho "Ressalva sobre H2". O conteúdo trata de
reconciliar **H3** com H2, reabrindo a confusão de numeração corrigida 20 linhas acima.

**P-3 — RELEVANTE.** Benchmark §6.2 e técnico §4. Descrevem a falha de `B` só como "ruído baixo
com gradiente íngreme", omitindo a faixa `f_base` = 0,28 com β ≥ 0,55 e π ≥ 0,15.

**P-4 — RELEVANTE.** Benchmark §3 e §6.2 reivindicam o diferencial territorial sem a etiqueta de
cobertura estipulada.

**P-5 — MENOR.** Técnico §3.3: das 11 configurações em que `B` não supera `LOOKUP`, uma não está
em nenhum dos "cantos" descritos. Trocar por "dez das onze".

**P-6 — MENOR.** Técnico §3.8 e §4: 0,054269 / 0,017127 = 3,169 → **3,17×**, não 3,18×. Mesmo
deslize com 31,447 escrito como 31,44.

**P-7 — MENOR.** Técnico §3.1: 4,4×10⁻¹⁷ é o **máximo da grade**; na referência, de que a frase
trata, é 1,94×10⁻¹⁷.

**P-8 — MENOR.** Técnico §3.7: "As 18 configurações formam duas faixas" — as faixas cobrem 10
das 18.

---

## Nota de verificação do orquestrador

A afirmação do parecer em **D-3** de que "0,64 não consta do ledger" foi reconferida e está
**parcialmente incorreta**: existem cinco configurações da grade com ECE de `C` entre 0,6324 e
0,6467. O problema apontado permanece válido por outra razão — o resumo escreve "chega a", que
promete o máximo, e o máximo real é 0,7374 (`f_base` = 0,40; β = 0,70; π = 0,05).

D-4, D-5 e D-6 foram reconferidos de forma independente e estão corretos:
critério (iii) = 210/224 (passou), critério (ii) parte `B` = 33/48 (reprovou);
`RULE_OR` 0,2525 contra média 0,6688 dos demais = 37,8%; razão de ECE na referência = 91,8×.

## O que a revisão verificou e passou

20 números do técnico e 8 do benchmark localizados na linha de origem, zero órfãos; tabelas de
apoio conferidas contra `resultados/`; critérios lidos no código-fonte, não no que o documento diz
de si; hipóteses conferidas no PDF — as 6 ocorrências no técnico e as 5 no benchmark estão
corretas e **os dois documentos concordam, sem nenhuma inversão remanescente**; Figura 4 conferida
célula a célula (48 valores, 15 bordas = 15 reprovações); ausência de p-valor e de intervalo de
confiança; escopo de triagem nos dois; ECE de `LOOKUP` tratado como degenerado e excluído de toda
conclusão; anomalia Taguatinga/Gama declarada, não silenciada.

## O que ficou fora do alcance da revisão

O experimento não foi reexecutado — os hashes SHA-256 alegados não foram testados nesta revisão.
22 das 33 referências do benchmark não foram reabertas, incluindo as URLs de CGU/TCU/NIST e os 11
arquivos `LICENSE` que sustentam a tabela de licenças. As figuras 1, 2, 3 e 5 não foram
conferidas. **`bracos.py`, `metricas.py` e `gerador.py` não foram auditados** — se um deles
estiver errado, todos os CSVs estarão errados de forma consistente e esta revisão não o
detectaria. Os `.docx` não foram revisados.
