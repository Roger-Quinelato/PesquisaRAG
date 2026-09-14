# Guia das figuras — o que cada gráfico mostra, por que importa e o que ele prova

As cinco figuras em `figuras/` são geradas por `experimento/figuras.py` (Figuras 1 e 2) e
`experimento/figuras_relatorio.py` (Figuras 3, 4 e 5), com paleta e estilo compartilhados em
`experimento/paleta_sns.py`. Nenhum número aqui é novo: todos vêm de `resultados/` e já estão
auditados em `relatorios/ledger_numeros.md` e em `relatorios/Relatorio_Tecnico_RAG_Bayesiano.md`.
Este guia serve para quem olha uma figura solta — num slide, num banner — e precisa saber o que
ela mostra, por que ela foi escolhida entre as várias que o experimento poderia produzir, e o que
ela efetivamente prova ou refuta.

Convenção de cor, fixa nas cinco figuras: **azul = braço A** (território ignorado), **laranja =
braço B** (território na verossimilhança), **água/verde = braço C** (território no prior). Regras
e tabela empírica usam tons de cinza/sage porque são referência de piso e teto, não objeto de
comparação de identidade. Essa cor nunca muda de figura para figura nem é redistribuída por corte
de dados — quem aprendeu "B é laranja" pode confiar nisso em todo o documento.

---

## Figura 1 — `fig1_precisao_calibracao.png`

**O que mostra.** Três painéis lado a lado, todos com o ruído da evidência no eixo x, na
configuração de referência (β = 0,55; π = 0,15): a precisão da fila de revisão sob orçamento de
10% (painel 1), a diferença de cada braço contra a tabela empírica (painel 2) e o erro de
calibração esperado, o ECE (painel 3).

**Por que ela importa.** É a figura que decide se vale a pena usar Bayes. Sem ela, a pergunta "o
modelo bayesiano é melhor que uma tabela de consulta?" fica sem resposta visual — os números
isolados (0,059 p.p., 0,673 p.p.) não comunicam por si só o quão próximas as curvas estão. O
painel 2 existe especificamente porque, no painel 1, as curvas de `LOOKUP`, `A` e `B` ficam quase
sobrepostas: sem replotar a diferença, o ganho de `B` fica invisível a olho nu.

**O que ela prova.** No painel 1, `A` (azul) e a tabela empírica seguem praticamente juntas do
início ao fim — é a primeira evidência visual de que aplicar Bayes sem informação territorial não
ganha nada sobre uma tabela de oito células. No painel 2, isso fica quantificado: a linha azul de
`A` oscila em torno de zero (mediana −0,022 p.p.; suporte de 86/224 configurações, indistinguível
de moeda honesta), enquanto a linha laranja de `B` fica consistentemente acima de zero (mediana
+0,673 p.p., positiva em 213/224) — um ganho real, mas pequeno. A curva verde de `C` no mesmo
painel mostra a contrapartida: ela cai abaixo de zero bem mais fundo do que `B` sobe acima, porque
condicionar o prior à região não troca precisão por equidade de graça — perde nos dois. O painel 3
é o mais dramático dos três: as curvas de `LOOKUP`, `A` e `B` ficam grudadas perto de zero em toda
a faixa de ruído, enquanto a curva verde de `C` sobe quase em linha reta até quase 0,65 — a
assinatura visual do que a Figura 3 vai explicar como mecanismo (dupla contagem).

---

## Figura 2 — `fig2_equidade_territorial.png`

**O que mostra.** A fração de pessoas inocentes de cada Região Administrativa enviada à revisão
humana (eixo y), contra a cobertura do cadastro territorial daquela região (eixo x), para os
braços `RULE_CNT`, `A`, `B` e `C` na configuração de referência. Cada ponto é uma RA; o
coeficiente de correlação de cada braço vai na legenda.

**Por que ela importa.** É a única figura do conjunto que fala diretamente com quem decide
política pública, e não só com quem lê a matemática. Nenhuma variável demográfica entra no
gerador — a taxa de fraude é idêntica nas oito regiões por construção —, então esta figura isola
uma pergunta que interessa fora da estatística: mesmo sem informação sobre quem é o solicitante,
o sistema penaliza sistematicamente quem mora onde o cadastro é pior?

