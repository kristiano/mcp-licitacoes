# FastMCP Tools — Detailed Reference

## The `@tool` Decorator

```python
@mcp.tool(
    name="find_products",           # Custom name (default: function name)
    description="Search catalog.",  # Custom description (default: docstring)
    tags={"catalog", "search"},     # Organization/filtering tags
    meta={"version": "1.2"},        # Custom metadata passed to clients
    timeout=30.0,                   # Execution timeout in seconds
    version="2",                    # Component versioning
    annotations={                   # MCP protocol annotations
        "title": "Find Products",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    output_schema={...},            # Manual JSON Schema for output
)
async def search(query: str) -> list[dict]:
    ...
```

## Type Annotations

FastMCP supports all Pydantic-compatible types:

| Type | Example | Notes |
|------|---------|-------|
| Basic | `int`, `float`, `str`, `bool` | Simple scalars |
| Binary | `bytes` | Raw strings, NOT auto-decoded base64 |
| Date/Time | `datetime`, `date`, `timedelta` | ISO format strings |
| Collections | `list[str]`, `dict[str, int]`, `set[int]` | |
| Optional | `float \| None`, `Optional[float]` | |
| Union | `str \| int` | |
| Constrained | `Literal["A", "B"]`, `Enum` | Enum: clients send values, not names |
| Path/UUID | `Path`, `UUID` | Auto-converted from strings |
| Pydantic | `class UserData(BaseModel)` | Must be JSON objects (dicts), not strings |

**`*args` and `**kwargs` are NOT supported** — FastMCP needs complete schemas.

## Parameter Metadata

### Simple descriptions
```python
from typing import Annotated

@mcp.tool
def process(
    url: Annotated[str, "URL of the image"],
    width: Annotated[int, "Target width in pixels"] = 800,
) -> dict: ...
```

### Advanced with Field
```python
from pydantic import Field

@mcp.tool
def process(
    width: Annotated[int, Field(description="Width", ge=1, le=2000)] = 800,
    format: Annotated[Literal["jpeg", "png"], Field(description="Format")] = "jpeg",
) -> dict: ...
```

Field supports: `description`, `ge/gt/le/lt`, `min_length/max_length`, `pattern`, `default`.

## Hiding Parameters (Dependency Injection)

```python
from fastmcp.dependencies import Depends

def get_user_id() -> str:
    return "user_123"

@mcp.tool
def get_details(user_id: str = Depends(get_user_id)) -> str:
    # user_id is injected, NOT shown to LLM
    return f"Details for {user_id}"
```

## Return Values & Content Blocks

| Return Type | MCP Content |
|-------------|-------------|
| `str` | `TextContent` |
| `bytes` | Base64 `BlobResourceContents` |
| `Image(path=...)` | `ImageContent` |
| `Audio(path=...)` | `AudioContent` |
| `File(path=...)` | Base64 `EmbeddedResource` |
| `list[...]` | Multiple content blocks |
| `None` | Empty response |
| `dict` / Pydantic / dataclass | `TextContent` + `structuredContent` |

### Media Helpers
```python
from fastmcp.utilities.types import Image, Audio, File

@mcp.tool
def get_chart() -> Image:
    return Image(path="chart.png")          # path= or data= (mutually exclusive)
    # Image(data=raw_bytes, format="png")   # format= required with data=
```

## Structured Output & Output Schemas

When a tool has return type annotations, FastMCP auto-generates output schemas and structured content.

- **Object returns** (`dict`, Pydantic, dataclass) → always become `structuredContent`
- **Primitive returns** (`int`, `str`, `list`) → become `structuredContent` only if return type is annotated (wrapped in `{"result": value}`)

```python
@mcp.tool
def calculate(a: int, b: int) -> int:
    return a + b
# Result: {"content": [{"type": "text", "text": "5"}], "structuredContent": {"result": 5}}
```

### ToolResult for Full Control

```python
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

@mcp.tool
def advanced() -> ToolResult:
    return ToolResult(
        content=[TextContent(type="text", text="Summary")],
        structured_content={"data": "value", "count": 42},
        meta={"execution_time_ms": 145},
    )
```

### Custom Serialization
```python
import yaml

@mcp.tool
def get_config() -> ToolResult:
    data = {"key": "value", "debug": True}
    return ToolResult(
        content=yaml.dump(data),
        structured_content=data,
    )
```

## Error Handling

```python
from fastmcp.exceptions import ToolError

@mcp.tool
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ToolError("Division by zero")  # Always sent to client
    return a / b

# mask_error_details=True hides non-ToolError messages
mcp = FastMCP("Secure", mask_error_details=True)
```

## Timeouts

```python
@mcp.tool(timeout=30.0)
async def fetch_data(url: str) -> dict:
    ...  # Returns MCP error code -32000 if exceeded
```

Timeouts don't apply to background tasks (`task=True`). Use Docket's `Timeout` for those.

## Annotations (MCP Protocol)

| Annotation | Type | Default | Purpose |
|-----------|------|---------|---------|
| `readOnlyHint` | bool | false | Tool only reads, no modifications |
| `destructiveHint` | bool | true | Changes are destructive |
| `idempotentHint` | bool | false | Repeated calls same effect |
| `openWorldHint` | bool | true | Interacts with external systems |
| `title` | str | - | Display name for UIs |

**`readOnlyHint=True`** is important — ChatGPT/Claude skip confirmation for read-only tools.

## Using with Class Methods

```python
from fastmcp.tools import tool

class Calculator:
    def __init__(self, multiplier: int):
        self.multiplier = multiplier

    @tool()
    def multiply(self, x: int) -> int:
        """Multiply x."""
        return x * self.multiplier

calc = Calculator(multiplier=3)
mcp.add_tool(calc.multiply)  # Only 'x' in schema, not 'self'
```

## Component Visibility

```python
mcp.disable(keys={"tool:admin_action"})   # Disable by key
mcp.disable(tags={"admin"})               # Disable by tag
mcp.enable(tags={"public"}, only=True)    # Allowlist mode
```

## Duplicate Handling

```python
mcp = FastMCP("Server", on_duplicate_tools="error")
# Options: "warn" (default), "error", "replace", "ignore"
```

## Removing Tools Dynamically

```python
mcp.local_provider.remove_tool("my_tool")
```

## Versioning

```python
@mcp.tool(version="2")
def my_tool() -> str: ...
# Clients auto-receive highest version
```
