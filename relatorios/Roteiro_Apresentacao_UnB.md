# Roteiro de apresentação do pôster: Congresso de Iniciação Científica UnB/DF

**Pôster:** Bayes, RAs e Viés: Influência da Localidade na Triagem de Crédito

Numa sessão de pôster, você fica ao lado do banner e os avaliadores chegam em momentos
diferentes, com tempos diferentes. Por isso este roteiro tem duas versões: um **pitch de
1 minuto**, para quem está de passagem, e uma **apresentação completa de cerca de 6 minutos**,
que percorre o pôster na ordem de leitura e aponta cada figura. Os números são os mesmos
impressos no pôster e conferidos em `relatorios/ledger_numeros.md`.

A versão anterior deste roteiro, feita para slides, está no histórico do git.

---

## Pitch de 1 minuto

> "A gente testou uma pergunta simples: num modelo bayesiano que faz triagem de crédito, onde
> a região do solicitante deve entrar, na suspeita inicial ou no peso das evidências?
> Simulamos oito Regiões Administrativas com exatamente a mesma taxa de fraude. A única
> diferença entre elas é a qualidade do cadastro de endereço. Três resultados. Colocar a
> região na suspeita inicial piora a calibração do modelo em 224 de 224 configurações.
> Mesmo sem nenhuma variável demográfica, os inocentes de Ceilândia vão quase duas vezes mais
> à revisão do que os do Plano Piloto. E mover a região para o peso das evidências melhora um
> pouco a precisão, mas não corrige essa desigualdade. A conclusão é que, enquanto o cadastro
> for pior em algumas regiões, qualquer sistema que use o endereço vai penalizar quem mora
> lá."

Se o avaliador ficar, siga para a versão completa a partir da Metodologia.

---

## Apresentação completa (cerca de 6 minutos)

### 1. A pergunta (20 s) · aponte para o título

> "Quando um modelo bayesiano de triagem de crédito usa o endereço como evidência, e o
> cadastro territorial do DF tem qualidade diferente entre as regiões, onde o dado de região
> deve entrar: na probabilidade inicial de suspeita, o prior, ou no peso de cada evidência, a
> verossimilhança?"

### 2. Por que a pergunta existe (40 s) · Introdução

> "O projeto maior propõe um sistema que recupera evidências documentais, tipifica as
> inconsistências e atualiza a probabilidade de fraude com Bayes, para que a justificativa
> seja o próprio cálculo. Mas a proposta original tinha duas hipóteses que brigam entre si.
> Uma dizia que calibrar o prior com dados da região deixaria o modelo mais informativo. A
> outra dizia que o sistema reduziria vieses contra populações vulneráveis. Só que um prior
> regional aumenta a suspeita de quem mora em certas regiões antes de olhar o caso, e isso
> fica registrado na trilha de auditoria. Esta etapa transformou esse conflito em
> experimento."

Se citar as hipóteses pelo número, diga o enunciado junto: H3 é a do prior regional, H2 é a
da redução de vieses. A numeração já foi trocada por engano uma vez neste projeto.

### 3. O objetivo (30 s) · Figura 1

> "Comparamos três variantes do mesmo modelo. Na Figura 1: a A ignora a região; a B coloca
> a região no peso das evidências; a C coloca a região no prior. Medimos três coisas:
> calibração, precisão na fila de revisão e equidade entre as regiões."

### 4. Como foi feito (1 min) · Metodologia, Figura 2

> "Fraude é uma variável latente: não existe base pública com fraude rotulada. Então
> simulamos o mecanismo. Cada caso tem fraude com a mesma probabilidade, 15%, nas oito
> regiões; essa igualdade é o controle do experimento. São três evidências: situação
> cadastral, endereço e valor. Só o endereço depende da região. Na Figura 2, o falso positivo
> do endereço vai de 17,7% no Plano Piloto a 40,8% em Ceilândia, porque onde o cadastro é
> pior, não achar o endereço é quase normal. Como a fraude é igual em todo lugar, qualquer
> diferença entre regiões nos resultados só pode vir da qualidade do dado."

