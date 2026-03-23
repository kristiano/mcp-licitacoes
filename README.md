# mcp-brasil

MCP servers para APIs públicas brasileiras.

Um único pacote Python que conecta AI agents (Claude, GPT, etc.) a dados governamentais do Brasil: IBGE, Banco Central, Portal da Transparência, Câmara dos Deputados, Senado Federal, DataJud e mais.

## Quick Start

```bash
# Instalar
git clone https://github.com/seu-usuario/mcp-brasil.git
cd mcp-brasil
make dev

# Rodar server (stdio)
make run

# Rodar via HTTP (:8000)
make serve
```

## Integrações

### Claude Desktop

Adicione ao arquivo `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) ou `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "mcp-brasil": {
      "command": "/CAMINHO/PARA/uv",
      "args": ["run", "--directory", "/CAMINHO/PARA/mcp-brasil", "python", "-m", "mcp_brasil.server"],
      "env": {
        "TRANSPARENCIA_API_KEY": "sua-chave-aqui"
      }
    }
  }
}
```

> **Dica:** Descubra o caminho do `uv` com `which uv` no terminal.

Reinicie o Claude Desktop para ativar.

### Cursor

Crie o arquivo `.cursor/mcp.json` na raiz do projeto:

```json
{
  "mcpServers": {
    "mcp-brasil": {
      "command": "uv",
      "args": ["run", "--directory", "/CAMINHO/PARA/mcp-brasil", "python", "-m", "mcp_brasil.server"],
      "env": {
        "TRANSPARENCIA_API_KEY": "sua-chave-aqui"
      }
    }
  }
}
```

Depois em **Settings > MCP**, ative o server `mcp-brasil`.

### Claude Code

```bash
claude mcp add mcp-brasil -s user -- \
  uv run --directory /CAMINHO/PARA/mcp-brasil python -m mcp_brasil.server
```

### Outros clientes MCP (HTTP)

Rode o server em modo HTTP e conecte via URL:

```bash
make serve
# Server disponível em http://localhost:8000/mcp
```

## Features disponíveis

| Feature | API | Tools | Auth | Status |
|---------|-----|-------|------|--------|
| `ibge` | servicodados.ibge.gov.br | 9 | Nenhuma | Ativo |
| `bacen` | api.bcb.gov.br | 8 | Nenhuma | Ativo |
| `transparencia` | portaldatransparencia.gov.br | — | API key gratuita | Em desenvolvimento |
| `camara` | dadosabertos.camara.leg.br | — | Nenhuma | Planejado |
| `senado` | legis.senado.leg.br | — | Nenhuma | Planejado |
| `datajud` | api-publica.datajud.cnj.jus.br | — | API key CNJ | Planejado |
| `brasilapi` | brasilapi.com.br | — | Nenhuma | Planejado |
| `diario_oficial` | queridodiario.ok.org.br | — | Nenhuma | Planejado |

### IBGE (9 tools)

- `listar_estados` — Lista os 27 estados brasileiros
- `buscar_municipios` — Municípios de um estado por UF
- `listar_regioes` — 5 macro-regiões do Brasil
- `consultar_nome` — Frequência de um nome por década
- `ranking_nomes` — Nomes mais populares do Brasil
- `consultar_agregado` — Dados agregados (população, PIB, etc.)
- `listar_pesquisas` — Pesquisas e agregados disponíveis
- `obter_malha` — Metadados geográficos (centroide, área, bbox)
- `buscar_cnae` — Classificação de atividades econômicas

### Banco Central (8 tools)

- `consultar_serie` — Valores de uma série temporal do BCB
- `ultimos_valores` — Últimos N valores de uma série
- `metadados_serie` — Metadados de uma série (nome, unidade, periodicidade)
- `series_populares` — Catálogo de séries mais usadas por categoria
- `buscar_serie` — Busca textual no catálogo de séries
- `indicadores_atuais` — Selic, IPCA, dólar e outros indicadores em tempo real
- `calcular_variacao` — Estatísticas de variação de uma série
- `comparar_series` — Compara múltiplas séries lado a lado

## Arquitetura

O projeto usa **Package by Feature** com **Auto-Registry**:

- Features são organizadas em `data/` (APIs) e `agentes/` (agentes inteligentes)
- O server raiz descobre e monta features automaticamente via `FeatureRegistry`
- Para adicionar uma nova feature, basta criar o diretório seguindo a convenção

```
src/mcp_brasil/
├── server.py              # Auto-registry (nunca muda)
├── _shared/               # Utilitários compartilhados
│   └── feature.py         # FeatureMeta + FeatureRegistry
├── data/                  # Features de consulta a APIs
│   ├── ibge/              # Feature: IBGE
│   │   ├── __init__.py    # FEATURE_META
│   │   ├── server.py      # mcp: FastMCP
│   │   ├── tools.py       # Lógica das tools
│   │   ├── client.py      # HTTP async
│   │   ├── schemas.py     # Pydantic models
│   │   └── constants.py   # URLs, códigos
│   ├── bacen/             # Feature: Banco Central
│   └── ...
├── agentes/               # Features de agentes inteligentes
│   └── redator/           # Feature: Redator Oficial
└── ...
```

### Fluxo dentro de cada feature

```
server.py  →  tools.py  →  client.py  →  schemas.py
  registra     orquestra    faz HTTP      dados puros
```

Regras:
- `tools.py` nunca faz HTTP direto — delega para `client.py`
- `client.py` nunca formata para LLM — retorna Pydantic models
- `schemas.py` apenas Pydantic models, zero lógica
- `server.py` apenas registra tools/resources/prompts

## Desenvolvimento

```bash
make dev            # Instalar dependências (prod + dev)
make test           # Rodar todos os testes
make test-feature F=ibge  # Testes de uma feature
make lint           # Lint + format check
make fix            # Auto-fix lint + format
make types          # mypy strict
make ci             # lint + types + test
make run            # Server stdio
make serve          # Server HTTP :8000
make inspect        # Listar tools/resources/prompts
make clean          # Limpar caches
```

## Como contribuir

1. Crie um diretório em `src/mcp_brasil/data/{feature}/` (APIs) ou `src/mcp_brasil/agentes/{feature}/` (agentes)
2. Exporte `FEATURE_META` no `__init__.py`
3. Exporte `mcp: FastMCP` no `server.py`
4. Adicione testes em `tests/data/{feature}/` ou `tests/agentes/{feature}/`
5. Rode `make ci` e abra um PR

Consulte `AGENTS.md` e `docs/adrs/` para padrões e decisões de arquitetura.

## Licença

MIT
