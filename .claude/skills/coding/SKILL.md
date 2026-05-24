---
name: coding
description: "Use this skill for all Python coding work — writing new code, implementing features, debugging, testing, managing Git commits, updating documentation, and maintaining requirements.txt. This is stage 5 of the development pipeline. Trigger when the user says 'let's code', 'write the code', 'implement this', 'build it', 'coding', 'debug this', 'fix this', 'add a feature', 'write a test', 'commit this', 'update requirements', or when handing off from a completed Project Plan. This skill governs all active development work."
---

# Coding Skill

You are running the **Coding** stage — stage 5 of the development pipeline. Your job is to implement the project according to the Architecture document and Project Plan, following Matt's coding standards precisely.

The user (Matt) is actively learning Python OOP. Write clean, well-commented code and explain reasoning as you go. Never just drop code without context — help him understand what's happening and why.

---

## Before Writing Any Code

Check that the following exist. If any are missing, create or confirm them first:

- [ ] Project folder at `F:\Pycharm Projects\project-name\`
- [ ] Virtual environment created and activated
- [ ] `.gitignore` in place (includes venv/, __pycache__/, .env)
- [ ] `requirements.txt` (even if empty)
- [ ] Git repo initialised and connected to GitHub
- [ ] Architecture document exists in `docs/`
- [ ] Project plan exists in `docs/`

If any of these are missing, set them up before writing a single line of feature code.

---

## MCP Architecture Check

Before coding anything, check the **MCP Architecture & Ecosystem Check** section of the Product Design Brief and the **MCP Integration Decisions** section of the Architecture document. The coding approach differs significantly depending on what was decided there.

---

**If the architecture type is "App using MCPs" or "Hybrid":**

The app connects to MCP servers as its integration layer instead of calling raw APIs directly. Install the MCP Python SDK:

```bash
pip install mcp
pip freeze > requirements.txt
```

Create an integration class that wraps the MCP connection — keep this thin, with all business logic in separate classes per the architecture:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPIntegration:
    """Connects to an MCP server and calls its tools."""

    async def call_tool(self, server_command: str, tool_name: str, arguments: dict) -> str:
        """Call a named tool on the specified MCP server."""
        server_params = StdioServerParameters(command=server_command, args=[])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result.content[0].text
```

Use the Architecture document's **MCP Integration Decisions** section to know exactly which MCP servers are in use, which tools they expose, and what the security assessment found. Do not discover this at coding time — it should already be on file.

---

**If the architecture type is "MCP server" or "Hybrid":**

The product itself is an MCP server that exposes tools, resources, or prompts for Claude Desktop or other AI agents to consume. Use FastMCP — the high-level Python SDK for building MCP servers:

```bash
pip install mcp
pip freeze > requirements.txt
```

Basic server structure:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Server Name")

@mcp.tool()
def my_tool(param: str) -> str:
    """What this tool does — this description appears in Claude's tool list."""
    return f"Result: {param}"

@mcp.resource("resource://my-data")
def my_resource() -> str:
    """A resource Claude can read."""
    return "resource content here"

if __name__ == "__main__":
    mcp.run()
```

Keep all business logic in separate classes per the architecture document. The `@mcp.tool()` and `@mcp.resource()` decorators are the interface layer only — they should be thin wrappers calling into the proper class structure:

```python
from mcp.server.fastmcp import FastMCP
from src.logic.processor import DataProcessor

mcp = FastMCP("My Server Name")
_processor = DataProcessor()

@mcp.tool()
def process_data(input: str) -> str:
    """Process input data and return a result."""
    return _processor.run(input)
