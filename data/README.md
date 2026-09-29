# `data/` — dados

Nenhum dado é versionado no git. Esta pasta existe para organizar os arquivos **na máquina local**.

| Subpasta | Conteúdo | Versionado? |
|---|---|---|
| `data/raw/` | Extrações de fontes oficiais (Receita Federal, Geoportal/SEDUH, BCB/SCR), como baixadas | Não |
| `data/interim/` | Dados intermediários de limpeza | Não |
| `data/sintetico/` | Datasets sintéticos gerados por `experimento/exportar_dataset.py` | Não (regeneráveis por semente) |

Todos os identificadores são **sintéticos**. Não use nada daqui para decisão real de crédito.

As regras de versionamento, proveniência e verificação estão em
[`docs/protocolo_versionamento.md`](../docs/protocolo_versionamento.md).
