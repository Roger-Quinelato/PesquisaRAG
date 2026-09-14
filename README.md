# Pesquisa RAG Bayesiano — Triagem Explicável de Inconsistências Cadastrais

Pesquisa de Iniciação Científica sobre triagem explicável de inconsistências cadastrais e
documentais em análise de crédito no DF/RIDE, combinando recuperação de evidências (RAG),
tipificação simbólica e inferência bayesiana. O repositório reúne a proposta PIDTI, o
experimento de simulação causal, os dados sintéticos, os relatórios técnicos e os resumos
submetidos a congresso.

Guia de trabalho completo (ambiente, comandos, convenções, achados verificados): `CLAUDE.md`.

## Arquivos principais

| Arquivo/pasta | Conteúdo |
|---|---|
| `dataset_sintetico_v2.csv` | **Dataset em uso.** 5.000 casos com `fraude_latente` separada das evidências observáveis |
| `dataset_sintetico_500_casos.csv` | **Legado, defeituoso** — as flags de evidência reproduzem o `ground_truth` por construção. Ver "Dataset legado" no `CLAUDE.md`. Não usar para comparar abordagens |
| `experimento/` | `gerador.py` (mecanismo causal), `bracos.py` (seis abordagens), `metricas.py`, `varredura.py`, `equidade.py`, `figuras.py`, `exportar_dataset.py` |
| `relatorios/` | Relatório técnico, benchmark de estado da arte, parecer do CTO, ledger de números auditados e guia das figuras |
| `Proposta_PIDTI_RAG_Bayesiano2.pdf` | Proposta PIDTI: hipóteses H1–H3, arquitetura em 4 camadas, cronograma, referências |
| `fontes_oficiais.csv` | 7 fontes oficiais (Receita Federal, Geoportal/SEDUH, BCB/SCR) com URL e uso pretendido |
| `base_paper_rag_bayesiano.xlsx` | Fontes, dataset, schema e desenho experimental original (parcialmente superado pelo `experimento/`) |
| `Resumo Congresso IC UnB - RAG Bayesiano.md` | Resumo desta pesquisa submetido a congresso |
| `Resumo Congresso IC UnB - Modelo Preditivo.md` | Resumo de IC anterior — modelo de formato e de registro para resumos novos |

## Reproduzir o experimento

Determinístico por semente, ~8 minutos:

```bash
python experimento/varredura.py && python experimento/equidade.py && python experimento/figuras.py
```

Dependências: apenas `numpy` e `matplotlib`. Não há build, lint nem suíte de testes — a
verificação é a reexecução (rodar duas vezes e comparar os CSVs, que devem ser idênticos).
Detalhes de ambiente e comandos adicionais (regerar dataset, extrair texto do PDF da proposta)
estão em `CLAUDE.md`.

## Principais achados verificados

Ver `CLAUDE.md` (seção "Achados verificados") e `relatorios/ledger_numeros.md` para os números
auditados e a grade completa de configurações. Resumo:

- A variante bayesiana sem território não supera a tabela empírica de forma relevante.
- Condicionar o *prior* à taxa observada da região é dominado em 224/224 configurações, em
  Brier e em ECE — o mecanismo é dupla contagem (double dipping).
- Com taxa de fraude idêntica por construção entre Regiões Administrativas e nenhuma variável
  demográfica no modelo, a discriminação territorial emerge sozinha a partir da qualidade
  desigual da fonte de endereço.
- Mover a Região Administrativa para a verossimilhança melhora a acurácia de forma modesta, mas
  **não corrige a inequidade de forma robusta** sob o critério pré-registrado.
- Conclusão que orienta as próximas fases: enquanto a cobertura cadastral variar entre Regiões
  Administrativas, qualquer sistema que use endereço como evidência penalizará quem mora onde o
  registro é pior — inclusive os construídos para serem neutros. Medir e publicar a cobertura
  cadastral por RA é requisito de governança.

## Importante — uso restrito a pesquisa

Todos os identificadores, empresas, endereços e valores dos datasets são **sintéticos**. Não
use nenhum arquivo deste repositório para concessão, negação ou qualquer decisão real de
crédito. O objetivo é exclusivamente pesquisa experimental em cenários controlados.
