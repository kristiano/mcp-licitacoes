---
name: fastmcp
description: >
  Expert guide for building MCP servers with FastMCP v3 (Prefect). Use this skill whenever the user
  wants to create, modify, or debug an MCP server using FastMCP — including defining tools, resources,
  prompts, testing servers, composing multiple servers, adding authentication, deploying over HTTP,
  or integrating with Claude, OpenAI, or other LLM clients. Also use it when the user mentions
  "FastMCP", "MCP server", "Model Context Protocol", "@mcp.tool", "@mcp.resource", "@mcp.prompt",
  or wants to expose Python functions as AI-callable tools. Trigger even if the user just says
  "add a tool" or "create an MCP endpoint" in a Python project that uses or could use FastMCP.
---

# FastMCP v3 — Building MCP Servers

FastMCP v3 (by Prefect) is the standard Python framework for building Model Context Protocol servers.
It exposes Python functions as **tools**, **resources**, and **prompts** that LLMs can discover and invoke.

## Quick Reference

```python
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
async def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

@mcp.resource("data://config")
def get_config() -> str:
    return '{"theme": "dark"}'

@mcp.prompt
def review_code(code: str) -> str:
    """Ask for a code review."""
    return f"Please review:\n```\n{code}\n```"

if __name__ == "__main__":
    mcp.run()  # stdio (default) or mcp.run(transport="http", port=8000)
```

## Core Concepts

### Tools (`@mcp.tool`)

Tools are functions LLMs can invoke. FastMCP auto-generates schemas from type hints and docstrings.

```python
from typing import Annotated
from pydantic import Field

@mcp.tool
async def search_products(
    query: str,
    max_results: Annotated[int, "Maximum results to return"] = 10,
    category: str | None = None,
) -> list[dict]:
    """Search the product catalog with optional category filtering."""
    ...
```

Key patterns:
- **Docstrings** become the tool description LLMs see — always write clear ones
- **Type hints** generate the input schema automatically (Pydantic types, Literal, Enum all work)
- **Annotated[type, "description"]** adds per-parameter descriptions
- **`async def`** is preferred for I/O; sync functions run in a threadpool automatically
- **Pydantic models** as parameters or return types work natively
- **`ToolResult`** for full control over content + structured output
- **`annotations={"readOnlyHint": True}`** tells clients the tool is safe (skips confirmation)
- **`timeout=30.0`** limits execution time in seconds
- **Error handling**: raise `ToolError` for client-visible errors, or any exception (logged + converted)

### Resources (`@mcp.resource`)

Read-only data sources clients can pull. Each resource has a unique URI.

```python
@mcp.resource("data://app-status", mime_type="application/json")
async def get_status() -> str:
    return json.dumps({"status": "ok", "uptime": 12345})

# Resource templates — parameterized URIs
@mcp.resource("users://{user_id}/profile")
async def get_profile(user_id: str) -> str:
    return json.dumps(await fetch_user(user_id))
```

Key patterns:
- Return `str` (text), `bytes` (binary), or `ResourceResult` for full control
- Templates use `{param}` in URI; `{param*}` for wildcard (multi-segment) paths
- Query params: `"data://{id}{?format,limit}"` — must be optional function params

### Prompts (`@mcp.prompt`)

Reusable message templates that guide LLM interactions.

```python
from fastmcp.prompts import Message

@mcp.prompt
def analyze_data(dataset: str, focus: str = "summary") -> list[Message]:
    """Create an analysis request."""
    return [
        Message(f"Analyze {dataset} with focus on {focus}"),
        Message("I'll analyze that for you.", role="assistant"),
    ]
```

Key patterns:
- Return `str` (auto-wrapped as user message), `list[Message]`, or `PromptResult`
- Parameters with defaults are optional; without defaults are required

### Context (`Context`)

Access MCP capabilities (logging, progress, resources, sampling) inside tools/resources/prompts.

```python
from fastmcp import FastMCP, Context

@mcp.tool
async def process(data: str, ctx: Context) -> str:
    await ctx.info(f"Processing: {data}")
    await ctx.report_progress(progress=50, total=100)
    resource = await ctx.read_resource("data://config")
    summary = await ctx.sample(f"Summarize: {data[:200]}")
    return summary.text
```

Context is injected automatically by type hint. Available methods:
- **Logging**: `ctx.debug()`, `ctx.info()`, `ctx.warning()`, `ctx.error()`
- **Progress**: `ctx.report_progress(progress, total)`
- **Resources**: `ctx.read_resource(uri)`, `ctx.list_resources()`
- **Sampling**: `ctx.sample(prompt)` — ask the client's LLM
- **Elicitation**: `ctx.elicit("question", response_type=str)` — ask the user
- **Session state**: `ctx.get_state(key)`, `ctx.set_state(key, value)`
- **Session ID**: `ctx.session_id`, `ctx.request_id`, `ctx.client_id`

### Dependency Injection

Hide parameters from LLM schema and inject runtime values.

