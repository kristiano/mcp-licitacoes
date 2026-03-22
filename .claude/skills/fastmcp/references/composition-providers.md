# FastMCP Composition & Providers — Detailed Reference

## Server Composition with mount()

### Basic Mounting

```python
from fastmcp import FastMCP

weather = FastMCP("Weather")

@weather.tool
def get_forecast(city: str) -> str:
    return f"Sunny in {city}"

@weather.resource("data://cities")
def list_cities() -> list[str]:
    return ["London", "Paris", "Tokyo"]

main = FastMCP("MainApp")
main.mount(weather)  # All weather components available through main
```

### Namespacing

Avoid naming conflicts when mounting multiple servers:

```python
main.mount(weather, namespace="weather")
main.mount(calendar, namespace="calendar")
# Tools: weather_get_forecast, calendar_get_events
# Resources: data://weather/cities, data://calendar/events
```

| Component | Without Namespace | With `namespace="api"` |
|-----------|-------------------|----------------------|
| Tool | `my_tool` | `api_my_tool` |
| Prompt | `my_prompt` | `api_my_prompt` |
| Resource | `data://info` | `data://api/info` |
| Template | `data://{id}` | `data://api/{id}` |

### Mounting External Servers

```python
from fastmcp.server import create_proxy

# Remote HTTP server
mcp.mount(create_proxy("http://api.example.com/mcp"), namespace="api")

# Local Python script
mcp.mount(create_proxy("./my_server.py"), namespace="local")

# npm package
github_config = {
    "mcpServers": {
        "default": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"]
        }
    }
}
mcp.mount(create_proxy(github_config), namespace="github")

# Python uvx tool
sqlite_config = {
    "mcpServers": {
        "default": {
            "command": "uvx",
            "args": ["mcp-server-sqlite", "--db", "data.db"]
        }
    }
}
mcp.mount(create_proxy(sqlite_config), namespace="db")

# Explicit transport classes
from fastmcp.client.transports import NpxStdioTransport, UvxStdioTransport

mcp.mount(
    create_proxy(NpxStdioTransport(package="@modelcontextprotocol/server-github")),
    namespace="github",
)
```

### Dynamic Composition

mount() creates a live link — add components after mounting:
```python
main.mount(dynamic_server, namespace="dyn")

@dynamic_server.tool  # Added AFTER mounting — works!
def added_later() -> str:
    return "Available through main!"
```

### Tag Filtering with Composition

```python
prod_app = FastMCP("Production")
prod_app.mount(api_server, namespace="api")
prod_app.enable(tags={"production"}, only=True)
# Only production-tagged tools visible
```

### Custom Routes Forwarding

```python
@subserver.custom_route("/health", methods=["GET"])
async def health():
    return {"status": "ok"}

main.mount(subserver)  # /health accessible through main
```

### Conflict Resolution

Most recently mounted wins:
```python
main.mount(server_a)
main.mount(server_b)  # server_b's shared_tool wins
```

### Performance Notes

- HTTP-mounted servers: 300-400ms vs 1-2ms for local tools
- Consider caching for latency-critical paths
- Limit mounting depth

## Providers

Providers source components (tools, resources, prompts) from different backends.

### Provider Architecture

```python
from fastmcp.server.providers import LocalProvider

# Every server has a built-in LocalProvider for @mcp.tool, @mcp.resource, etc.
mcp.local_provider.remove_tool("my_tool")
```

### ProxyProvider — Remote Servers

```python
from fastmcp.server import create_proxy

# Wraps a remote MCP server as a local provider
proxy = create_proxy("http://remote-server.com/mcp")
mcp.mount(proxy, namespace="remote")
```

### FileSystemProvider — Expose Files

```python
from fastmcp.server.providers import FileSystemProvider

provider = FileSystemProvider(
    root_path="./data",
    uri_prefix="files://",
    recursive=True,
    glob_pattern="*.json",
)
mcp.mount(provider, namespace="files")
```

### SkillsProvider — Claude Skills

```python
from fastmcp.server.providers import SkillsProvider

provider = SkillsProvider(skills_dir="./skills")
mcp.mount(provider)
```

## Transforms

Transforms modify how components are presented to clients.

### Namespace Transform

Applied automatically by `mount(server, namespace="ns")`.

### Tool Search Transform

Replace large tool catalogs with on-demand discovery:
```python
from fastmcp.transforms import ToolSearchTransform

mcp = FastMCP("Large Server", transforms=[ToolSearchTransform()])
# Instead of listing 100+ tools, clients search for relevant ones
```

### Code Mode Transform

Let LLMs write scripts that chain tool calls:
```python
from fastmcp.transforms import CodeModeTransform

mcp = FastMCP("Scripting", transforms=[CodeModeTransform()])
# LLMs can write Python scripts that call multiple tools
```

### Resources as Tools

```python
from fastmcp.transforms import ResourcesAsToolsTransform

mcp = FastMCP("Server", transforms=[ResourcesAsToolsTransform()])
# Resources become callable as tools
```

### Prompts as Tools

```python
from fastmcp.transforms import PromptsAsToolsTransform

mcp = FastMCP("Server", transforms=[PromptsAsToolsTransform()])
# Prompts become callable as tools
```

## Lifespans

Server-level setup/teardown — runs once, not per session.

```python
from fastmcp.server.lifespan import lifespan

@lifespan
async def db_lifespan(server):
    db = await connect_db()
    try:
        yield {"db": db}
    finally:
        await db.close()

mcp = FastMCP("App", lifespan=db_lifespan)

@mcp.tool
def query(ctx: Context) -> list:
    db = ctx.lifespan_context["db"]
    return db.fetch_all()
```

### Composing Lifespans

```python
@lifespan
async def config_lifespan(server):
    yield {"config": load_config()}

@lifespan
async def cache_lifespan(server):
    cache = Cache()
    try:
        yield {"cache": cache}
    finally:
        await cache.close()

mcp = FastMCP("App", lifespan=config_lifespan | cache_lifespan)
# Enters left→right, exits right→left, merges context dicts
```

### Legacy asynccontextmanager

```python
from contextlib import asynccontextmanager
from fastmcp.server.lifespan import ContextManagerLifespan

@asynccontextmanager
async def legacy(server):
    yield {"key": "value"}

# Direct use
mcp = FastMCP("App", lifespan=legacy)

# Composition with @lifespan
combined = ContextManagerLifespan(legacy) | new_lifespan
```

### With FastAPI

```python
from fastmcp.utilities.lifespan import combine_lifespans

app = FastAPI(lifespan=combine_lifespans(app_lifespan, mcp_app.lifespan))
app.mount("/mcp", mcp.http_app())
```
