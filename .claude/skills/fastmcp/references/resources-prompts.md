# FastMCP Resources & Prompts — Detailed Reference

## Resources

### The `@resource` Decorator

```python
@mcp.resource(
    uri="data://app-status",          # Required — unique URI
    name="ApplicationStatus",         # Custom name (default: function name)
    description="Current app status", # Custom description (default: docstring)
    mime_type="application/json",     # MIME type (inferred if not set)
    tags={"monitoring", "status"},    # Categorization tags
    meta={"version": "2.1"},          # Custom metadata
    version="2",                      # Component versioning
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def get_status() -> str:
    return json.dumps({"status": "ok"})
```

### Return Values

| Return | Content Type |
|--------|-------------|
| `str` | `TextResourceContents` (text/plain) |
| `bytes` | `BlobResourceContents` (application/octet-stream) |
| `ResourceResult` | Full control over contents and metadata |

For structured data (dicts, lists), serialize with `json.dumps()` — don't return raw dicts.

### ResourceResult

```python
from fastmcp.resources import ResourceResult, ResourceContent

@mcp.resource("data://users")
def get_users() -> ResourceResult:
    return ResourceResult(
        contents=[
            ResourceContent(content='[{"id": 1}]', mime_type="application/json"),
            ResourceContent(content="# Users\n...", mime_type="text/markdown"),
        ],
        meta={"total": 1},
    )

# Simple shortcuts
return ResourceResult("plain text")
return ResourceResult(b"\x00\x01\x02")
```

### Resource Classes (static content)

```python
from fastmcp.resources import FileResource, TextResource, DirectoryResource

mcp.add_resource(FileResource(
    uri="file:///app/README.md",
    path=Path("./README.md").resolve(),
    mime_type="text/markdown",
))

mcp.add_resource(TextResource(
    uri="resource://notice",
    text="System maintenance Sunday.",
))

mcp.add_resource(DirectoryResource(
    uri="resource://data-files",
    path=Path("./data").resolve(),
    recursive=False,
))
```

Available: `TextResource`, `BinaryResource`, `FileResource`, `HttpResource`, `DirectoryResource`.

## Resource Templates

Parameterized URIs with `{param}` placeholders.

```python
@mcp.resource("weather://{city}/current")
def get_weather(city: str) -> str:
    return json.dumps({"city": city, "temp": 22})

# Wildcard — matches multiple path segments
@mcp.resource("path://{filepath*}")
def get_file(filepath: str) -> str:
    return f"Content at: {filepath}"

# Multiple params + wildcard
@mcp.resource("repo://{owner}/{path*}/template.py")
def get_template(owner: str, path: str) -> dict:
    return {"owner": owner, "path": path}
```

### Query Parameters (RFC 6570)

```python
@mcp.resource("data://{id}{?format,limit}")
def get_data(id: str, format: str = "json", limit: int = 10) -> str:
    ...
# Requests: data://123, data://123?format=xml&limit=50
```

Rules:
- Path params → required function params (no defaults)
- Query params → optional function params (must have defaults)
- All URI template params must exist as function params

### Template Parameter Rules

```python
# Multiple templates for one function
def lookup_user(name: str | None = None, email: str | None = None) -> dict:
    ...

mcp.resource("users://email/{email}")(lookup_user)
mcp.resource("users://name/{name}")(lookup_user)
```

## Prompts

### The `@prompt` Decorator

```python
@mcp.prompt(
    name="analyze_data",               # Custom name
    description="Analysis request",    # Custom description
    tags={"analysis"},                 # Tags
    meta={"version": "1.1"},           # Metadata
    version="2",                       # Versioning
)
def analysis_prompt(dataset: str, focus: str = "summary") -> str:
    return f"Analyze {dataset} focusing on {focus}"
```

### Return Values

| Return | Result |
|--------|--------|
| `str` | Single user message |
| `list[Message \| str]` | Conversation (strings auto-wrapped as user messages) |
| `PromptResult` | Full control over messages + metadata |

### Message Class

```python
from fastmcp.prompts import Message

Message("Hello!")                    # user role (default)
Message("I can help.", role="assistant")
Message({"key": "value"})           # Auto-serialized to JSON text
Message(["item1", "item2"])
```

### PromptResult

```python
from fastmcp.prompts import PromptResult, Message

@mcp.prompt
def code_review(code: str) -> PromptResult:
    return PromptResult(
        messages=[
            Message(f"Review:\n```\n{code}\n```"),
            Message("I'll analyze this.", role="assistant"),
        ],
        description="Code review prompt",
        meta={"review_type": "security"},
    )
```

### Typed Arguments

MCP spec requires string arguments, but FastMCP auto-converts:
```python
@mcp.prompt
def analyze(numbers: list[int], threshold: float) -> str:
    avg = sum(numbers) / len(numbers)
    return f"Average: {avg}, above threshold: {avg > threshold}"
# Client sends: {"numbers": "[1,2,3]", "threshold": "2.5"}
```

Keep types simple: `list[int]`, `dict[str, str]`, `float`, `bool`. Avoid complex Pydantic models.

## Error Handling (Both)

```python
from fastmcp.exceptions import ResourceError

@mcp.resource("data://safe")
def fail_safe() -> str:
    raise ResourceError("File not found")  # Always sent to client

# mask_error_details=True masks non-ResourceError/ToolError messages
```

## Visibility & Duplicates

Same as tools:
```python
mcp.disable(keys={"resource:data://secret"})
mcp.disable(tags={"internal"})
mcp.enable(tags={"public"}, only=True)

mcp = FastMCP("Server", on_duplicate_resources="error")
mcp = FastMCP("Server", on_duplicate_prompts="error")
```
