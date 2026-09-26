"""The gateway: ONE MCP server in front of many.

    python -m mcp_servers.gateway.server        (stdio; started by the host)

To the host it is an ordinary MCP server. Behind it, it is an MCP CLIENT of
every server listed in upstreams.json. On tools/list it returns the union of
their tools, unchanged. On tools/call it:

  1. checks the caller's token scope, and refuses out-of-scope tools with a
     recoverable message the model can act on;
  2. forwards the call to whichever upstream owns that tool;
  3. writes ONE audit line: caller, tool, upstream, ingredient queried, decision.

Still no model here. The gateway decides "may this caller use this tool", which
is policy, not reasoning. The model stays in the host.

Built on the low-level Server rather than FastMCP because FastMCP derives each
tool's schema from a Python signature, and a proxy has no signature. It must
pass the upstream's inputSchema through verbatim.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from contextlib import AsyncExitStack, asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anyio
import mcp.types as types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import get_default_environment, stdio_client
from mcp.server.lowlevel import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.stdio import stdio_server

HERE = Path(__file__).parent
UPSTREAMS = Path(os.environ.get("GATEWAY_UPSTREAMS", HERE / "upstreams.json"))
TOKENS = Path(os.environ.get("GATEWAY_TOKENS", HERE / "tokens.json"))
AUDIT_LOG = Path(os.environ.get("GATEWAY_AUDIT_LOG", "out/gateway_audit.log"))

# The token is presented once, when the host starts this process, so the
# caller's identity is fixed for the whole session. Only its sha256 is stored.
_TOKEN = os.environ.get("GATEWAY_TOKEN", "")
_GRANT: dict[str, Any] | None = json.loads(TOKENS.read_text(encoding="utf-8")).get(
    hashlib.sha256(_TOKEN.encode()).hexdigest()
) if _TOKEN else None
CALLER = _GRANT["caller"] if _GRANT else "anonymous"

sessions: dict[str, ClientSession] = {}
tool_owner: dict[str, str] = {}
tools: list[types.Tool] = []
resource_owner: dict[str, str] = {}
resources: list[types.Resource] = []


def _params(spec: dict[str, Any]) -> StdioServerParameters:
    env = get_default_environment()
    env.update({k: str(v) for k, v in (spec.get("env") or {}).items()})
    command = sys.executable if spec["command"] == "python" else spec["command"]
    return StdioServerParameters(command=command, args=spec.get("args", []), env=env, cwd=os.getcwd())


@asynccontextmanager
async def lifespan(_server: Server):
    upstreams = json.loads(UPSTREAMS.read_text(encoding="utf-8"))["mcpServers"]
    async with AsyncExitStack() as stack:
        errlog = stack.enter_context(open(os.devnull, "w"))
        for name, spec in upstreams.items():
            read, write = await stack.enter_async_context(stdio_client(_params(spec), errlog=errlog))
            session = await stack.enter_async_context(ClientSession(read, write))
            init = await session.initialize()
            sessions[name] = session
            for tool in (await session.list_tools()).tools:
                tool_owner[tool.name] = name
                tools.append(tool)
            if init.capabilities.resources:
                for res in (await session.list_resources()).resources:
                    resource_owner[str(res.uri)] = name
                    resources.append(res)
        yield {}


server = Server("recipe-gateway", version="week9", lifespan=lifespan)


def _allowed(tool: str) -> bool:
    if _GRANT is None:
        return False
    allow = _GRANT.get("allow_tools")
    if allow is not None and tool not in allow:
        return False
    return tool not in _GRANT.get("deny_tools", [])


def _queried(arguments: dict[str, Any]) -> Any:
    for key in ("ingredient", "name", "ingredients", "query", "recipe_id"):
        if key in arguments:
            return arguments[key]
    return None


def _audit(tool: str, arguments: dict[str, Any], decision: str, is_error: bool) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "caller": CALLER,
            "tool": tool,
            "upstream": tool_owner.get(tool),
            "ingredient_queried": _queried(arguments),
            "decision": decision,
            "isError": is_error,
        }, ensure_ascii=False) + "\n")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return tools


@server.call_tool(validate_input=False)  # the upstream validates against its own schema
async def call_tool(name: str, arguments: dict[str, Any]) -> types.CallToolResult:
    if name not in tool_owner:
        _audit(name, arguments, "unknown_tool", True)
        return _error(f"no tool named {name!r} behind this gateway.")
    if not _allowed(name):
        still = [t.name for t in tools if _allowed(t.name)]
        _audit(name, arguments, "deny", True)
        return _error(
            f"permission denied: caller {CALLER!r} is not scoped for {name}. This is an access "
            f"policy, not a fault, and retrying will be denied again. Still allowed: "
            f"{', '.join(still) or 'nothing'}. Tell the user this data is unavailable to you; "
            f"do not estimate it."
        )
    result = await sessions[tool_owner[name]].call_tool(name, arguments)
    _audit(name, arguments, "allow", bool(result.isError))
    return result  # passed through unchanged: content, structuredContent, isError


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    return resources


@server.read_resource()
async def read_resource(uri) -> list[ReadResourceContents]:
    res = await sessions[resource_owner[str(uri)]].read_resource(uri)
    return [ReadResourceContents(content=getattr(c, "text", ""), mime_type=c.mimeType) for c in res.contents]


def _error(text: str) -> types.CallToolResult:
    return types.CallToolResult(content=[types.TextContent(type="text", text=text)], isError=True)


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    anyio.run(main)