```python
from fastmcp.dependencies import Depends, CurrentContext

def get_db():
    return Database(os.environ["DB_URL"])

@mcp.tool
async def query(sql: str, db=Depends(get_db)) -> list:
    """Run a database query. (db is injected, not visible to LLM)"""
    return await db.execute(sql)
```

Built-in dependencies: `CurrentContext()`, `CurrentFastMCP()`, `CurrentRequest()`,
`CurrentHeaders()`, `CurrentAccessToken()`, `TokenClaim("sub")`.

### Server Composition (`mount`)

Combine multiple servers into one. Components are live-linked.

```python
weather = FastMCP("Weather")
calendar = FastMCP("Calendar")

main = FastMCP("Main")
main.mount(weather, namespace="weather")   # weather_get_forecast
main.mount(calendar, namespace="calendar") # calendar_get_events
```

Mount remote servers: `main.mount(create_proxy("http://api.example.com/mcp"), namespace="api")`

### Lifespans

Server-level setup/teardown that runs once (not per-session).

```python
from fastmcp.server.lifespan import lifespan

@lifespan
async def app_lifespan(server):
    db = await connect_db()
    try:
        yield {"db": db}
    finally:
        await db.close()

mcp = FastMCP("MyServer", lifespan=app_lifespan)

@mcp.tool
def query(ctx: Context) -> list:
    db = ctx.lifespan_context["db"]
    return db.fetch_all()
```

Compose with `|`: `mcp = FastMCP("App", lifespan=config_lifespan | db_lifespan)`

### Testing

In-memory transport — no network, no deployment, fast and deterministic.

```python
from fastmcp import FastMCP, Client

async def test_my_tool():
    server = FastMCP("Test")

    @server.tool
    def add(a: int, b: int) -> int:
        return a + b

    async with Client(server) as client:
        result = await client.call_tool("add", {"a": 2, "b": 3})
        assert result.data == 5
```

For HTTP transport testing: use `run_server_async` from `fastmcp.utilities.tests`.

### Running & Deployment

```python
# STDIO (local, default)
mcp.run()

# HTTP (remote)
mcp.run(transport="http", host="0.0.0.0", port=8000)

# ASGI app (production — use with uvicorn)
app = mcp.http_app()
```

CLI: `fastmcp run server.py:mcp --transport http --port 8000`

### Middleware

Cross-cutting concerns (auth, logging, rate limiting) without modifying tools.

```python
from fastmcp.server.middleware import Middleware, MiddlewareContext

class LoggingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        print(f"Calling tool: {context.message.name}")
        result = await call_next(context)
        return result

mcp.add_middleware(LoggingMiddleware())
```

Hooks hierarchy: `on_message` → `on_request` → `on_call_tool` / `on_read_resource` / `on_get_prompt`

## FastMCP Constructor — Common Parameters

```python
mcp = FastMCP(
    name="MyServer",
    instructions="Description for clients",
    version="1.0.0",
    auth=my_auth_provider,           # OAuthProvider or TokenVerifier
    lifespan=my_lifespan,            # Setup/teardown
    on_duplicate="warn",             # "warn" | "error" | "replace" | "ignore"
    strict_input_validation=False,   # True for strict JSON Schema validation
    list_page_size=None,             # Pagination for list operations
)
```

## Reference Files

For detailed documentation on specific topics, read the appropriate reference file:

| Topic | File | When to read |
|-------|------|-------------|
| Tools (full API) | `references/tools.md` | Detailed tool patterns: output schemas, structured content, ToolResult, media helpers, validation, annotations, timeouts |
| Resources & Prompts | `references/resources-prompts.md` | Resource templates, wildcards, query params, ResourceResult, PromptResult, Message class |
| Context & DI & Middleware | `references/context-di-middleware.md` | Dependency injection, custom dependencies, middleware hooks, session state, elicitation, sampling |
| Composition & Providers | `references/composition-providers.md` | mount(), namespacing, ProxyProvider, FileSystemProvider, SkillsProvider, transforms, code-mode |
| Testing | `references/testing.md` | In-memory testing, HTTP transport testing, fixtures, mocking, inline snapshots |
| Deployment & CLI | `references/deployment.md` | HTTP deployment, ASGI apps, FastAPI integration, CLI commands, server configuration, authentication overview |

The full FastMCP v3 documentation (331 files, 2.8MB) is bundled at `docs/` within this skill directory.

When detailed information is needed beyond what's in the reference files, read the original docs directly:
- Tools: `docs/servers/tools.md`
- Resources: `docs/servers/resources.md`
- Prompts: `docs/servers/prompts.md`
- Context: `docs/servers/context.md`
- DI: `docs/servers/dependency-injection.md`
- Middleware: `docs/servers/middleware.md`
- Composition: `docs/servers/composition.md`
- Auth: `docs/servers/auth/authentication.md`
- Testing: `docs/development/tests.md`
- HTTP: `docs/deployment/http.md`
- CLI: `docs/cli/overview.md`
- Integrations: `docs/integrations/` directory
- Python SDK reference: `docs/python-sdk/` directory
- Changelog: `docs/changelog.md`
- Upgrade guides: `docs/getting-started/upgrading/`
