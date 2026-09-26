"""The MCP host: read mcp_config.json, discover every server's tools, and hand
them to the unchanged Week 7 agent loop.

    python -m rag.mcp_host --list-tools
    python -m rag.mcp_host "Make the shakshuka 1.5x and take out the egg"

THREE ROLES, AND WHERE EACH ONE LIVES.
  host    this process. It owns the conversation and the ONLY model call
          (run_agent -> rag.llm.call_with_tools -> Gemini).
  client  one mcp.ClientSession per server, created below. It speaks JSON-RPC
          and knows nothing about models.
  server  a child process per entry in mcp_config.json. It gets a tool name and
          arguments, returns JSON, and never sees a model or an API key.

NOTHING IN THIS FILE NAMES A TOOL. What the model is offered is whatever
`tools/list` returned from the configured servers at start-up. Adding a server
is a config edit; this file and rag/agent.py stay byte-identical. That claim is
checked with `git diff` in results_week9.md, not asserted here.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
import threading
import time
import uuid
from contextlib import AsyncExitStack
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import get_default_environment, stdio_client

from rag.agent import SYSTEM_PROMPT, Budgets, run_agent
from rag.config import OUT_DIR, ROOT, _read_env
from rag.contract import RunResult
from rag.tools import ToolResult

CONFIG_PATH = ROOT / "mcp_config.json"
TRACE_PATH = OUT_DIR / "mcp_trace.jsonl"
SERVER_STDERR = OUT_DIR / "mcp_servers.stderr.log"
CALL_TIMEOUT_S = 30.0

_ENV_REF = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


def _expand(value: str) -> str:
    """${VAR} is filled from the environment or .env, so a token is never
    written into the committed config file."""
    return _ENV_REF.sub(lambda m: _read_env(m.group(1)) or "", value)


def load_config(path: Path = CONFIG_PATH) -> dict[str, dict[str, Any]]:
    """The same shape Claude Desktop and most MCP hosts use:
    {"mcpServers": {"<name>": {"command": ..., "args": [...], "env": {...}}}}"""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    servers = raw.get("mcpServers") or {}
    if not servers:
        raise SystemExit(f"{path}: no servers under 'mcpServers'")
    return servers


def _server_params(spec: dict[str, Any]) -> StdioServerParameters:
    command = spec["command"]
    # "python" means the interpreter running the host, so the config does not
    # hard-code a path to one machine's virtualenv.
    if command == "python":
        command = sys.executable
    env = get_default_environment()  # PATH and friends only: no API keys leak
    env.update({k: _expand(str(v)) for k, v in (spec.get("env") or {}).items()})
    cwd = spec.get("cwd")
    return StdioServerParameters(
        command=command,
        args=[_expand(str(a)) for a in spec.get("args", [])],
        env=env,
        cwd=str((ROOT / cwd).resolve()) if cwd else str(ROOT),
    )


@dataclass
class DiscoveredTool:
    server: str
    name: str
    description: str
    input_schema: dict[str, Any]


class MCPHost:
    """Owns one background event loop and one ClientSession per server.

    run_agent is synchronous and calls registry[name](**args). MCP sessions are
    async. So every session lives on a private loop in a daemon thread, and each
    registry entry is a small sync function that submits session.call_tool to
    that loop and waits. All sessions are opened and closed inside ONE task
    (_lifecycle), because anyio refuses to close a stdio pipe from a different
    task than the one that opened it.
    """

    def __init__(self, config_path: Path = CONFIG_PATH, run_id: str | None = None):
        self.config_path = Path(config_path)
        self.config = load_config(self.config_path)
        self.run_id = run_id or uuid.uuid4().hex[:8]
        self.sessions: dict[str, ClientSession] = {}
        self.server_info: dict[str, dict[str, Any]] = {}
        self.tools: list[DiscoveredTool] = []
        self.attached: list[tuple[str, str]] = []  # (uri, text) the APP attaches
        self.calls: list[dict[str, Any]] = []
        self._by_name: dict[str, DiscoveredTool] = {}
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._ready = threading.Event()
        self._shutdown: asyncio.Event | None = None
        self._lifecycle_future = None
        self._error: BaseException | None = None

    # -- start-up: initialize + tools/list against every configured server --

    def __enter__(self) -> "MCPHost":
        self._thread.start()
        self._lifecycle_future = asyncio.run_coroutine_threadsafe(self._lifecycle(), self._loop)
        self._ready.wait()
        if self._error is not None:
            self.__exit__(None, None, None)
            raise RuntimeError(f"MCP start-up failed: {self._error!r}") from self._error
        return self

    def __exit__(self, *exc) -> None:
        if self._shutdown is not None:
            self._loop.call_soon_threadsafe(self._shutdown.set)
        if self._lifecycle_future is not None:
            try:
                self._lifecycle_future.result(timeout=10)
            except Exception:  # noqa: BLE001 - shutdown is best effort
                pass
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)

    async def _lifecycle(self) -> None:
        try:
            SERVER_STDERR.parent.mkdir(parents=True, exist_ok=True)
            with open(SERVER_STDERR, "a", encoding="utf-8") as errlog:
                async with AsyncExitStack() as stack:
                    for name, spec in self.config.items():
                        await self._connect(stack, name, spec, errlog)
                    self._shutdown = asyncio.Event()
                    self._ready.set()
                    await self._shutdown.wait()
        except BaseException as exc:  # noqa: BLE001 - reported to the caller
            self._error = exc
            self._ready.set()

    async def _connect(self, stack: AsyncExitStack, name: str, spec: dict[str, Any], errlog) -> None:
        read, write = await stack.enter_async_context(
            stdio_client(_server_params(spec), errlog=errlog)
        )
        session = await stack.enter_async_context(ClientSession(read, write))
        init = await session.initialize()  # JSON-RPC "initialize" + "notifications/initialized"
        listed = await session.list_tools()  # JSON-RPC "tools/list"
        self.sessions[name] = session
        self.server_info[name] = {
            "serverInfo": init.serverInfo.model_dump(exclude_none=True),
            "protocolVersion": init.protocolVersion,
            "tools": [t.name for t in listed.tools],
        }
        for t in listed.tools:
            if t.name in self._by_name:
                raise ValueError(
                    f"tool name {t.name!r} is offered by both "
                    f"{self._by_name[t.name].server!r} and {name!r}; rename one in its server"
                )
            tool = DiscoveredTool(name, t.name, t.description or "", t.inputSchema)
            self.tools.append(tool)
            self._by_name[t.name] = tool
        # Resources are context the APP decides to attach, not something the
        # model fetches turn by turn. Only URIs the config names are attached.
        for uri in spec.get("attach_resources", []):
            res = await session.read_resource(uri)
            text = "\n".join(getattr(c, "text", "") for c in res.contents)
            self.attached.append((uri, text))

    # -- what run_agent receives ---------------------------------------------

    @property
    def tool_schemas(self) -> list[dict[str, Any]]:
        """MCP inputSchema is JSON Schema, and Gemini accepts JSON Schema as-is
        via parameters_json_schema, so nothing is hand-translated per tool."""
        return [
            {"name": t.name, "description": t.description, "parameters_json_schema": t.input_schema}
            for t in self.tools
        ]

    @property
    def registry(self) -> dict[str, Any]:
        return {t.name: self._caller(t.name) for t in self.tools}

    @property
    def system_prompt(self) -> str:
        if not self.attached:
            return SYSTEM_PROMPT
        blocks = "\n\n".join(f"[{uri}]\n{text}" for uri, text in self.attached)
        return (
            f"{SYSTEM_PROMPT}\nREFERENCE ATTACHED BY THE APP. This is context, not a "
            f"tool; you do not need to fetch it.\n\n{blocks}\n"
        )

    def _caller(self, name: str):
        def call(**arguments: Any) -> ToolResult:
            return self.call(name, arguments)

        return call

    # -- one tools/call --------------------------------------------------------

    def call(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        tool = self._by_name[name]
        session = self.sessions[tool.server]
        started = time.perf_counter()
        try:
            future = asyncio.run_coroutine_threadsafe(session.call_tool(name, arguments), self._loop)
            res = future.result(timeout=CALL_TIMEOUT_S)
        except Exception as exc:  # noqa: BLE001 - transport failure, reported as such
            # A dead server must not look like "no match": the model would
            # treat the silence as an answer and invent the missing facts.
            text = (
                f"server {tool.server!r} did not answer ({type(exc).__name__}: {exc}). "
                "This is a connection failure, not an empty result; do not guess what it would have said."
            )
            out, is_error = ToolResult(False, error=text), True
        else:
            text = "\n".join(c.text for c in res.content if getattr(c, "type", "") == "text")
            is_error = bool(res.isError)
            if is_error:
                out = ToolResult(False, error=text or "tool reported an error with no message")
            else:
                out = ToolResult(True, _as_dict(text, res.structuredContent))
        self._trace(tool, arguments, is_error, text, (time.perf_counter() - started) * 1000.0)
        return out

    def _trace(self, tool: DiscoveredTool, arguments: dict[str, Any], is_error: bool, text: str, ms: float) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": self.run_id,
            "event": "tools/call",
            "server": tool.server,
            "tool": tool.name,
            "arguments": arguments,
            "isError": is_error,
            "result_text": text if len(text) <= 1500 else text[:1500] + " ...[truncated]",
            "ms": round(ms, 1),
        }
        self.calls.append(entry)
        TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACE_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def run(self, client, request: str, budgets: Budgets | None = None) -> RunResult:
        return run_agent(
            client,
            request,
            budgets=budgets,
            tool_schemas=self.tool_schemas,
            registry=self.registry,
            system_prompt=self.system_prompt,
        )


def _as_dict(text: str, structured: Any) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    if isinstance(structured, dict):
        return structured
    return {"text": text}


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Run the recipe agent with tools discovered over MCP.")
    ap.add_argument("request", nargs="?")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--list-tools", action="store_true", help="print what tools/list returned, then exit")
    ap.add_argument("--max-laps", type=int, default=Budgets.max_laps)
    ap.add_argument("--max-tokens", type=int, default=Budgets.max_tokens)
    ap.add_argument("--max-cost", type=float, default=Budgets.max_cost_usd)
    ap.add_argument("--max-seconds", type=float, default=Budgets.max_seconds)
    args = ap.parse_args()
    if not args.list_tools and not args.request:
        ap.error("give a request, or --list-tools")

    with MCPHost(Path(args.config)) as host:
        for name, info in host.server_info.items():
            si = info["serverInfo"]
            print(f"server {name!r}: {si.get('name')} v{si.get('version')} "
                  f"(protocol {info['protocolVersion']}) -> tools/list: {', '.join(info['tools'])}")
        print(f"{len(host.tools)} tools discovered: {', '.join(t.name for t in host.tools)}")
        for uri, _ in host.attached:
            print(f"attached resource: {uri}")
        if args.list_tools:
            return

        from rag.generate import build_client

        budgets = Budgets(args.max_laps, args.max_tokens, args.max_cost, args.max_seconds)
        print(f"run_id {host.run_id}\n")
        result = host.run(build_client(), args.request, budgets)

        for entry in result.log:
            print(json.dumps(entry, ensure_ascii=False))
        print("\nMCP tools/call trace (server -> tool):")
        for c in host.calls:
            flag = "ERROR" if c["isError"] else "ok"
            print(f"  [{c['server']}] {c['tool']}({json.dumps(c['arguments'], ensure_ascii=False)}) -> {flag}")
            if c["isError"]:
                print(f"      {c['result_text']}")
        print()
        print(f"ok            : {result.ok}")
        print(f"terminated_by : {result.terminated_by or '(ran to completion)'}")
        print(f"laps          : {result.laps}")
        print(f"tokens        : {result.total_tokens}")
        print(f"cost          : ${result.cost_usd:.6f}")
        if result.answer:
            print(json.dumps(result.answer, indent=2, ensure_ascii=False))
        elif result.error:
            print(f"error         : {result.error}")


if __name__ == "__main__":
    main()
