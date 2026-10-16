# D2.T2 — Estudo LxMLS Day 1: Naïve Bayes e classificadores lineares

**Objetivo.** Entender prior, verossimilhança, independência condicional e inferência em Naïve Bayes, relacionando-os à agregação probabilística usada na pesquisa. O LxMLS Day 1 oficial de 2026 é sobre classificadores lineares e inclui Naïve Bayes multinomial como exemplo; este guia dá ênfase aos conceitos explicitamente pedidos na tarefa.

## 1. Modelo e hipótese de independência

Seja Y uma classe e \(x=(x_1,\ldots,x_d)\) um vetor de características. Naïve Bayes aplica Bayes e aproxima a distribuição conjunta das características por

\[
P(Y=y\mid x)\propto P(Y=y)P(x\mid Y=y)
\approx P(Y=y)\prod_{j=1}^{d}P(x_j\mid Y=y).
\]

A hipótese “naïve” é independência condicional das características dado Y. Ela permite estimar cada distribuição separadamente, reduzindo a quantidade de parâmetros. Não afirma que as características sejam independentes no conjunto de dados sem condicionar à classe. Também não garante que a probabilidade prevista esteja calibrada.

Em features categóricas ou Bernoulli, cada fator é uma probabilidade de categoria ou presença/ausência. Para texto com contagens, Naïve Bayes multinomial modela as contagens de palavras condicionadas à classe. O suavizamento de Laplace evita probabilidade zero para um evento nunca visto no treino.

## 2. Cálculo em log-odds

Para duas classes, fraude \(F=1\) e não fraude \(F=0\), as odds posteriores são

\[
\frac{P(F=1\mid E)}{P(F=0\mid E)}
=\frac{P(F=1)}{P(F=0)}\;\frac{P(E\mid F=1)}{P(E\mid F=0)}.
\]

Sob independência condicional das evidências \(E_j\), o logaritmo vira soma:

\[
\operatorname{logit}P(F=1\mid E)
=\operatorname{logit}(\pi)+\sum_j\log\frac{P(E_j\mid F=1)}{P(E_j\mid F=0)}.
\]

Para uma evidência binária, presente contribui \(\log(s_j/f_j)\); ausente contribui \(\log((1-s_j)/(1-f_j))\). Aplicar a função logística \(\sigma(z)=1/(1+e^{-z})\) converte log-odds em probabilidade.

### Exemplo numérico didático

Use os parâmetros padrão da simulação: prior \(\pi=0{,}15\), sensibilidades \((0{,}65;0{,}70;0{,}60)\) e FPR global \((0{,}16;0{,}27825;0{,}16)\). Se as três evidências forem positivas, as odds posteriores são

\[
\frac{0{,}15}{0{,}85}\times\frac{0{,}65}{0{,}16}\times\frac{0{,}70}{0{,}27825}\times\frac{0{,}60}{0{,}16}\approx6{,}76,
\]

ou posterior aproximado \(6{,}76/(1+6{,}76)=0{,}871\). Esse cálculo ilustra o braço A, com FPR global, e é uma probabilidade sob o mecanismo didático, não uma estimativa de fraude real. Se a evidência de endereço for ausente, seu fator passa a \((1-0{,}70)/(1-0{,}27825)\), diminuindo as odds.

## 3. Conexão com o estudo de RAG Bayesiano

O braço A de `experimento/bracos.py` soma log-razões de verossimilhança com prior global. O braço B usa FPR de endereço específico da RA na verossimilhança. O braço C troca o prior global por um prior inferido da taxa observada de inconsistência da RA. O relatório encontrou dupla contagem no C: a mesma evidência que informa a verossimilhança ajuda a construir o prior regional.

Isso não é um resultado universal sobre prioris regionais. É um achado condicionado ao desenho sintético e ao modo como o prior C foi construído. Os valores de cobertura das RAs são estipulados, não medidos. A camada RAG ainda não foi integrada ou avaliada; portanto este material trata da agregação de evidências já extraídas, não da qualidade de recuperação documental.

### Independência e evidência duplicada

Independência condicional é uma aproximação/modelagem que deve ser justificada. Se duas flags forem derivadas da mesma fonte ou de uma evidência duplicada, multiplicar as duas razões como se fossem independentes pode contar a mesma informação duas vezes e inflar o posterior. Uma trilha de auditoria deve registrar a origem de cada sinal, dependências conhecidas, valores de prior e verossimilhança e versão do modelo.

No simulador atual, cada flag é gerada em sorteio Bernoulli separado condicionado a F e RA. Essa independência condicional está imposta pelo gerador, não verificada em dados reais. Em um sistema futuro, dependência de fontes e erros comuns precisam ser modelados e avaliados.

## 4. O que o Day 1 oficial acrescenta

O guia LxMLS 2026 apresenta modelos lineares em que o score é uma função afim das features e a decisão separa classes por uma fronteira linear. Naïve Bayes multinomial também pode ser escrito como classificador linear: em log-probabilidade, cada palavra soma um peso por classe e um termo de prior. O que distingue o modelo é a derivação probabilística e a hipótese de independência, mesmo quando a regra final tem forma linear.

Uma probabilidade posterior e um score linear não são conceitos intercambiáveis. O score precisa de uma transformação e de um modelo probabilístico especificado para ser interpretado como probabilidade. Calibração deve ser medida separadamente, por exemplo com Brier e ECE, já usados no repositório.

## 5. Exercícios de checagem

1. Escreva a fatoração naïve para três evidências condicionadas a F.
2. Para \(\pi=0{,}20\), uma evidência presente tem sensibilidade 0,8 e FPR 0,1. Calcule a probabilidade posterior.
3. O que ocorre com a hipótese de independência se duas flags vêm da mesma consulta documental duplicada?
4. Por que um Naïve Bayes pode classificar bem e ainda produzir probabilidades mal calibradas?
5. Explique por que o resultado do braço C não prova que todo prior regional é inadequado.

<details><summary>Respostas</summary>

1. \(P(E_1,E_2,E_3\mid F)=\prod_jP(E_j\mid F)\), analogamente para não F. 2. \(0{,}8\cdot0{,}2/(0{,}8\cdot0{,}2+0{,}1\cdot0{,}8)=2/3\). 3. As flags são dependentes; tratá-las como independentes duplica evidência. 4. A hipótese de independência pode distorcer as probabilidades conjuntas e a confiança prevista, embora o modelo ainda possa classificar bem; discriminação e calibração são propriedades diferentes. 5. O C usa prior estimado da mesma taxa de inconsistências que depois informa a verossimilhança, e o achado se limita a essa construção e ao mecanismo simulado.

</details>

## Referências e relação com o código

- LxMLS, [Day 1 — Linear Classifiers (2026)](https://lxmls.it.pt/2026/guide/day1.html): classificadores lineares, Naïve Bayes multinomial e suavizamento.
- LxMLS, [Day 0 — Basic Tutorials (2026)](https://lxmls.it.pt/2026/guide/day0.html): probabilidade e fundamentos matemáticos.
- Código: [`experimento/bracos.py`](../experimento/bracos.py), [`experimento/gerador.py`](../experimento/gerador.py), [`experimento/metricas.py`](../experimento/metricas.py).
- Resultados e limites: [`Relatorio_Tecnico_RAG_Bayesiano.md`](Relatorio_Tecnico_RAG_Bayesiano.md) e [`README.md`](../README.md).

**Critério de conclusão do estudo:** conseguir atualizar odds com prior e razões de verossimilhança, explicar a hipótese de independência condicional e apontar um risco de dependência entre evidências no pipeline.
