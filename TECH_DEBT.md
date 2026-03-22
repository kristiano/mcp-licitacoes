# TECH_DEBT.md — Interactive TODO for Technical Debt

> Track bugs, incompatibilities, mocks, and incomplete implementations.
> Update this file whenever you find something that needs attention later.

## Legend

- `[ ]` — Open (needs work)
- `[~]` — In progress
- `[x]` — Resolved

---

## Bootstrap Phase

- [x] **mount() API mismatch** — `feature.py` used `mount("/path", server)` instead of FastMCP v3's `mount(server, namespace=name)`. Fixed.
- [x] **list_tools() accessed private API** — `_tool_manager._tools` is private FastMCP internals. Removed method to avoid mypy strict failures.
- [x] **_shared/http_client.py** — `create_client()` + `http_get()` with retry + exponential backoff + 429/5xx.
- [x] **_shared/formatting.py** — `markdown_table`, `format_brl`, `format_number_br`, `format_percent`, `truncate_list`.
- [x] **_shared/cache.py** — `TTLCache` class + `@ttl_cache(ttl=300)` decorator for async functions.
- [x] **settings.py** — Env var overrides: `HTTP_TIMEOUT`, `HTTP_MAX_RETRIES`, `HTTP_BACKOFF_BASE`, `USER_AGENT`.
- [x] **pyproject.toml dependency-groups** — Migrated from `[project.optional-dependencies]` to `[dependency-groups]`. `make dev` uses `uv sync --group dev`.
- [x] **justfile removed** — Replaced by Makefile.

## Core — Open

- [ ] **Response size limiting for LLM context** — APIs can return huge payloads (e.g., 5000+ municipios). Need a strategy to truncate/summarize responses to avoid blowing LLM context windows. See `_shared/formatting.py:truncate_list` as starting point.

## Transparência Feature

- [ ] **API response shapes unverified** — Parsing helpers (`_parse_*` in `client.py`) are based on API docs and reference code. Real API responses may have different field names or nesting. All schema fields are `| None` to handle this gracefully, but field mappings need validation with real API calls.
- [ ] **Rate limiting not enforced client-side** — Portal da Transparência has 90 req/min (06h-23h59) and 300 req/min (00h-05h59) limits. Currently relying on `http_get()` retry for 429, but no proactive throttling.
- [ ] **Pagination not automatic** — All tools accept `pagina` but don't auto-paginate. Users must manually request subsequent pages.
- [ ] **Pre-existing mypy errors in lifespan.py and ibge/client.py** — 7 type errors unrelated to transparencia. Transparencia passes mypy clean.

## Known Limitations

- [ ] **No CONTRIBUTING.md** — Mentioned in roadmap Semana 0 but not yet created.

---

*Last updated: 2026-03-22*