**Diga antes que perguntem:** "A cobertura do cadastro por região foi estipulada, não medida.
Obter o dado real no Geoportal/SEDUH é o próximo passo."

> "O sistema não aprova nem nega crédito: ele ordena uma fila para revisão humana. Por isso a
> métrica principal é a precisão entre os 10% de casos mais suspeitos. Foram 224
> configurações de parâmetros, cada uma com 8 repetições de 40 mil casos, e os critérios de
> aceitação foram declarados antes de rodar."

### 5. Resultado: Bayes sem região não ganha nada, e região no prior quebra a calibração (1 min) · Figura 3

> "No painel (a) da Figura 3, a linha azul, da variante A, fica em cima do zero: sem
> informação territorial, o modelo bayesiano só empata com uma tabela empírica simples, com
> diferença mediana de 0,06 ponto percentual. A linha laranja, da B, fica acima: ganho real,
> mas modesto, de 0,67 ponto na mediana, positivo em 213 das 224 configurações."

> "O painel (b) é o resultado mais forte. Colocar a região no prior, a linha verde, piorou a
> calibração em todas as 224 configurações. Na configuração de referência, o erro de
> calibração passa de 0,0025 para 0,2255, mais de 90 vezes maior. O motivo é dupla contagem:
> a taxa da região que alimenta o prior é produzida pelas mesmas evidências que depois entram
> de novo no cálculo. O modelo conta o mesmo sinal duas vezes e fica confiante demais."

### 6. Resultado: a discriminação aparece sozinha (1 min) · Figura 4

> "Este é o resultado mais importante para política pública. Não existe raça, renda nem
> escolaridade no modelo, e a fraude é igual em todas as regiões. Mesmo assim, na Figura 4, a
> regra por contagem manda à revisão 5,6% dos inocentes de Ceilândia, contra 2,9% no Plano
> Piloto. A correlação entre cobertura do cadastro e falso positivo é de −0,997, e se repete
> em 48 de 48 configurações. A linha verde mostra que o prior regional piora isso: 12,6%
> contra 0,5%."

### 7. Resultado: a verossimilhança não resolve (1 min) · Figuras 5 e 6

> "A ideia natural seria: então coloca a região na verossimilhança, que é onde ela realmente
> atua. Na Figura 4, a linha laranja até parece corrigir. Mas essa figura é uma configuração
> só. Na Figura 5, que resume a grade inteira, três achados se sustentam, e o quarto, que diz
> que B corrige a disparidade, foi reprovado: passou em 33 de 48 configurações, e o critério
> declarado antes exigia todas. A Figura 6 mostra onde falha: as células com borda preta se
> concentram em ruído baixo com gradiente territorial forte e em ruído alto com muita fraude.
> Mantivemos esse resultado reprovado no pôster com o mesmo destaque dos outros."

### 8. Conclusão (1 min) · Figura 7

> "A posição do dado territorial importa mais do que usar Bayes. No prior, degrada a
> calibração e concentra o falso positivo nas regiões de cadastro pior. Na verossimilhança,
> ganha um pouco de precisão, mas não resolve a equidade. Na Figura 7, a diferença entre a
> região mais e a menos penalizada é de 1,7 ponto em A, 5,4 em B e 8,8 em C. Ou seja, B e C
> aumentam a disparidade. Esse mecanismo, dado de qualidade desigual gerando injustiça, já
> foi descrito na literatura por Akpinar, Lipton e Chouldechova, em 2024; aqui ele aparece
> aplicado ao cadastro territorial do DF."

> "A mensagem final: enquanto a cobertura do cadastro variar entre as regiões, qualquer
> sistema que use o endereço como evidência vai penalizar quem mora onde o registro é pior,
> inclusive os que foram feitos para ser neutros. Medir e publicar essa cobertura por região
> é requisito de governança, não detalhe técnico."

