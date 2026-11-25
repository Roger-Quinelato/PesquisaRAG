# Matriz de qualidade das fontes

Card D3.T2. Define **o que significa "cobertura cadastral" de uma RA** de modo medível, avalia as
fontes do catálogo (`catalogo_fontes_locais.md`) contra critérios de qualidade e registra o que
fica estipulado até a medição.

## 1. Definição operacional (proposta, ainda não validada com a orientação)

No gerador, a taxa de falso positivo da evidência de endereço é
`f_endereço(r) = f_base + β·(1 − c_r)`, onde `c_r` é a **cobertura do cadastro territorial** da
RA `r`: a probabilidade de que um endereço **correto** de um solicitante daquela RA seja
localizado no cadastro. Medir `c_r` diretamente exigiria testar endereços reais, o que não temos.
A proposta é aproximá-la por uma **razão de regularidade**:

```
c_r ≈ lotes_registrados(r) / (lotes_registrados(r) + lotes_em_nucleos_nao_regularizados(r))
```

com numerador de F1 ("Lotes Registrados") e denominador acrescido dos lotes dos núcleos urbanos
ainda em regularização (F2/F3). Limites conhecidos desta aproximação, que precisam ir para o
texto de qualquer resultado que a use:

- mede **regularidade fundiária**, e não a probabilidade de o endereço ser achado: é um proxy;
- a contagem de lotes por núcleo pode não existir em F2/F3 (pode haver só área ou número de
  núcleos), e nesse caso a razão seria por área, não por lote;
- a sensibilidade do resultado a `c_r` é mapeada pela varredura de β, mas **não** por uma
  ordenação errada das RAs: se a ordenação medida diferir da estipulada, os resultados
  territoriais mudam de natureza e precisam ser refeitos.

## 2. Critérios de qualidade

| Critério | Pergunta |
|---|---|
| Cobertura territorial | A fonte abrange todas as RAs do experimento? |
| Atualidade | Qual a data de referência, e quanto tempo desde a última atualização? |
| Granularidade | Chega ao lote/endereço ou só ao núcleo/RA? |
| Acesso e licença | Download aberto? A licença permite uso em pesquisa e registro de software? |
| Reprodutibilidade | Dá para registrar versão, data e sha256 (`protocolo_versionamento.md` §2.2)? |
| Viés de origem | Quem produz o dado e para quê? A fonte sub-registra justamente as áreas de interesse? |

## 3. Avaliação (25/11/2026)

`?` = não verificado nesta etapa. Nenhuma célula foi preenchida por inferência.

| Fonte | Território | Atualidade | Granularidade | Acesso/licença | Reprodutível | Viés de origem |
|---|---|---|---|---|---|---|
| F1 Geoportal (Lotes Registrados) | `?` | `?` | lote (pela descrição da camada) | `?` | `?` | Cadastro oficial; tende a ser pior justamente onde há ocupação irregular, o que **é** o fenômeno medido |
| F2 Portal da Regularização | todo o DF (por RA, segundo o IPE) | `?` | núcleo urbano | `?` | `?` | Só inclui núcleos que entraram no processo |
| F3 Diagnóstico IPE-DF (sumário) | 3 de 8 RAs legíveis no mapa | 2023 | núcleo urbano, sem lotes | PDF público | sim (PDF datado) | Estudo pontual, não série; só núcleos que entraram no Portal. **Insuficiente para `c_r`** (catálogo §1.1) |
| F5 PDAD 2021 | 33 RAs | 2021 | domicílio (amostra) | microdados com dicionário | `?` | Amostral; erro de amostragem em RA pequena |

## 4. O que fica estipulado até a medição

`gerador.COBERTURA = (0,97; 0,94; 0,90; 0,84; 0,76; 0,70; 0,62; 0,55)` continua **estipulado** e
assim deve ser rotulado em qualquer relatório, pôster ou resumo. Quando a medição existir:

1. nova versão do dataset (`v3`) e do protocolo (`protocolo_experimental_v2.md`);
2. critérios de aceitação **declarados antes** de rodar com o vetor medido;
3. relato explícito de se a ordenação medida coincide com a estipulada, porque as conclusões
   territoriais dependem dela.
