# Pacote inicial — RAG Bayesiano para Detecção Explicável de Inconsistências Documentais

Este pacote foi preparado como base de um estudo preliminar/short paper.

## Arquivos
- `dataset_sintetico_500_casos.csv`: 500 casos controlados com ground truth conhecido.
- `fontes_oficiais.csv`: fontes oficiais da Receita Federal, Geoportal/SEDUH e Banco Central.
- `base_paper_rag_bayesiano.xlsx`: workbook com fontes, dataset, schema e desenho experimental.

## Uso recomendado
1. Use o dataset sintético como base principal do experimento.
2. Use CNPJ/Receita e Geoportal como fontes externas de evidência quando necessário.
3. Use as normas do Banco Central como corpus textual do RAG.
4. Compare pelo menos:
   - regras simples;
   - RAG;
   - RAG + Bayes.
5. Métricas mínimas:
   - Precision / Recall / F1;
   - Brier Score;
   - calibração;
   - rastreabilidade das evidências.

## Importante
Os identificadores, empresas, endereços e valores do dataset são sintéticos.
Não use este arquivo para concessão, negação ou decisão real de crédito.
O objetivo é apenas pesquisa experimental e detecção de inconsistências em cenários controlados.

## Escopo sugerido do short paper
Pergunta:
"Agregação bayesiana de evidências recuperadas por RAG melhora a calibração e a rastreabilidade na detecção de inconsistências documentais?"

Corpus inicial:
- Resolução CMN nº 5.037/2022;
- normas e leiautes do SCR;
- dados cadastrais/territoriais usados apenas como referência de evidência.

Gerado em 2026-09-06.
