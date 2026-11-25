# D2.T1 — Estudo LxMLS Day 0: fundamentos matemáticos

**Objetivo.** Reunir o mínimo de álgebra linear, probabilidade, máxima verossimilhança (MLE) e prioris conjugadas necessário para ler os modelos do projeto e acompanhar os materiais do LxMLS. Este texto é um guia de estudo aplicado; não substitui as aulas nem afirma reproduzir o roteiro oficial.

## 1. Álgebra linear para representar evidências

Um vetor guarda as características de um caso. No experimento, as três evidências binárias são \(E=(E_1,E_2,E_3)\), com status, endereço e valor. Uma matriz \(X\in\mathbb R^{n\times p}\) reúne n casos e p características, uma linha por caso.

O produto interno \(w^Tx=\sum_jw_jx_j\) combina características em um escore. Em um classificador linear, \(s(x)=w^Tx+b\); o escore não é automaticamente uma probabilidade. O produto matricial \(Xw\) calcula os escores de todos os casos de uma vez. A norma euclidiana \(\|w\|_2=\sqrt{\sum_jw_j^2}\) mede o tamanho do vetor e aparece em regularização.

**Aplicação aqui.** `experimento/bracos.py` soma contribuições por evidência na escala logarítmica. A soma dos logaritmos de razões de verossimilhança equivale ao logaritmo do produto dessas razões; cada evidência adiciona uma contribuição interpretável.

## 2. Probabilidade: eventos, condicionamento e Bayes

Para eventos A e B, a regra do produto é \(P(A,B)=P(A\mid B)P(B)\). Se A e B são independentes, \(P(A\mid B)=P(A)\), logo \(P(A,B)=P(A)P(B)\). Independência é uma hipótese sobre a distribuição, não uma consequência de observar variáveis diferentes.

Se \(H\) é uma hipótese e \(E\) uma evidência, Bayes dá

\[
P(H\mid E)=\frac{P(E\mid H)P(H)}{P(E)},\qquad
P(E)=\sum_hP(E\mid h)P(h).
\]

O prior \(P(H)\) representa a incerteza antes da evidência; a verossimilhança \(P(E\mid H)\) diz quão provável seria a evidência sob cada hipótese; o posterior \(P(H\mid E)\) é a distribuição atualizada. Não confundir \(P(E\mid H)\) com \(P(H\mid E)\).

**Exemplo de prevalência.** Se 1% dos casos têm um evento, um sinal aparece em 90% dos eventos e em 10% dos demais, então \(P(H\mid E)=0{,}9\cdot0{,}01/(0{,}9\cdot0{,}01+0{,}1\cdot0{,}99)\approx8{,}3\%\). Mesmo um sinal útil não torna o evento provável quando ele é raro.

## 3. Verossimilhança e máxima verossimilhança

Para observações \(x_1,\ldots,x_n\) e parâmetro \(\theta\), a verossimilhança é \(L(\theta)=\prod_i p(x_i\mid\theta)\). Maximizar o logaritmo, \(\ell(\theta)=\sum_i\log p(x_i\mid\theta)\), é equivalente e transforma produtos em somas, numericamente mais estáveis.

Para dados Bernoulli com k sucessos em n observações, \(L(p)=p^k(1-p)^{n-k}\). Derivando o log da verossimilhança e igualando a zero, obtém-se \(\hat p_{MLE}=k/n\). É a proporção observada. Com poucos dados pode resultar em 0 ou 1, confiança excessiva que a inferência bayesiana pode regularizar.

No projeto, sensibilidade e taxa de falso positivo são probabilidades condicionais de uma evidência binária: por exemplo, \(s_j=P(E_j=1\mid F=1)\) e \(f_j=P(E_j=1\mid F=0)\). Os valores do gerador são parâmetros estipulados para simulação, não estimativas de pessoas ou dados reais.

## 4. Prior conjugado: Beta–Bernoulli

Se \(p\) é desconhecido e cada observação é Bernoulli, escolha \(p\sim\mathrm{Beta}(\alpha,\beta)\), cuja densidade é proporcional a \(p^{\alpha-1}(1-p)^{\beta-1}\). Após k sucessos e n−k falhas,

\[
p\mid x_{1:n}\sim\mathrm{Beta}(\alpha+k,\;\beta+n-k).
\]

A família Beta é conjugada à Bernoulli porque a distribuição posterior permanece Beta. A média posterior é \((\alpha+k)/(\alpha+\beta+n)\): equivale a combinar contagens observadas com pseudo-contagens do prior. Com prior uniforme Beta(1,1), 0 sucessos em 0 observações mantém média 0,5; com dados, a influência relativa do prior diminui.

Conjugação torna a atualização fechada e simples, mas não garante que o prior ou o modelo estejam bem especificados. O resultado depende das hipóteses adotadas.

## 5. Do modelo simples ao experimento

No gerador do repositório, \(F\sim\mathrm{Bernoulli}(\pi)\), com \(\pi=0{,}15\) na configuração padrão. As evidências são geradas condicionalmente a F; a taxa de falso positivo do endereço também depende da RA. O vetor de cobertura territorial é explicitamente estipulado, não medido. Por isso os valores do experimento demonstram consequências do mecanismo simulado, não taxas empíricas do DF.

Uma boa leitura de qualquer equação do projeto deve identificar: variável aleatória, evento observado, parâmetro, condicionamento, unidade de análise e hipótese de independência. Para este modelo, a independência relevante é condicional: as evidências são sorteadas separadamente dado F e a RA no mecanismo; isso não implica independência marginal depois de ocultar F.

## 6. Exercícios de checagem

1. Em 20 observações Bernoulli, há 6 sucessos. Qual é o MLE de p?
2. Com prior Beta(2,3), os mesmos dados produzem qual posterior e média posterior?
3. Explique por que \(P(E\mid F)\) não é, em geral, igual a \(P(F\mid E)\).
4. Por que as evidências podem estar dependentes marginalmente, embora sejam geradas de modo independente condicionado a F?

<details><summary>Respostas</summary>

1. \(6/20=0{,}30\). 2. Beta(8,17), média \(8/25=0{,}32\). 3. Bayes também depende da prevalência e da probabilidade total de E. 4. A variável latente compartilhada F induz associação ao misturar populações com diferentes probabilidades de evidência.

</details>

## Referências e relação com o código

- LxMLS, [Day 0 — Basic Tutorials (2026)](https://lxmls.it.pt/2026/guide/day0.html): probabilidade, álgebra linear e otimização numérica como fundamentos.
- Bishop, C. M. *Pattern Recognition and Machine Learning*, cap. 2 (distribuições de probabilidade) e cap. 3 (modelos lineares).
- Código aplicado: [`experimento/gerador.py`](../experimento/gerador.py), [`experimento/bracos.py`](../experimento/bracos.py) e [`experimento/metricas.py`](../experimento/metricas.py).
- Escopo e limitações: [`Relatorio_Tecnico_RAG_Bayesiano.md`](Relatorio_Tecnico_RAG_Bayesiano.md). Todos os dados são sintéticos; não usar em decisões reais de crédito.

**Critério de conclusão do estudo:** conseguir resolver os quatro exercícios e explicar, sem consultar o texto, prior, verossimilhança, posterior e a diferença entre independência condicional e marginal.
