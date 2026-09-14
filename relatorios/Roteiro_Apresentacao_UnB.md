# Roteiro de apresentação — Congresso de Iniciação Científica da UnB

**Título de trabalho:** Onde o dado territorial deve entrar em um modelo bayesiano de triagem de
inconsistências cadastrais — no prior ou na verossimilhança?

Este roteiro segue a estrutura do resumo submetido (`Resumo Congresso IC UnB - RAG Bayesiano.md`,
já corrigido conforme `relatorios/PARECER_CTO.md`) e reaproveita as figuras já produzidas em
`figuras/`. Cada bloco indica a duração aproximada para uma apresentação de 8–10 minutos e o
número da figura/tabela de apoio.

---

## Slide 1 — A pergunta (30s)

**Fala:** "Quando um modelo bayesiano de triagem de crédito usa o endereço do solicitante como
evidência, e o cadastro territorial do Distrito Federal tem qualidade desigual entre Regiões
Administrativas — o dado de região deve calibrar a probabilidade inicial de suspeita, o *prior*,
ou o peso que cada evidência recebe, a verossimilhança?"

**No slide:** só a pergunta, uma frase, sem logotipos de arquitetura em quatro camadas. A
audiência decide em 10 segundos se quer prestar atenção; dar a pergunta primeiro economiza esse
tempo.

## Slide 2 — Por que a pergunta existe (1 min)

**Fala:** "A proposta original deste projeto tinha duas hipóteses que convivem mal. Uma dizia que
calibrar o prior com dados territoriais locais tornaria o modelo mais informativo. A outra dizia
que o sistema reduziria vieses contra populações vulneráveis. Um prior condicionado à região eleva
a suspeita de quem mora ali antes mesmo de examinar o caso — e registra isso por escrito na
própria trilha de auditoria que o projeto promete produzir. As duas hipóteses apontam em direções
opostas, e esta etapa da pesquisa transformou essa contradição em experimento."

**No slide:** as duas hipóteses lado a lado, com uma seta de conflito entre elas. (Evitar citar
H2/H3 pelo número na fala — a numeração já foi invertida por engano uma vez neste projeto; se
citar pelo número, sempre com o enunciado ao lado.)

## Slide 3 — Como o experimento foi desenhado (1,5 min)

**Fala:** "Fraude é uma variável latente — não existe rótulo confiável de fraude cadastral nas
bases disponíveis. Por isso o experimento simula o mecanismo causal: cada caso tem uma fraude
latente sorteada com a mesma probabilidade em todas as oito Regiões Administrativas — essa
igualdade é o controle central do experimento. Três evidências documentais ruidosas nascem dessa
fraude, e só a evidência de endereço tem sua taxa de falso positivo crescendo onde a cobertura do
cadastro territorial é menor. Como a taxa de fraude é igual por construção, qualquer disparidade
territorial que aparecer nos resultados só pode vir da qualidade da fonte, nunca da população."

**No slide:** diagrama simples — fraude latente → três setas para as evidências → uma quarta seta
rotulada "gradiente territorial" chegando só na evidência de endereço.

**Ressalva a dizer em voz alta, não só no slide:** "A cobertura cadastral por região usada aqui é
estipulada, não medida — obtê-la no Geoportal/SEDUH é o próximo passo da pesquisa."

## Slide 4 — Os seis braços e os três critérios pré-registrados (1 min)

**Fala:** "Comparamos seis abordagens: duas regras determinísticas, uma tabela empírica que serve
de teto de referência, e três variantes bayesianas que diferem só em onde colocam o território —
fora do modelo, na verossimilhança, ou no prior. Antes de rodar qualquer coisa, declaramos três
critérios de aceitação, com a regra de que achado reprovado sai do texto. Um dos três reprovou, e
ele está aqui com o mesmo destaque dos outros dois."

**No slide:** tabela dos seis braços (`Relatorio_Tecnico_RAG_Bayesiano.md`, Tabela 1, versão
resumida) e os três critérios enunciados em uma linha cada.

## Slide 5 — Resultado 1: Bayes sozinho não ajuda (1 min, Figura 1)

**Fala:** "O primeiro resultado é negativo, e é o mais instrutivo. A variante bayesiana que ignora
o território não supera a tabela empírica de referência — a diferença tem mediana de seis
centésimos de ponto percentual, e nunca passa de três décimos, o que está dentro do ruído
amostral. O aparato bayesiano, aplicado a evidências tratadas como homogêneas, só reproduz o que
uma tabela de oito padrões já entrega."

**Figura:** `figuras/fig1_precisao_calibracao.png`.

## Slide 6 — Resultado 2: o prior territorial quebra a calibração (1,5 min, Figura 3)

**Fala:** "O segundo resultado é categórico. Condicionar o prior à taxa de inconsistência
observada da região piora o escore de Brier e o erro de calibração em todas as 224 configurações
testadas, sem uma única exceção. Na configuração de referência, o erro de calibração passa de
dois milésimos para vinte e três centésimos — mais de noventa vezes maior — chegando a setenta e
quatro centésimos no pior caso da grade. O mecanismo é dupla contagem: a taxa que alimenta o
prior é produzida pelas mesmas evidências que depois entram na verossimilhança. Não é um efeito
que desaparece com mais dados — é estrutural."

