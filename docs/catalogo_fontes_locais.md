# Catálogo de fontes de dados locais

Card D3.T1. Lista as fontes oficiais que podem substituir o vetor `COBERTURA` de `gerador.py`
(hoje **estipulado**, não medido) e alimentar a fase RAG. Cada linha diz o que foi **verificado**
e o que ainda **não foi**.

**Estado em 25/11/2026: nenhum dado foi baixado, e nenhum valor de cobertura foi medido.** Uma
busca de fontes (três consultas) não encontrou um indicador publicado de "cobertura do cadastro
territorial por RA". O que existe são camadas geográficas e relatórios de regularização, dos quais
a cobertura teria de ser **derivada** (ver `matriz_qualidade_fontes.md`). Nenhum número deste
documento vem da base; os fatos abaixo são os que as páginas consultadas afirmam.

## 1. Fontes candidatas

| # | Fonte | Órgão | O que oferece (verificado na página) | O que NÃO foi verificado | Uso previsto |
|---|---|---|---|---|---|
| F1 | Geoportal | SEDUH/DF | Banco de dados interno da SEDUH disponibilizado ao público; camadas como "CADASTRO TERRITORIAL > Lotes Registrados" (campo "Norma Vigente") e "LIMITES > Regiões Administrativas" | Se há download em lote por camada, formato, licença e data de atualização; se a camada de lotes registrados cobre todo o DF | Numerador/denominador da cobertura por RA |
| F2 | Portal da Regularização | SEDUH/DF | Cadastro de núcleos urbanos em regularização; o diagnóstico do IPE-DF cita 428 núcleos cadastrados, apresentados por RA | Se os núcleos têm geometria e área baixáveis; critério de entrada no portal | Área/lotes ainda não regularizados por RA |
| F3 | Diagnóstico da regularização fundiária urbana no DF | IPE-DF | Sumário executivo (2023) com mapa de núcleos por RA; **lido, ver §1.1: insuficiente** | O texto completo do diagnóstico, que pode ter a tabela por RA | Triangular com F1/F2 |
| F4 | Dicionário de dados de parcelamentos do solo | SEDUH/DF | Dicionário dos shapefiles de parcelamento | Se as camadas descritas são públicas | Definir campos |
| F5 | PDAD 2021 | IPE-DF (ex-Codeplan) | Pesquisa por amostra, 100 mil domicílios sorteados, cerca de 31 mil respondentes, **33 RAs**, microdados com dicionário de variáveis | Se existe variável de regularidade do endereço; o dicionário de 2021 não foi lido (só o de 2018, com a variável de RA) | Contexto socioeconômico; **não** cobertura |
| F6 | Dados abertos do GDF / dados.gov.br | vários | Um relatório da SEDUH afirma que os vetoriais também estão em dados.gov.br, mas "o acesso deve ser solicitado" | Quais conjuntos e se o pedido é necessário | Via alternativa a F1 |
| F7 | Receita Federal, BCB/SCR | federais | Listadas em `fontes_oficiais.csv` (local) | Fora do escopo da cobertura territorial | Fase RAG (D5) |

Links (consultados em 25/11/2026):

- Diagnóstico da regularização fundiária urbana no DF (IPE-DF):
  https://ipe.df.gov.br/documents/d/ipedf/sumario-executivo-diagnostico-da-regularizacao-fundiaria-urbana-no-distrito-federal-pdf
- Dicionário de dados de parcelamentos (SEDUH):
  https://parcelamentosdosolo.seduh.df.gov.br/docs/desdobro/modelos/modelo/shapefile/01)%20DICION%C3%81RIO%20DE%20DADOS%20(PDF).pdf
- Geoportal SEDUH: `geoportal.seduh.df.gov.br/mapa` (citado em estudo técnico da SEDUH; não foi
  aberto nesta etapa)
- PDAD 2021 (IPE-DF):
  https://ipe.df.gov.br/documents/d/ipedf/apresentacao_pdad-df_2021-pdf

## 1.1 Tentativa de extração: sumário do IPE-DF (F3), 25/11/2026

O sumário executivo (10 páginas, **Brasília, 2023**) foi baixado e lido. O texto confirma 428
núcleos urbanos no Portal da Regularização (194 de interesse social, 220 de interesse específico,
17 não indicados), mas os números **por RA** estão num mapa, em imagem. Lidos no mapa, com rótulo
legível, para as 8 RAs do experimento:

| RA | Núcleos urbanos | % dos 428 |
|---|---|---|
| Gama | 31 | 7,2% |
| Sobradinho | 24 | 5,6% |
| Ceilândia | 19 | 4,4% |
| Plano Piloto, Águas Claras, Guará, Taguatinga, Samambaia | sem rótulo no mapa | — |

**Conclusão: esta fonte não serve para medir `c_r`.** Três razões:

1. cinco das oito RAs não têm valor legível (não dá para distinguir zero de omissão);
2. é contagem de **núcleos**, sem lotes nem domicílios, então não se normaliza por tamanho: uma
   RA com 19 núcleos grandes pode ter mais lotes irregulares que outra com 31 pequenos;
3. o sumário não define nenhum indicador de cobertura do cadastro. Os dados são do Portal da
   Regularização em 2022/2023, e o próprio estudo recomenda registrar datas de atualização.

Não use esses três números como evidência a favor ou contra a ordenação estipulada em
`gerador.COBERTURA` (em que Ceilândia tem a pior cobertura): contagem não normalizada não decide
isso. O texto completo do diagnóstico (`www.ipe.df.gov.br`) pode ter a tabela por RA; **não foi
lido**.

## 2. Discrepância que precisa ser resolvida: 8 RAs contra 33

O gerador usa **8 RAs** (Plano Piloto, Águas Claras, Guará, Taguatinga, Gama, Sobradinho,
Samambaia, Ceilândia). O DF tem **33 RAs** na delimitação oficial usada pela PDAD 2021. Duas
opções, a decidir antes de medir:

1. manter as 8 e medir só nelas (comparável a todos os resultados publicados até aqui);
2. migrar para as 33 (mais realista, mas muda a grade, o gerador e todos os números, e exige
   nova versão do dataset, `v3`, e novo protocolo).

Recomendação: **opção 1 para o Relatório Parcial 1** e opção 2 como parte do protocolo v2.

## 3. Próximos passos (exigem acesso ao Geoportal, que esta etapa não teve)

1. Abrir o Geoportal e confirmar, para F1, o download das camadas "Lotes Registrados" e
   "Regiões Administrativas" (formato, licença, data).
2. Se o download não for público, registrar o pedido via dados.gov.br ou e-SIC e anexar o
   protocolo.
3. Baixar para `data/raw/` (fora do git) e registrar cada arquivo em `data/raw/PROVENIENCIA.md`
   no formato de `protocolo_versionamento.md` §2.2: arquivo, fonte, data, consulta, sha256,
   licença.
4. Calcular a cobertura conforme a definição de `matriz_qualidade_fontes.md` e só então
   substituir `gerador.COBERTURA`, criando nova versão do dataset.
