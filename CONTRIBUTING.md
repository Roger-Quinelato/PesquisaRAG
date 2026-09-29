# Como contribuir

Regras de fluxo de trabalho do repositório. O idioma de trabalho é **português do Brasil**:
documentos, nomes de colunas, rótulos de figura, mensagens de commit, títulos de PR e issues.

## Branches

| Branch | Papel | Quem escreve |
|---|---|---|
| `main` | Versão estável. Cada merge aqui corresponde a uma entrega ou release (R1, R2…). | Só via PR vindo de `develop` (ou `hotfix/*`) |
| `develop` | Integração do trabalho do ciclo. É a base de todo branch novo. | Só via PR |
| `<tipo>/<card>-<descricao>` | Trabalho de uma tarefa. Nasce de `develop` e volta para `develop`. | O responsável pela tarefa |

Nome do branch de trabalho: tipo do commit principal, código do card no Trello e uma descrição
curta em minúsculas com hífens, sem acentos.

```
feat/d3t3-gerador-sintetico-v2
exp/d3t9-benchmark-inicial
docs/d4t1-revisao-bibliografica
fix/d3t7-ece-bins-vazios
hotfix/readme-link-quebrado      # único tipo que parte de main
```

Fluxo:

```bash
git switch develop && git pull
git switch -c feat/d3t3-gerador-sintetico-v2
# ... commits ...
git push -u origin feat/d3t3-gerador-sintetico-v2
# abrir PR para develop, citando a issue:  "Closes #32"
```

Para fechar uma release, abra um PR de `develop` para `main` e crie a tag `rN` no commit de merge.

## Convenção de commits

Formato baseado em [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/),
com a descrição em português:

```
<tipo>(<escopo opcional>): <descrição no imperativo, minúscula, sem ponto final>

<corpo opcional: o porquê da mudança, não o como>

Refs #<issue>   |   Closes #<issue>
```

| Tipo | Uso |
|---|---|
| `feat` | Funcionalidade nova no código (braço, métrica, módulo RAG…) |
| `fix` | Correção de erro no código ou em número publicado |
| `exp` | Experimento novo ou rodada de varredura que altera `resultados/` |
| `data` | Gerador, dataset, fontes de dados |
| `docs` | README, relatórios, CLAUDE.md, resumos |
| `fig` | Figuras e scripts de figura |
| `refactor` | Reorganização sem mudança de comportamento |
| `chore` | Infraestrutura: `.gitignore`, Docker, dependências, CI |

Escopos comuns: `gerador`, `bracos`, `metricas`, `varredura`, `equidade`, `relatorio`, `poster`.

Exemplos:

```
feat(bracos): adicionar braço B com RA na verossimilhança
fix(metricas): corrigir ECE quando o bin está vazio
exp(varredura): ampliar grade de beta para 8 níveis
docs(relatorio): registrar reprovação do critério de equidade
chore: adicionar Dockerfile mínimo

Refs #20
```

Regras:

- Um commit, uma mudança lógica. Não misture refatoração com mudança de resultado.
- Todo commit que altere um número citado em relatório ou resumo precisa dizer isso no corpo.
- Referencie a issue da tarefa (`Refs #N` no commit; `Closes #N` na descrição do PR).

## Pull requests

- Todo PR vai para `develop`, exceto releases (`develop` → `main`) e `hotfix/*` (→ `main`).
- Preencha o template (`.github/pull_request_template.md`).
- A verificação é a reexecução: se o PR mexe em `experimento/`, rode o pipeline duas vezes e
  confirme que os CSVs de `resultados/` são idênticos (ver `README.md`).
- Merge por *merge commit* (preserva o histórico da tarefa). Apague o branch após o merge.

## Issues e Trello

Cada card do quadro "PIDTI- RAG BAYNESIANO" tem uma issue correspondente. Épicos (`D1`…`D10`)
são issues com o rótulo `épico`, e as tarefas (`Dn.Tm`) são sub-issues do épico. Rótulos de
estado: `backlog`, `em andamento`. Quando um PR fecha a issue, mova o card para FINALIZADOS.

## Restrições

- Todos os dados são **sintéticos**. Não use para nenhuma decisão real de crédito.
- Datasets, planilhas, PDFs de artigos e resumos de congresso ficam fora do git (`.gitignore`).
- O experimento usa apenas `numpy`; não adicione scipy, sklearn, PyMC, SDV nem geradores
  ajustados a dados (ver `CLAUDE.md`).
