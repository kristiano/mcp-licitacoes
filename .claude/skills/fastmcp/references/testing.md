# FastMCP Testing — Detailed Reference

## In-Memory Testing (Primary Approach)

Pass server directly to `Client` — no network, no deployment, milliseconds per test.

```python
from fastmcp import FastMCP, Client

async def test_greeting():
    server = FastMCP("Test")

    @server.tool
    def greet(name: str) -> str:
        """Greet a user."""
        return f"Hello, {name}!"

    async with Client(server) as client:
        result = await client.call_tool("greet", {"name": "Alice"})
        assert result.data == "Hello, Alice!"
```

### Testing Resources

```python
async def test_config_resource():
    server = FastMCP("Test")

    @server.resource("data://config")
    def get_config() -> str:
        return '{"version": "1.0"}'

    async with Client(server) as client:
        result = await client.read_resource("data://config")
        assert "1.0" in result[0].content
```

### Testing Prompts

```python
async def test_prompt():
    server = FastMCP("Test")

    @server.prompt
    def review(code: str) -> str:
        return f"Review: {code}"

    async with Client(server) as client:
        result = await client.get_prompt("review", {"code": "x = 1"})
        assert "Review:" in result.messages[0].content.text
```

### Testing Tool Errors

```python
async def test_divide_by_zero():
    server = FastMCP("Test")

    @server.tool
    def divide(a: int, b: int) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    async with Client(server) as client:
        with pytest.raises(Exception):
            await client.call_tool("divide", {"a": 10, "b": 0})
```

## Fixtures

Create reusable server configurations. **Don't open clients in fixtures** — it can cause event loop issues.

```python
import pytest
from fastmcp import FastMCP, Client

@pytest.fixture
def weather_server():
    server = FastMCP("Weather")

    @server.tool
    def get_temperature(city: str) -> dict:
        temps = {"NYC": 72, "LA": 85}
        return {"city": city, "temp": temps.get(city, 70)}

    return server

async def test_temperature(weather_server):
    async with Client(weather_server) as client:
        result = await client.call_tool("get_temperature", {"city": "LA"})
        assert result.data == {"city": "LA", "temp": 85}
```

## Mocking External Dependencies

```python
from unittest.mock import AsyncMock

async def test_with_mock_db():
    server = FastMCP("Data")

    mock_db = AsyncMock()
    mock_db.fetch_users.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]

    @server.tool
    async def list_users() -> list:
        return await mock_db.fetch_users()

    async with Client(server) as client:
        result = await client.call_tool("list_users", {})
        assert len(result.data) == 2
        mock_db.fetch_users.assert_called_once()
```

## HTTP Transport Testing

### In-Process (Preferred)

```python
from fastmcp import FastMCP, Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.utilities.tests import run_server_async

@pytest.fixture
async def http_url():
    server = FastMCP("Test")

    @server.tool
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    async with run_server_async(server) as url:
        yield url

async def test_http(http_url: str):
    async with Client(transport=StreamableHttpTransport(http_url)) as client:
        result = await client.ping()
        assert result is True

        greeting = await client.call_tool("greet", {"name": "World"})
        assert greeting.data == "Hello, World!"
```

### Subprocess (Special Cases)

For complete process isolation (STDIO transport, subprocess behavior):

```python
from fastmcp.utilities.tests import run_server_in_process

def run_server(host: str, port: int) -> None:
    server = FastMCP("Test")

    @server.tool
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    server.run(host=host, port=port)

@pytest.fixture
async def http_url():
    with run_server_in_process(run_server, transport="http") as url:
        yield f"{url}/mcp"
```

## Test Best Practices

### Single Behavior Per Test
```python
# GOOD: Tests one thing
async def test_tool_registration():
    mcp = FastMCP("test")

    @mcp.tool
    def add(a: int, b: int) -> int:
        return a + b

    tools = mcp.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "add"

# BAD: Tests multiple behaviors
async def test_everything():
    mcp = FastMCP("test")
    @mcp.tool
    def add(a: int, b: int) -> int:
        return a + b
    @mcp.resource("data://x")
    def x() -> str:
        return "x"
    assert mcp.list_tools()
    assert mcp.list_resources()
```

### Self-Contained Setup

Every test creates its own server — no shared state, run in any order.

### Inline Snapshots

```python
from inline_snapshot import snapshot

async def test_schema():
    mcp = FastMCP("test")

    @mcp.tool
    def calc(amount: float, rate: float = 0.1) -> dict:
        """Calculate tax."""
        return {"tax": amount * rate}

    tools = mcp.list_tools()
    assert tools[0].inputSchema == snapshot({
        "type": "object",
        "properties": {
            "amount": {"type": "number"},
            "rate": {"type": "number", "default": 0.1},
        },
        "required": ["amount"],
    })
```

Run `pytest --inline-snapshot=create` to auto-populate, `pytest --inline-snapshot=fix` to update.

## Pytest Markers

```python
@pytest.mark.integration       # Real external APIs
@pytest.mark.client_process    # Spawns subprocesses
```

Skip with: `pytest -m "not integration and not client_process"`

## Using with respx (HTTP mocking)

For testing client.py modules that make HTTP calls:

```python
import respx
import httpx

@respx.mock
async def test_api_client():
    respx.get("https://api.example.com/data").mock(
        return_value=httpx.Response(200, json={"result": "ok"})
    )

    result = await my_client.fetch_data()
    assert result == {"result": "ok"}
```