**O que ela prova.** A resposta é sim, para quase todos os braços: a linha cinza tracejada de
`RULE_CNT` e a linha azul de `A` descem de forma quase linear da esquerda (baixa cobertura, alto
FPR) para a direita (alta cobertura, baixo FPR) — correlações de −1,00 e −0,99. A linha verde de
`C` faz o mesmo, só que de forma mais extrema: sai do ponto mais alto do gráfico (Ceilândia, 12,6%)
e despenca até quase zero em Plano Piloto — o prior territorial não só herda a disparidade, ele a
amplifica (razão de 27,4× entre as duas regiões extremas). A exceção visual é a linha laranja de
`B`: ela sobe da esquerda para a direita entre Ceilândia e Sobradinho, mas depois se achata e
inverte de novo perto de Plano Piloto — daí a correlação positiva (+0,80) parecer melhor do que
realmente é. A nota de rodapé da própria figura avisa o que o gráfico, sozinho, não mostra: esta é
uma única configuração; na grade completa de 48, a inversão de `B` só se sustenta em 30 delas.

---

## Figura 3 — `fig3_confiabilidade.png`

**O que mostra.** Um diagrama de confiabilidade (reliability diagram): no eixo x, a probabilidade
que cada braço atribuiu a um grupo de casos; no eixo y, a fração desses casos que de fato tinha
fraude latente. A diagonal pontilhada é a calibração perfeita — "quando o modelo diz 30%, acontece
30%". O tamanho de cada marcador é proporcional à fração de casos naquele grupo.

**Por que ela importa.** O ECE do painel 3 da Figura 1 é um número só; esta figura mostra *a forma*
do erro, o que muda a interpretação. Um ECE alto pode vir de superconfiança (o modelo diz "90%"
quando deveria dizer "60%") ou de subconfiança — e só a curva revela qual é o caso e em que faixa
de probabilidade o desvio se concentra.

**O que ela prova.** `LOOKUP`, `A` e `B` — a faixa cinza grossa e as linhas azul e laranja — seguem
a diagonal com tanta fidelidade que praticamente se confundem numa só espessura, do canto inferior
esquerdo ao superior direito: ECE de 0,0000 (degenerado, ver ressalva no rodapé), 0,0025 e 0,0027,
respectivamente. A curva verde de `C` conta uma história diferente e específica: ela começa
*abaixo* da diagonal nos grupos de baixa probabilidade prevista e sobe para *acima* dela nos
grupos de probabilidade alta — não é um deslocamento uniforme, é superconfiança sistemática nas
duas pontas. Essa é a assinatura visual exata da dupla contagem descrita em
`Relatorio_Tecnico_RAG_Bayesiano.md` (seção 3.5): a taxa que calibra o prior de `C` é produzida
pelas mesmas evidências que depois entram na verossimilhança, então o modelo conta o mesmo sinal
duas vezes e termina mais confiante do que deveria nos dois extremos.

---

## Figura 4 — `fig4_heatmap_beta_pi.png`

**O que mostra.** Três mapas de calor lado a lado, um por nível de ruído da evidência, cada um
cruzando o gradiente territorial β (linhas) com a prevalência de fraude π (colunas). A cor de cada
célula é a correlação entre cobertura cadastral e FPR entre inocentes para o braço `B`; células com
borda preta reprovam o critério pré-registrado (correlação ≥ −0,10).

**Por que ela importa.** É a figura que decide, sozinha, se `B` pode ser vendido como solução de
equidade — e a resposta não pode vir de um único número, porque o comportamento de `B` **muda de
sinal dentro da própria grade**. Uma tabela de médias esconderia exatamente o padrão que interessa:
onde `B` falha não é aleatório, é sistemático em duas regiões identificáveis do espaço de
parâmetros.