**Figura:** `figuras/fig3_confiabilidade.png` (curva de `C` afastada da diagonal).

## Slide 7 — Resultado 3: a disparidade emerge sem nenhuma variável demográfica (1,5 min, Figura 2)

**Fala:** "O terceiro resultado é o mais relevante para política pública. Não existe raça, renda,
escolaridade ou qualquer atributo demográfico no modelo. Ainda assim, a correlação entre a
cobertura cadastral da região e a fração de inocentes enviados à revisão chega a menos zero
vírgula nove nove sete, e essa correlação negativa se repete em 48 de 48 configurações testadas.
Na configuração de referência, o inocente de Ceilândia é enviado à revisão em cinco vírgula seis
por cento dos casos, contra dois vírgula nove por cento no Plano Piloto. A discriminação
territorial emerge sozinha, da qualidade desigual da base pública."

**Figura:** `figuras/fig2_equidade_territorial.png`.

## Slide 8 — Resultado 4: mover para a verossimilhança não é solução de equidade (1,5 min, Figura 4)

**Fala:** "A hipótese natural é corrigir isso movendo o território para a verossimilhança em vez
do prior. Isso de fato melhora um pouco a precisão da fila de revisão — mediana de sete décimos
de ponto percentual, positiva em 213 de 224 configurações. Mas o segundo critério pré-registrado,
o de equidade, reprovou: o critério declarado de antemão é atendido em 33 das 48 configurações, e
a inversão estrita do sinal da correlação ocorre em apenas 30 das 48 — falhando exatamente sob
ruído baixo com gradiente territorial íngreme, e também sob ruído alto com prevalência de fraude
alta. E mesmo quando o sinal inverte, a amplitude da disparidade nessa variante é três vezes maior
que na variante que ignora o território: ela não reduz a desigualdade, redistribui quem paga por
ela."

**Figura:** `figuras/fig4_heatmap_beta_pi.png` (células reprovadas com borda).

## Slide 9 — Conclusão (1 min)

**Fala:** "A posição do dado territorial no modelo importa mais do que o uso da inferência
bayesiana em si. Colocá-lo no prior degrada a calibração de forma robusta. Colocá-lo na
verossimilhança melhora um pouco a acurácia, mas não resolve a equidade. E o resultado de fundo é
desconfortável: não existe correção, no nível da agregação de evidências, para a desigualdade
produzida por qualidade desigual de dado. Enquanto a cobertura do cadastro territorial variar
entre regiões, qualquer sistema que use endereço como evidência penalizará quem mora onde o
registro é pior — inclusive os sistemas construídos para serem neutros."

**No slide:** a frase de fechamento em destaque, e a ponte com a outra etapa do grupo (dengue):
"Esta é a segunda vez, em dois domínios diferentes, que o obstáculo se revela ser a qualidade do
dado, não a escolha do método."

## Slide 10 — Próximo passo e limitações (30s)

**Fala:** "O próximo passo prioritário é medir a cobertura cadastral real do DF no Geoportal/
SEDUH, hoje estipulada. E vale repetir o escopo: esta etapa avalia só a camada de agregação
probabilística — a camada de recuperação de evidências (RAG) ainda não foi implementada nem
avaliada —, e o sistema, em nenhum momento, decide concessão ou negação de crédito: ele ordena uma
fila de revisão humana."

---

## Perguntas prováveis da banca e resposta pronta

- **"Isso não é só Fellegi-Sunter de 1969?"** — "Sim, o mecanismo de agregação é de 1969 e a
  implementação de referência (Splink) já é madura e open source. A contribuição não é o
  mecanismo, é a pergunta: onde a covariável territorial entra, testada com critérios
  pré-registrados e uma reprovação real."
- **"Por que simulação, e não dados reais do DF?"** — "Porque fraude é latente — não existe
  rótulo confiável — e avaliar calibração exige conhecer o parâmetro verdadeiro que gerou os
  dados. Um gerador ajustado a dados reais destruiria exatamente essa verificação."
- **"A cobertura cadastral que vocês usam é dado real do Geoportal?"** — "Não. É estipulada, uma
  ordenação plausível das oito regiões, não uma medição. Toda afirmação territorial deste
  trabalho é condicional a esse vetor, e obtê-lo de verdade é o próximo passo."
- **"Afinal, o sistema é enviesado ou não?"** — "As duas coisas são verdadeiras ao mesmo tempo.
  Ignorar o território é enviesado, com correlação de quase −1 em 48 de 48 configurações. Mover
  para a verossimilhança reduz o viés na maior parte dos casos, mas falha exatamente sob as
  condições mais adversas, e ainda triplica o tamanho da disparidade quando falha."
- **"Vocês implementaram o RAG?"** — "Não nesta etapa. Esta etapa isola e avalia só a camada de
  agregação bayesiana das evidências, que é o alicerce sobre o qual o RAG será construído depois."

---

## Checklist antes de apresentar

- [ ] Resumo submetido corrigido conforme `PARECER_CTO.md` (D-1 a D-6) — **feito nesta sessão**.
- [ ] Nenhum número desta fala diverge de `relatorios/ledger_numeros.md`.
- [ ] Figuras 1–4 abertas e conferidas visualmente antes de subir ao palco.
- [ ] Ensaiar a resposta sobre "cobertura estipulada" sem esperar a pergunta — dizer antes.
