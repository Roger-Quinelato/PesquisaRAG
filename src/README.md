# `src/` — código do sistema

Reservado para o código do sistema de triagem, separado do experimento de simulação
(`experimento/`). Ainda vazio: os módulos entram nas fases seguintes do projeto.

| Módulo previsto | Épico |
|---|---|
| `src/rag/` — corpus, indexação vetorial, recuperação e proveniência das evidências | D5 (#10) |
| `src/motor/` — motor bayesiano: agregação das evidências e posterior calibrado | D7 (#12) |
| `src/xai/` — explicação, rastreabilidade e encaminhamento a revisão humana | D9 (#14) |

`experimento/` continua sendo o lugar do mecanismo gerador, dos braços e da varredura. Quando um
braço virar componente do sistema (por exemplo, o motor `B`), a implementação passa para `src/` e o
experimento passa a importá-la de lá.
