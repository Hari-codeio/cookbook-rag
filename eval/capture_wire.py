"""Capture the raw JSON-RPC exchange with one MCP server, with NO MCP library
on the client side.

    python eval/capture_wire.py [server_name]        (default: ingredient_db)

It starts the server exactly as mcp_config.json says, writes JSON-RPC lines to
its stdin by hand, and reads its stdout line by line. Every line in both
directions is saved verbatim to out/wire_raw.jsonl. wire.json at the repo root
is that capture plus hand-written annotations.

The point is to see that MCP over stdio is nothing more than this: one JSON
object per line, a request with an `id`, a response carrying the same `id`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.mcp_host import load_config  # noqa: E402  (config parsing only)

OUT = ROOT / "out" / "wire_raw.jsonl"

MESSAGES = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "cookbook-rag-host", "version": "week9"},
    }},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
        "name": "get_allergens", "arguments": {"ingredient": "creme fraiche"},
    }},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
        "name": "get_allergens", "arguments": {"ingredient": "creme fraiche lite"},
    }},
]


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "ingredient_db"
    spec = load_config()[name]
    command = sys.executable if spec["command"] == "python" else spec["command"]
    proc = subprocess.Popen(
        [command, *spec.get("args", [])],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    log: list[dict] = []
    for msg in MESSAGES:
        line = json.dumps(msg)
        proc.stdin.write(line + "\n")
        proc.stdin.flush()
        log.append({"direction": "host -> server", "line": line})
        if "id" not in msg:  # a notification gets no reply
            continue
        reply = proc.stdout.readline().rstrip("\n")
        log.append({"direction": "server -> host", "line": reply})
    proc.stdin.close()
    proc.wait(timeout=10)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in log) + "\n", encoding="utf-8")
    for e in log:
        print(f"{e['direction']}: {e['line']}")


if __name__ == "__main__":
    main()