**O que ela prova.** No painel de ruído mais baixo (0,07), a coluna da esquerda (β alto, π baixo)
é quase toda vermelha com borda — a pior faixa de falha de `B`, com correlações chegando a −0,97.
No painel de ruído mais alto (0,28), a reprovação reaparece no canto oposto: células com π alto e
β alto voltam a ficar vermelhas (até −0,91), a segunda faixa de falha que o resumo submetido
tinha omitido e que esta pesquisa corrigiu explicitamente. No painel do meio (ruído de referência,
0,16) — o que a Figura 2 usa —, quase tudo é azul, e é justamente por isso que uma figura isolada
na configuração de referência, sozinha, daria a impressão errada de que `B` resolve o problema. O
título já cravado na figura resume o resultado que ela sustenta: o critério pré-registrado passa em
33 das 48 células; a inversão estrita de sinal, em só 30.

---

## Figura 5 — `fig5_sensibilidade.png`

**O que mostra.** Oito painéis pequenos: os quatro de cima variam β com π fixo, os quatro de baixo
variam π com β fixo. Cada painel replica o painel 2 da Figura 1 (diferença de precisão contra a
tabela empírica) para uma combinação diferente de parâmetros.

**Por que ela importa.** Toda figura anterior usa a configuração de referência ou uma célula da
grade. Esta é a única que responde à pergunta que sustenta a validade das outras: **os efeitos
sobrevivem quando os parâmetros mudam, ou são um acidente da célula escolhida?** Sem ela, cada
número do relatório teria de vir acompanhado da desculpa "mas isso pode ser só esta configuração".

**O que ela prova.** Em todos os oito painéis, sem exceção, a curva laranja de `B` fica acima de
zero e a curva verde de `C` fica abaixo — a direção dos dois efeitos centrais da pesquisa não
depende de qual célula da grade se escolhe para ilustrar. O tamanho, esse sim, varia bastante: o
pico de `B` vai de cerca de +0,9 p.p. (β = 0,25) a quase +3 p.p. (β = 0,70); o vale de `C`, por sua
vez, não varia de forma monotônica com π — é mais profundo em π = 0,10 (perto de −3,3 p.p.) do que
em π = 0,05, e quase desaparece em π = 0,25, onde a curva verde oscila perto de zero. A anotação de
texto num dos painéis ("Regra por
contagem: −8,3 p.p. fora de escala") é deliberada: em vez de esticar o eixo y de todos os oito
painéis para acomodar um único ponto extremo, o corte fica fixo e o valor fora de escala é citado
por escrito — a alternativa (deixar o eixo se ajustar) achataria os outros sete painéis e esconderia
exatamente o padrão que a figura existe para mostrar.

---

## Síntese — o que as cinco figuras provam em conjunto

Lidas em sequência, as figuras contam uma história com três movimentos, na mesma ordem da
Conclusão de `Relatorio_Tecnico_RAG_Bayesiano.md`:

1. **Bayes sem território não ajuda** (Figura 1, painéis 1 e 2): a variante `A` empata com a
   tabela empírica.
2. **Colocar o território no prior piora a calibração de forma estrutural, não circunstancial**
   (Figuras 1 painel 3 e 3): o ECE de `C` não é um número ruim isolado, é uma superconfiança
   sistemática nas duas pontas da distribuição, com mecanismo identificável (dupla contagem).
3. **Colocar o território na verossimilhança ganha um pouco de precisão, mas não é solução de
   equidade** (Figuras 2, 4 e 5): o ganho de `B` é real e sobrevive à grade inteira (Figura 5), mas
   sua correção da disparidade territorial é frágil e falha em duas faixas identificáveis da grade
   (Figura 4) — o que uma única configuração de referência (Figura 2) não deixaria ver sozinha.

A figura que mais generaliza sozinha é a 5 (nenhuma célula da grade contradiz a direção dos
efeitos); a que mais qualifica uma afirmação simples é a 4 (o "33/48" só faz sentido lido junto com
o mapa de onde ficam os 15 que falham); e a que mais fala fora da estatística é a 2 (o achado de
que qualidade desigual de cadastro produz disparidade territorial sem nenhuma variável
demográfica no modelo).

*Reprodução: `python experimento/figuras.py && python experimento/figuras_relatorio.py`, a partir
de `resultados/` já gerado por `varredura.py` e `equidade.py`. Todas as figuras são determinísticas
por semente — duas execuções produzem PNGs de hash SHA-256 idêntico.*