Opcional, se o avaliador conhecer o grupo: "É a segunda vez, em dois domínios diferentes, que
o obstáculo acaba sendo a qualidade do dado, e não o método."

### 9. Limitações e próximo passo (20 s)

> "Três limitações: é simulação, então valem as direções, não os tamanhos exatos; a cobertura
> do cadastro foi estipulada; e a parte de recuperação de evidências, o RAG, ainda não foi
> integrada. O próximo passo é medir a cobertura real no Geoportal."

---

## Perguntas prováveis e respostas prontas

- **"Por que simulação, e não dados reais do DF?"** — "Porque a fraude é latente: não existe
  rótulo confiável. E para medir calibração é preciso conhecer a probabilidade verdadeira que
  gerou os dados. Um gerador ajustado a dados reais perderia exatamente essa referência."
- **"A cobertura do cadastro é dado real do Geoportal?"** — "Não. É uma ordenação plausível
  das oito regiões, estipulada. Todo resultado territorial depende dela. Variar a intensidade
  do gradiente (β) é uma defesa parcial: os efeitos principais mantêm a direção, mas o
  tamanho muda. Medir de verdade é o próximo passo."
- **"O que é essa tabela empírica? Por que ela é o teto?"** — "Ela calcula a taxa de fraude
  para cada combinação das três evidências usando o próprio rótulo simulado. Na prática não
  daria para implantá-la, porque na vida real não se conhece a fraude. Ela serve de régua: é o
  máximo que três evidências sim ou não conseguem informar sem usar a região."
- **"Por que precisão nos 10% e não acurácia ou F1?"** — "Porque o sistema não decide
  crédito, ele ordena uma fila para analistas com tempo limitado. A pergunta útil é: dos casos
  que o analista consegue revisar, quantos são fraude de verdade?"
- **"O que é dupla contagem, de forma simples?"** — "A taxa de inconsistência da região é
  calculada a partir das mesmas evidências que depois o modelo usa para avaliar o caso. É
  como ouvir o mesmo boato duas vezes e achar que são duas testemunhas."
- **"Na Figura 4 a linha de B sobe. Então B não resolve?"** — "Nessa configuração específica
  parece. Mas na grade inteira ela só atende ao critério em 33 de 48 casos (Figura 5), e as
  falhas estão concentradas nas condições da Figura 6. Além disso, a disparidade em B é cerca
  de três vezes a de A (Figura 7). Ela não reduz a desigualdade, muda quem paga por ela."
- **"Isso não é só Fellegi-Sunter, de 1969?"** — "O mecanismo de agregação é, sim. A
  contribuição não é o mecanismo, é a pergunta de onde a região entra, testada com critérios
  declarados antes e com uma reprovação real."
- **"Esse efeito de dado desigual gerando viés já não é conhecido?"** — "O mecanismo geral é,
  e citamos Akpinar, Lipton e Chouldechova (2024). O que este trabalho faz é aplicar ao caso
  em que a qualidade da fonte muda a especificidade de uma evidência, com dado dentro de um
  mesmo município e com a taxa de fraude igualada por construção."
- **"Vocês implementaram o RAG?"** — "Ainda não. Esta etapa avalia só a camada que agrega as
  evidências com Bayes, que é a base sobre a qual o RAG vai ser construído."

---

## Checklist antes da sessão

- [ ] Pôster impresso conferido: legendas numeradas de 1 a 7, sem textos duplicados.
- [ ] QR code das Referências testado no celular.
- [ ] Pitch de 1 minuto ensaiado em voz alta, cronometrado.
- [ ] Ressalva da cobertura estipulada dita por você, antes da pergunta.
- [ ] Números da fala iguais aos do pôster e aos de `relatorios/ledger_numeros.md`.
