# FastMCP Context, Dependency Injection & Middleware — Detailed Reference

## Context

### Accessing Context

Three ways (all equivalent):

```python
# 1. Type hint injection (most common)
from fastmcp import FastMCP, Context

@mcp.tool
async def my_tool(query: str, ctx: Context) -> str:
    await ctx.info(f"Processing: {query}")
    return "done"

# 2. Explicit CurrentContext() dependency
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

@mcp.tool
async def my_tool(query: str, ctx: Context = CurrentContext()) -> str:
    ...

# 3. get_context() in nested functions
from fastmcp.server.dependencies import get_context

async def helper():
    ctx = get_context()  # Only works during a request
    await ctx.info("from helper")
```

### Context Methods

**Logging:**
```python
await ctx.debug("Starting")
await ctx.info(f"Processing {len(data)} items")
await ctx.warning("Deprecated param")
await ctx.error("Failed")
```

**Progress:**
```python
await ctx.report_progress(progress=50, total=100)
```

**Resource Access:**
```python
resources = await ctx.list_resources()
content_list = await ctx.read_resource("data://config")
content = content_list[0].content
```

**Prompt Access:**
```python
prompts = await ctx.list_prompts()
result = await ctx.get_prompt("analyze", {"dataset": "users"})
```

**LLM Sampling:**
```python
response = await ctx.sample("Analyze this data", temperature=0.7)
text = response.text
```

**User Elicitation:**
```python
result = await ctx.elicit("Enter your name:", response_type=str)
if result.action == "accept":
    name = result.data
```

**Session State:**
```python
await ctx.set_state("counter", 42)
count = await ctx.get_state("counter")  # returns None if not found
await ctx.delete_state("counter")

# Non-serializable (current request only)
await ctx.set_state("client", http_client, serializable=False)
```

**Properties:**
```python
ctx.request_id          # Unique request ID
ctx.client_id           # Client ID (if provided)
ctx.session_id          # MCP session ID
ctx.transport           # "stdio" | "sse" | "streamable-http" | None
ctx.fastmcp             # FastMCP server instance
ctx.lifespan_context    # Dict from lifespan yield
ctx.request_context     # Low-level MCP request (None if not established)
```

**Session Visibility:**
```python
ctx.enable_components(tags={"advanced"})
ctx.disable_components(keys={"tool:admin_action"})
ctx.reset_visibility()
```

## Dependency Injection

Parameters with DI defaults are **excluded from the MCP schema** — clients never see them.

### Built-in Dependencies

| Dependency | Provides | Import |
|-----------|---------|--------|
| `Context` type hint | MCP Context | `from fastmcp import Context` |
| `CurrentContext()` | MCP Context (explicit) | `from fastmcp.dependencies import CurrentContext` |
| `CurrentFastMCP()` | Server instance | `from fastmcp.dependencies import CurrentFastMCP` |
| `CurrentRequest()` | Starlette Request (HTTP only) | `from fastmcp.dependencies import CurrentRequest` |
| `CurrentHeaders()` | HTTP headers dict (safe fallback) | `from fastmcp.dependencies import CurrentHeaders` |
| `CurrentAccessToken()` | AccessToken (raises if unauth) | `from fastmcp.dependencies import CurrentAccessToken` |
| `TokenClaim("sub")` | Specific token claim value | `from fastmcp.server.dependencies import TokenClaim` |

### Function helpers (for nested code)

```python
from fastmcp.server.dependencies import (
    get_context,
    get_server,
    get_http_request,
    get_http_headers,
    get_access_token,
)
```

### Custom Dependencies with Depends()

```python
from fastmcp.dependencies import Depends

def get_config() -> dict:
    return {"api_url": "https://api.example.com"}

async def get_user_id() -> int:
    return 42

@mcp.tool
async def fetch(
    query: str,
    config: dict = Depends(get_config),
    user_id: int = Depends(get_user_id),
) -> str:
    return f"User {user_id} fetching from {config['api_url']}"
```

**Caching**: Dependencies resolved once per request, reused across params.

**Resource Management** (cleanup):
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db():
    db = await connect()
    try:
        yield db
    finally:
        await db.close()

@mcp.tool
async def query(sql: str, db=Depends(get_db)) -> list:
    return await db.execute(sql)
```

**Nested Dependencies**:
```python
def get_base_url() -> str:
    return "https://api.example.com"

def get_client(url: str = Depends(get_base_url)) -> dict:
    return {"base_url": url, "version": "v1"}

@mcp.tool
async def call_api(endpoint: str, client: dict = Depends(get_client)) -> str:
    ...
```

### AccessToken

```python
token.client_id    # OAuth client ID
token.scopes       # List of granted scopes
token.expires_at   # Expiration timestamp
token.claims       # All token claims dict
```

## Middleware

### Creating Middleware

```python
from fastmcp.server.middleware import Middleware, MiddlewareContext

class TimingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        start = time.time()
        result = await call_next(context)
        elapsed = time.time() - start
        print(f"Tool {context.message.name} took {elapsed:.2f}s")
        return result

mcp.add_middleware(TimingMiddleware())
```

### Hook Hierarchy

```
Request → on_message → on_request → on_call_tool → Handler → Response
                                  → on_read_resource
                                  → on_get_prompt
                                  → on_list_tools
                                  → on_list_resources
                                  → on_list_prompts
         on_message → on_notification (fire-and-forget)
```

### Available Hooks

| Hook | When | Returns |
|------|------|---------|
| `on_message` | Every MCP message | Any |
| `on_request` | Requests expecting response | Any |
| `on_notification` | Fire-and-forget | None |
| `on_call_tool` | Tool execution | Tool result |
| `on_read_resource` | Resource read | Resource contents |
| `on_get_prompt` | Prompt render | Prompt messages |
| `on_list_tools` | Listing tools | Tool list |
| `on_list_resources` | Listing resources | Resource list |
| `on_list_prompts` | Listing prompts | Prompt list |
| `on_initialize` | Client connection | Init result |

### MiddlewareContext Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `method` | `str` | MCP method (e.g., `"tools/call"`) |
| `source` | `str` | `"client"` or `"server"` |
| `type` | `str` | `"request"` or `"notification"` |
| `message` | `object` | MCP message data |
| `timestamp` | `datetime` | When received |
| `fastmcp_context` | `Context` | FastMCP context (if available) |

### Execution Order

First added = first in, last out:
```python
mcp.add_middleware(ErrorHandlingMiddleware())   # 1st in, last out
mcp.add_middleware(RateLimitingMiddleware())    # 2nd
mcp.add_middleware(LoggingMiddleware())         # 3rd in, first out
```

### With Composition

Parent middleware runs for ALL requests (including mounted servers).
Child middleware only runs for that child's handlers.

```python
parent.add_middleware(AuthMiddleware())      # Runs for all
child.add_middleware(LoggingMiddleware())    # Only for child
parent.mount(child, namespace="child")
```

### Blocking Requests

Don't call `call_next` to block:
```python
class AuthMiddleware(Middleware):
    async def on_request(self, context, call_next):
        if not is_authenticated(context):
            raise PermissionError("Unauthorized")
        return await call_next(context)
```

### Modifying Arguments

```python
class DefaultsMiddleware(Middleware):
    async def on_call_tool(self, context, call_next):
        if context.message.name == "search":
            args = context.message.arguments or {}
            args.setdefault("limit", 10)
            context.message.arguments = args
        return await call_next(context)
```