```

Test the server locally before moving to deploy:

```bash
# Interactive testing with the MCP inspector
mcp dev src/main.py
```

The Deploy stage has specific guidance for distributing an MCP server — it is different from a standard web app deployment.

---

**If the architecture type is "No external integrations" or plain "App using raw APIs":**

No MCP-specific setup needed. Proceed with standard coding below.

---

## Coding Standards

All code must follow these standards. This is not optional — they exist to keep the project maintainable.

### OOP Principles

- Every meaningful unit of functionality lives in a class
- Classes have a single, clear responsibility
- Use `__init__` to set up state; don't do heavy work there
- Keep methods short — if a method does two different things, split it
- Prefer composition (passing objects in) over deep inheritance
- Use class and instance attributes deliberately — don't store things you don't need

### Type Hints

All method signatures must include type hints:

```python
def fetch_data(self, endpoint: str, params: dict) -> list[dict]:
```

Use `Optional[type]` for values that can be None. Import from `typing` for Python < 3.10.

### Docstrings

Every class and every public method gets a docstring:

```python
class APIClient:
    """Handles all HTTP communication with the external API.

    Manages authentication, request construction, and error handling.
    Does not contain any business logic.
    """

    def get(self, endpoint: str, params: dict = None) -> dict:
        """Make a GET request to the specified endpoint.

        Args:
            endpoint: The API path (e.g., '/users/search')
            params: Optional query parameters

        Returns:
            Parsed JSON response as a dictionary

        Raises:
            APIError: If the request fails or returns an error status
        """
```

### Error Handling

Never let the app crash silently. Design error handling from the start:

```python
try:
    response = self.client.get('/data')
except requests.exceptions.Timeout:
    logger.error("API request timed out")
    raise APIError("Service unavailable — please try again")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        raise APIError("Invalid API key — check your .env file")
    elif e.response.status_code == 429:
        raise APIError("Rate limit hit — slow down requests")
    else:
        logger.error(f"HTTP error: {e}")
        raise
```

### Logging

Use Python's `logging` module, not `print()`:

```python
import logging
logger = logging.getLogger(__name__)

# In main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Environment Variables

All secrets and configuration in `.env`, loaded via `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise EnvironmentError("API_KEY not set in .env file")
```

---

## Package Management

Every time a new package is added:

1. Install it: `pip install package-name`
2. Update requirements immediately: `pip freeze > requirements.txt`
3. Commit both the code change and the updated requirements.txt together

```bash
git add requirements.txt src/wherever/the_change_was.py
git commit -m "feat: add package-name for [reason]"
```

Never let requirements.txt fall out of sync with what's installed.

---

## Testing

Write tests alongside features, not after. Use `pytest`.

```
tests/
├── test_api_client.py
├── test_processor.py
└── conftest.py          # shared fixtures
```

**Minimum test coverage per class:**
- Happy path: does it work correctly with valid input?
- Error path: does it handle bad/missing input gracefully?
- Edge cases: empty lists, None values, unexpected types

Run tests before every commit:

```bash
pytest tests/ -v
```

If tests fail, fix them before committing. Never commit broken tests.

---

## Git Workflow

### Branching

```bash
# New feature
git checkout dev
git checkout -b feature/short-description

# When done
git checkout dev
git merge feature/short-description
git branch -d feature/short-description
```

Work on `dev`. Merge to `main` only when a milestone is stable and tested.

### Commit Discipline

- Commit early and often — small commits are easier to understand and revert
- One logical change per commit
- Never commit: venv/, .env, __pycache__, .pyc files

Commit message format:
```
type: short description (under 72 chars)

Optional longer explanation if the why isn't obvious.
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

### Milestone Tagging

At the end of each milestone:
```bash
git tag -a v0.1.0 -m "Milestone 1: Core skeleton complete"
git push origin dev --tags
```

---

## Documentation

Update `docs/logic.md` as you build. Capture:

- Non-obvious decisions ("We use X instead of Y because...")
- Data flow descriptions for complex logic
- Known limitations or future improvement notes
- Any API quirks or gotchas discovered

Don't leave this to the end — write it while the context is fresh.

---

## Working Through the Project Plan

When building, work milestone by milestone:

1. State which task from the project plan you're starting
2. Write the code
3. Explain what it does and why it's structured the way it is
4. Run any relevant tests
5. Commit with an appropriate message
6. Update requirements.txt if needed
7. Update docs/logic.md if anything non-obvious was implemented
8. Check off the task in the project plan
9. Move to the next task

At the end of each milestone, confirm with the user before moving on.

---

## Handing Off to QA

When a milestone or significant feature is complete:

> "The implementation is done. I'd recommend a **QA** pass now to review the code for correctness, efficiency, and edge cases before we continue. Ready to switch to the QA skill?"

Or if the full MVP is complete:

> "The MVP is built and tested. Ready for the **QA** skill to do a full review before we move to Deploy?"
