# FastMCP Deployment & CLI — Detailed Reference

## Running Your Server

### STDIO (Local, Default)

```python
mcp = FastMCP("MyServer")

if __name__ == "__main__":
    mcp.run()  # STDIO transport
```

### HTTP (Remote)

```python
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
# Accessible at http://localhost:8000/mcp
```

### ASGI App (Production)

```python
app = mcp.http_app()
# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
```

Benefits: multiple workers, custom middleware, integration with existing apps.

### Custom Path

```python
mcp.run(transport="http", host="0.0.0.0", port=8000, path="/api/mcp/")
# Or
app = mcp.http_app(path="/api/mcp/")
```

## CLI Commands

### Running

```bash
# STDIO (default)
fastmcp run server.py:mcp

# HTTP
fastmcp run server.py:mcp --transport http --port 8000

# With host binding
fastmcp run server.py:mcp --transport http --host 0.0.0.0 --port 8000
```

The CLI imports the server object directly — does NOT execute `__main__` block.

### Inspecting

```bash
fastmcp inspect server.py:mcp
# Lists all tools, resources, and prompts
```

### Installing into Clients

```bash
# Install into Claude Desktop
fastmcp install server.py:mcp

# Install with custom name
fastmcp install server.py:mcp --name "My Server"
```

### Client CLI

```bash
# List tools
fastmcp client list-tools server.py:mcp

# Call a tool
fastmcp client call-tool server.py:mcp greet '{"name": "World"}'

# Read a resource
fastmcp client read-resource server.py:mcp "data://config"
```

### Generate CLI from Server

```bash
fastmcp generate-cli server.py:mcp > cli.py
# Creates a CLI wrapper for your server's tools
```

## Health Checks

```python
from starlette.responses import JSONResponse

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy"})
```

## CORS Middleware

```python
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = mcp.http_app(middleware=middleware)
```

## FastAPI Integration

### Mounting MCP in FastAPI

```python
from fastapi import FastAPI
from fastmcp import FastMCP

fastapi_app = FastAPI()
mcp = FastMCP("Tools")

# Mount MCP as sub-application
mcp_app = mcp.http_app()
fastapi_app.mount("/mcp", mcp_app)
```

### Combined Lifespans

```python
from contextlib import asynccontextmanager
from fastmcp.utilities.lifespan import combine_lifespans

@asynccontextmanager
async def app_lifespan(app):
    print("FastAPI starting...")
    yield
    print("FastAPI shutting down...")

mcp_app = mcp.http_app()
fastapi_app = FastAPI(
    lifespan=combine_lifespans(app_lifespan, mcp_app.lifespan)
)
fastapi_app.mount("/mcp", mcp_app)
```

## Authentication Overview

### Bearer Token Verification

```python
from fastmcp.server.auth import BearerTokenVerifier

verifier = BearerTokenVerifier(
    verify_token=my_verify_function,
)
mcp = FastMCP("Secure", auth=verifier)
```

### OAuth Proxy

```python
from fastmcp.server.auth import OAuthProxy

auth = OAuthProxy(
    authorization_url="https://auth.example.com/authorize",
    token_url="https://auth.example.com/token",
    client_id="my-client-id",
    client_secret="my-client-secret",
)
mcp = FastMCP("OAuth Server", auth=auth)
```

### OIDC Proxy

```python
from fastmcp.server.auth import OIDCProxy

auth = OIDCProxy(
    issuer_url="https://accounts.google.com",
    client_id="my-client-id",
    client_secret="my-client-secret",
)
mcp = FastMCP("OIDC Server", auth=auth)
```

### Multi-Auth

```python
from fastmcp.server.auth import MultiAuth

auth = MultiAuth(providers=[bearer_auth, oauth_auth])
mcp = FastMCP("Multi", auth=auth)
```

For detailed auth documentation, read the original files:
- `SERVERS/auth/authentication.md` — Core auth mechanisms
- `SERVERS/auth/oauth-proxy.md` — OAuth proxy
- `SERVERS/auth/token-verification.md` — Token verification
- `SERVERS/auth/remote-oauth.md` — Remote OAuth
- `SERVERS/auth/oidc-proxy.md` — OIDC proxy
- `SERVERS/auth/multi-auth.md` — Multiple auth methods

## Server Configuration

### Common Parameters

```python
mcp = FastMCP(
    name="MyServer",
    instructions="How to use this server",
    version="1.0.0",
    website_url="https://example.com",
    auth=my_auth,
    lifespan=my_lifespan,
    tools=[tool1, tool2],              # Programmatic tool registration
    transforms=[ToolSearchTransform()], # Server-level transforms
    on_duplicate="warn",               # "warn" | "error" | "replace" | "ignore"
    strict_input_validation=False,
    list_page_size=None,               # Pagination for list ops
    mask_error_details=False,          # Hide internal error messages
    dereference_schemas=True,          # Inline $ref in schemas
)
```

### Session State Storage

```python
# Default: in-memory (single server)
mcp = FastMCP("App")

# Redis (distributed)
from key_value.aio.stores.redis import RedisStore
mcp = FastMCP("App", session_state_store=RedisStore(...))
```

### Background Tasks

```python
# Requires: pip install 'fastmcp[tasks]'
@mcp.tool(task=True)
async def long_job(data: str) -> str:
    """Runs as a background task via Docket."""
    ...
```

## Integration Guides

For integrating with specific platforms, read:
- `INTEGRATIONS/claude-desktop.md` — Claude Desktop setup
- `INTEGRATIONS/claude-code.md` — Claude Code integration
- `INTEGRATIONS/anthropic.md` — Anthropic SDK
- `INTEGRATIONS/openai.md` — OpenAI integration
- `INTEGRATIONS/chatgpt.md` — ChatGPT plugin
- `INTEGRATIONS/cursor.md` — Cursor IDE
- `INTEGRATIONS/fastapi.md` — FastAPI integration
- `INTEGRATIONS/openapi.md` — OpenAPI schema support

## Prefect Horizon (Managed Hosting)

```bash
# Push to GitHub, sign in to horizon.prefect.io, create project
# Entrypoint: server.py:mcp
# Result: https://your-project.fastmcp.app/mcp
```

Free for personal projects, enterprise governance for teams.
