---
name: new-package
description: Scaffold a new mcp-brasil feature package with all required files. Use when the user wants to create a new API module/feature/package, add a new data source, or says "new package", "nova feature", "new module", "criar pacote". Also use when adding any new Brazilian public API integration.
argument-hint: <feature-name> [--api-base <url>] [--auth <ENV_VAR>]
allowed-tools: Bash, Read, Write, Glob, Grep
---

# New Package — mcp-brasil Feature Scaffold

Creates a complete feature package following the project conventions (ADR-001, ADR-002).

## What it creates

```
src/mcp_brasil/data/{feature}/       # For data/API features
src/mcp_brasil/agentes/{feature}/    # For agent features
├── __init__.py     # FEATURE_META (auto-discovery marker)
├── constants.py    # API URLs, enums, codes
├── schemas.py      # Pydantic v2 models
├── client.py       # Async HTTP functions (httpx)
├── tools.py        # Tool functions with Context (LLM-formatted output)
├── resources.py    # Static reference data as MCP resources
├── prompts.py      # Analysis templates for LLMs
└── server.py       # FastMCP registration (tools + resources + prompts)
```

## How to use

Parse the argument for: feature name, optional `--api-base`, optional `--auth`.

Example invocations:
- `/new-package camara --api-base https://dadosabertos.camara.leg.br/api/v2`
- `/new-package datajud --api-base https://datajud-wiki.cnj.jus.br/api --auth DATAJUD_API_KEY`

## Steps

1. **Parse arguments**: Extract `feature_name`, `api_base` (default `""`), `auth_env_var` (default `None`)
2. **Validate**: Check the name is snake_case and the directory doesn't already exist
3. **Create directory**: `src/mcp_brasil/data/{feature_name}/` (for data/API features) or `src/mcp_brasil/agentes/{feature_name}/` (for agent features)
4. **Write all 8 files** using the templates in [refs/templates.md](refs/templates.md)
5. **Run lint**: `uv run ruff format src/mcp_brasil/data/{feature_name}/ && uv run ruff check src/mcp_brasil/data/{feature_name}/` (adjust path for agentes)
6. **Verify auto-discovery**: `uv run python -c "from mcp_brasil._shared.feature import FeatureRegistry; r = FeatureRegistry(); r.discover('mcp_brasil.data'); r.discover('mcp_brasil.agentes'); print(r.summary())"`
7. **Report**: Show the user which files were created and next steps

## Architecture rules (inviolable)

These come from ADR-001 and must be followed in all generated code:

| Rule | What it means |
|------|--------------|
| `server.py` only registers | Zero business logic, just `mcp.tool(fn)`, `mcp.resource(...)`, `mcp.prompt(fn)` calls |
| `tools.py` never makes HTTP | Delegates to `client.py`, returns formatted strings. Uses `ctx: Context` for logging |
| `resources.py` returns static data | JSON strings with reference data — no HTTP calls |
| `prompts.py` returns instruction strings | Guides LLM to use tools — no business logic |
| `client.py` never formats for LLM | Returns Pydantic models or raw dicts |
| `schemas.py` zero logic | Only `BaseModel` / `dataclass` definitions |
| `constants.py` zero imports | No imports from other project modules |
| All functions `async def` | Tools and client functions are async |
| Complete type hints | Every function fully typed |
| Docstrings on every tool | Used by LLM to decide when to call the tool |

## Dependency flow within the package

```
server.py → tools.py + resources.py + prompts.py → client.py → schemas.py
  registers    orchestrates / static data / templates    HTTP calls    data models
```

## Resource URI namespacing (CRITICAL)

Resource URIs in the feature server MUST NOT include the feature name. The root server's `mount(server, namespace="feature")` adds the prefix automatically.

```python
# ✅ CORRECT — in feature server.py
mcp.resource("data://catalogo", mime_type="application/json")(catalogo_fn)
# Result in root: data://feature/catalogo

# ❌ WRONG — double namespace
mcp.resource("data://feature/catalogo", mime_type="application/json")(catalogo_fn)
# Result in root: data://feature/feature/catalogo
```

## After scaffolding

Tell the user:
1. The feature is auto-discovered (no changes to root `server.py` needed)
2. They should fill in `constants.py` with real API URLs
3. They should define Pydantic models in `schemas.py`
4. They should implement HTTP functions in `client.py`
5. They should implement tool functions in `tools.py` (with `ctx: Context` for logging)
6. They should add static reference data in `resources.py`
7. They should add analysis prompts in `prompts.py`
8. They should register all components in `server.py` (tools + resources + prompts)

## Template reference

Read [refs/templates.md](refs/templates.md) for the exact file templates to use.
