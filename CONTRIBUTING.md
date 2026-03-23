# Contributing to mcp-brasil

Obrigado pelo interesse em contribuir!

## Getting Started

```bash
git clone https://github.com/seu-usuario/mcp-brasil.git
cd mcp-brasil
make dev        # Instala dependências de dev
make ci         # Roda lint + mypy + testes
```

## Estrutura do Projeto

```
src/mcp_brasil/
├── server.py           # Server raiz (auto-registry, nunca editado manualmente)
├── _shared/            # Código compartilhado (http_client, formatting, cache, rate_limiter)
├── data/               # Features de consulta a APIs
│   ├── ibge/           # Feature IBGE
│   ├── transparencia/  # Feature Portal da Transparência
│   └── {nova_feature}/ # Sua nova feature de dados aqui
└── agentes/            # Features de agentes inteligentes
    └── redator/        # Feature Redator Oficial
```

Leia os ADRs em `plan/adrs/` antes de implementar:
- **ADR-001** — Stack, package-by-feature, convenções
- **ADR-002** — Auto-registry pattern (FeatureRegistry)
- **ADR-003** — Padrão de agentes (Prompt + Resource + Tool)

## Como Adicionar uma Nova Feature

1. Crie o diretório `src/mcp_brasil/data/{feature}/` (APIs) ou `src/mcp_brasil/agentes/{feature}/` (agentes) com os arquivos obrigatórios:

```
src/mcp_brasil/data/{feature}/      # ou agentes/{feature}/
├── __init__.py     # FEATURE_META (obrigatório para auto-discovery)
├── server.py       # mcp: FastMCP (obrigatório)
├── tools.py        # Funções das tools
├── client.py       # HTTP async para a API
├── schemas.py      # Pydantic models
└── constants.py    # URLs, enums, códigos
```

2. Em `__init__.py`, defina `FEATURE_META`:

```python
FEATURE_META = {
    "name": "minha-feature",
    "description": "Descrição curta da API",
}
```

3. Em `server.py`, crie e registre as tools:

```python
from fastmcp import FastMCP
from . import tools

mcp = FastMCP("minha-feature")

@mcp.tool()
async def minha_tool(param: str) -> str:
    """Docstring usada pelo LLM para decidir quando chamar."""
    return await tools.minha_tool(param)
```

4. Crie testes em `tests/data/{feature}/` (ou `tests/agentes/{feature}/`):

```
tests/data/{feature}/         # ou tests/agentes/{feature}/
├── test_tools.py             # Mock client, testa lógica
├── test_client.py            # respx mock HTTP
└── test_integration.py       # fastmcp.Client e2e
```

5. Rode `make ci` para verificar que tudo passa.

## Convenções de Código

| Escopo | Convenção | Exemplo |
|--------|-----------|---------|
| Módulos | snake_case | `client.py` |
| Classes | PascalCase | `class Estado(BaseModel)` |
| Funções/tools | snake_case, verbo | `buscar_localidades()` |
| Constantes | UPPER_SNAKE | `IBGE_API_BASE` |
| Privados | `_prefixo` | `_shared/`, `_cache` |

### Regras Invioláveis

- `tools.py` nunca faz HTTP — delega para `client.py`
- `client.py` nunca formata para LLM — retorna Pydantic models
- `schemas.py` zero lógica — apenas BaseModel
- `server.py` da feature apenas registra — zero lógica de negócio
- Async everywhere — `async def` em tools e clients
- Type hints completos em todas as funções

## Testes

```bash
make test               # Todos os testes
make test-feature F=ibge  # Testes de uma feature
make lint               # ruff check + format check
make types              # mypy strict
make ci                 # lint + types + test
```

Testes usam:
- **pytest** + **pytest-asyncio** para async
- **respx** para mock HTTP em `test_client.py`
- **unittest.mock** para mock de client em `test_tools.py`
- **fastmcp.Client** para testes de integração e2e

## Pull Requests

- Use **Conventional Commits** (em português ou inglês):

```
feat(ibge): add tool consultar_populacao
fix(bacen): handle empty response from SGS
test(transparencia): add edge-case tests for client
docs: update README with new feature
```

- Garanta que `make ci` passa antes de abrir o PR
- Descreva o que mudou e por quê no corpo do PR
