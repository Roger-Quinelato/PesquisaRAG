# Protocolo de versionamento e reprodutibilidade

Card D1.T5 (issue #21). Estabelece o que é versionado, como cada artefato é reproduzido e como se
verifica que um número publicado ainda se sustenta.

O princípio que orienta tudo: **o código e as sementes são a fonte da verdade. Dados sintéticos,
resultados e figuras são derivados**, e por isso não se versionam; eles se regeneram.

## 1. O que entra no git

| Artefato | Versionado? | Onde | Por quê |
|---|---|---|---|
| Código do experimento | Sim | `experimento/` | Fonte da verdade |
| Código do sistema | Sim | `src/` | Fonte da verdade |
| Testes | Sim | `tests/` | Garantem as propriedades do gerador e das métricas |
| Protocolos e relatórios (`.md`) | Sim | `docs/`, `relatorios/` | O `.md` é a fonte; o `.docx` é derivado |
| Tabelas de apoio dos relatórios | Sim | `relatorios/tabelas/` | Recortes pequenos, citados no texto |
| Figuras do pôster | Sim | `figuras/poster_*.png`, `figuras/fig4_heatmap_beta_pi.png` | O README as exibe |
| Resultados da varredura | **Não** | `resultados/` | Regeneráveis (§3) |
| Demais figuras | **Não** | `figuras/` | Regeneráveis |
| Datasets sintéticos | **Não** | raiz ou `data/sintetico/` | Regeneráveis por semente (§2) |
| Dados de fontes oficiais | **Não** | `data/raw/` | Tamanho e termos de uso; registrar a proveniência (§2.2) |
| Artigos em PDF, planilhas, resumos de congresso | **Não** | local | Direitos autorais e documentos internos |

Exceção explícita: para fixar a versão exatamente submetida de um documento derivado, use
`git add -f` (por exemplo, `git add -f relatorios/Relatorio_Tecnico.docx`) e cite o motivo no commit.

## 2. Dados

### 2.1 Dados sintéticos

Um dataset sintético é identificado por **(versão do código do gerador, parâmetros, semente, n)**,
e não pelo arquivo. Para citar um dataset, cite essa tupla e o commit.

| Dataset | Comando | Semente | Parâmetros |
|---|---|---|---|
| `dataset_sintetico_v2.csv` | `python experimento/exportar_dataset.py 5000` | `20260907` | `Params()` padrão (π = 0,15; `f_base` = 0,16; β = 0,55) |

Regras:

- **Mudou o mecanismo em `gerador.py` → nova versão do dataset** (`v3`, …). Nunca sobrescreva uma
  versão citada em relatório com um mecanismo diferente.
- Ao gerar uma versão nova, **confira a divergência entre `OR(evidências)` e `fraude_latente`**.
  Precisa ser substancial (a v2 tem 41,5%). Se der 0%, o gerador repetiu o defeito do dataset
  legado. O teste `test_rotulo_latente_nao_e_funcao_das_evidencias` já cobre isso.
- Formato: `;` como delimitador, UTF-8 **com** BOM, decimal com ponto.
- `dataset_sintetico_500_casos.csv` é **legado e defeituoso** (ver `CLAUDE.md`). Não use para
  comparar abordagens.

### 2.2 Dados reais (fontes oficiais)

Quando entrarem (por exemplo, a cobertura cadastral por RA do Geoportal/SEDUH, que hoje é
**estipulada** em `gerador.COBERTURA`), cada extração em `data/raw/` precisa de um registro em
`data/raw/PROVENIENCIA.md`:

```
arquivo: data/raw/<nome>
fonte: <órgão, sistema, URL>
data_extracao: AAAA-MM-DD
consulta: <filtros ou parâmetros usados>
sha256: <hash do arquivo>
licenca: <termos de uso>
```

O registro é versionado, mas o arquivo não. Qualquer pessoa consegue verificar se tem o mesmo dado
comparando o hash.

## 3. Experimentos e sementes

| Script | Sementes | Casos por semente | Saída |
|---|---|---|---|
| `varredura.py` | `range(8)` | 40.000 | `resultados/varredura.csv`, `resultados/fpr_por_ra.csv` |
| `equidade.py` | `range(8)` | 40.000 | `resultados/equidade.csv` |
| `exportar_dataset.py` | `20260907` | 5.000 (padrão) | `dataset_sintetico_v2.csv` |

Regras:

- **Toda aleatoriedade passa por `np.random.default_rng(semente)`**, criado explicitamente e
  passado adiante. Não use `np.random.seed`, `np.random.rand` nem o `random` da biblioteca padrão.
- Semente, grade e tamanho de amostra ficam **declarados no topo do script**, como constantes, e
  nunca vêm de argumentos com valor padrão escondido.
- Mudar sementes, grade ou `N` muda os números publicados. Isso exige:
  1. commit `exp(...)` explicando a mudança;
  2. reexecução completa;
  3. atualização de `relatorios/ledger_numeros.md` e dos textos que citam os números.
- **Critérios de aceitação são declarados antes de rodar** (ver
  [`protocolo_experimental_v1.md`](protocolo_experimental_v1.md)). Alterar um critério depois de
  ver o resultado não é permitido; o que se faz é registrar um critério novo, com data.

Formato dos CSVs de `resultados/`: vírgula como delimitador, UTF-8 **sem** BOM
(`encoding="utf-8"`). É diferente dos datasets (§2.1), e a diferença é intencional.

## 4. Resultados e números publicados

- **Nenhum número entra em relatório, resumo ou pôster sem uma linha em
  `relatorios/ledger_numeros.md`** com arquivo, coluna e filtro que o reproduzem.
- A manchete de cada afirmação é a **mediana sobre a grade completa**. A configuração de
  referência só aparece como ilustração, e rotulada como tal.
- Número que não se reproduz sai do texto e vai para a seção de números não sustentados do ledger.
  Já aconteceu com o "+0,64 p.p.", ver `CLAUDE.md`.

## 5. Modelos

O experimento não tem artefato treinado: os "modelos" (braços) são funções fechadas dos parâmetros
do gerador, definidas em `experimento/bracos.py`. Versionar o código é versionar o modelo.

Quando o sistema tiver componentes com estado (índice vetorial do RAG, parâmetros estimados do
motor bayesiano):

- o artefato **não** vai para o git; vai para uma release do GitHub ou armazenamento externo;
- o git guarda um manifesto (`src/<componente>/MANIFESTO.md`) com a versão do código, os dados de
  entrada (pela tupla do §2.1 ou pelo hash do §2.2), a semente e o sha256 do artefato;
- **gerador ajustado a dados não é permitido**. Destruiria a verificabilidade da calibração, que
  depende de conhecer os parâmetros verdadeiros (ver `CLAUDE.md`).

## 6. Releases

Cada relatório parcial corresponde a uma release:

| Release | Entrega | Card |
|---|---|---|
| `r1` | Primeiro Relatório Parcial | D4.T5 (#44) |
| `r2` | Segundo Relatório Parcial | D6 (#11) |
| `r3` | Terceiro Relatório Parcial | D8 (#13) |

Para fechar uma release:

1. PR de `develop` para `main`.
2. Rodar `python -m unittest discover tests` e o pipeline completo **duas vezes**; os CSVs de
   `resultados/` precisam ser byte a byte idênticos.
3. Criar a tag anotada `rN` no commit de merge:
   `git tag -a r1 -m "Relatório Parcial 1"` e depois `git push origin r1`.
4. Anexar à release do GitHub os CSVs de `resultados/` e o `.docx` submetido. Assim a release
   carrega os derivados sem que eles entrem no histórico.

## 7. Ambiente

| Item | Valor atual |
|---|---|
| Python | 3.x no Windows 11, via PowerShell |
| Experimento | só `numpy` |
| Figuras | `matplotlib`, `pandas`, `seaborn` |
| Testes | `unittest` (biblioteca padrão), sem dependência extra |

A fixação de versões (`requirements.txt` ou `pyproject.toml`) e a imagem Docker são escopo dos
cards D1.T3 (#19) e D1.T4 (#20). Até lá, registre no relatório as versões de `numpy` e
`matplotlib` usadas na execução que gerou os números.

## 8. Checklist de verificação

Antes de citar um resultado ou fechar uma release:

- [ ] `python -m unittest discover tests` passa.
- [ ] O pipeline rodado duas vezes produz CSVs idênticos (`fc /b` no Windows, `cmp` no Linux).
- [ ] Todo número do texto tem linha no ledger.
- [ ] O commit que gerou os resultados está identificado (hash ou tag).
