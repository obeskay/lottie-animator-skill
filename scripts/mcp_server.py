#!/usr/bin/env python3
"""The Lottie tools as an MCP server, for agents that do not read skills.

Cursor, Codex, Windsurf, Claude Desktop and any other MCP client can lint,
convert, recolour, pack and render Lottie files through this server; each
tool runs the same script the skill uses, so the results match.

    claude mcp add lottie-animator -- python3 /path/to/lottie-animator-skill/scripts/mcp_server.py

or, in any client's JSON config:

    {"mcpServers": {"lottie-animator": {"command": "python3",
      "args": ["/path/to/lottie-animator-skill/scripts/mcp_server.py"]}}}

Transport is stdio, one JSON-RPC message per line. `render` needs Node, a
local Chrome and `npm install` in the repository; it returns the contact sheet
as an image so the agent can look at the frames. Everything else is stdlib.
"""
from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSION = "2.2.0"
PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")


def _py(script, *args):
    return [sys.executable, str(HERE / script), *args]


def _schema(props):
    return {"type": "object", "properties": props, "required": [k for k, v in props.items() if not v.pop("optional", False)]}


TOOLS = {
    "lint": {
        "description": "Lint a Lottie .json or .lottie for the defects that render blank, freeze, pop at the loop or look generated. Returns findings with codes and fixes.",
        "inputSchema": _schema({
            "path": {"type": "string", "description": "a .json or .lottie file, or a folder"},
            "strict": {"type": "boolean", "description": "warnings fail too", "optional": True},
        }),
        "argv": lambda a: _py("lottie_lint.py", a["path"], *(["--strict"] if a.get("strict") else [])),
    },
    "svg_to_lottie": {
        "description": "Convert an SVG into Lottie shape layers, one named layer per element, each anchored at its own centre. Static until animated.",
        "inputSchema": _schema({
            "svg": {"type": "string", "description": "source .svg path"},
            "out": {"type": "string", "description": "output .json path", "optional": True},
            "size": {"type": "number", "description": "square canvas size in px", "optional": True},
        }),
        "argv": lambda a: _py("svg2lottie.py", a["svg"], *(["-o", a["out"]] if a.get("out") else []),
                              *(["--size", str(a["size"])] if a.get("size") else [])),
    },
    "list_colors": {
        "description": "List every colour in a Lottie .json or .lottie with how often it is used and by which layers.",
        "inputSchema": _schema({"path": {"type": "string"}}),
        "argv": lambda a: _py("recolor.py", a["path"], "--list"),
    },
    "recolor": {
        "description": "Replace colours in a Lottie: fills, strokes, gradients, animated colours, text and solids.",
        "inputSchema": _schema({
            "path": {"type": "string"},
            "map": {"type": "object", "description": 'old hex to new hex, e.g. {"#FF5A5F": "#C8522B"}',
                    "additionalProperties": {"type": "string"}},
            "out": {"type": "string", "description": "output path (.json or .lottie); default overwrites", "optional": True},
        }),
        "argv": lambda a: _py("recolor.py", a["path"], *[x for old, new in a["map"].items() for x in ("--map", "%s=%s" % (old, new))],
                              *(["-o", a["out"]] if a.get("out") else [])),
    },
    "pack_dotlottie": {
        "description": "Pack one or more Lottie JSON files into a single .lottie (dotLottie v2) archive.",
        "inputSchema": _schema({
            "inputs": {"type": "array", "items": {"type": "string"}},
            "out": {"type": "string", "description": "output .lottie path"},
        }),
        "argv": lambda a: _py("dotlottie.py", "pack", *a["inputs"], "-o", a["out"]),
    },
    "unpack_dotlottie": {
        "description": "Unpack a .lottie into one JSON per animation, images inlined.",
        "inputSchema": _schema({
            "path": {"type": "string"},
            "out_dir": {"type": "string", "description": "output folder", "optional": True},
        }),
        "argv": lambda a: _py("dotlottie.py", "unpack", a["path"], "-o", a.get("out_dir") or "."),
    },
    "render": {
        "description": "Render a Lottie .json in real lottie-web and return the contact sheet image. Flags empty frames, clipping and content off canvas. Look at it before calling an animation done.",
        "inputSchema": _schema({
            "path": {"type": "string", "description": "a Lottie .json (unpack a .lottie first)"},
            "at": {"type": "string", "description": "timeline percentages, e.g. 0,25,50,75,100", "optional": True},
            "onion": {"type": "boolean", "description": "also stack frames to read easing and arcs", "optional": True},
        }),
        "argv": lambda a: ["node", str(HERE / "render.mjs"), a["path"], "--out", tempfile.mkdtemp(prefix="lottie-render-"),
                           *(["--at", a["at"]] if a.get("at") else []),
                           *(["--onion"] if a.get("onion") else [])],
    },
}


def call(name, args):
    tool = TOOLS[name]
    try:
        argv = tool["argv"](args)
    except (KeyError, TypeError, AttributeError) as error:
        return {"content": [{"type": "text", "text": "bad arguments: %s" % error}], "isError": True}
    try:
        done = subprocess.run(argv, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"content": [{"type": "text", "text": str(error)}], "isError": True}
    text = (done.stdout + done.stderr).strip() or "(no output)"
    # exit 1 is a verdict about the file (lint findings, a colour not found), not a tool failure
    content = [{"type": "text", "text": "%s\n\nexit %d" % (text, done.returncode)}]
    for label in ("onion skin", "filmstrip"):
        match = re.search(r"^%s: (.+\.png)$" % label, done.stdout, re.M)
        if match and Path(match.group(1)).is_file():
            data = base64.b64encode(Path(match.group(1)).read_bytes()).decode("ascii")
            content.append({"type": "image", "data": data, "mimeType": "image/png"})
    return {"content": content, "isError": done.returncode >= 2}


def handle(message):
    method, params = message.get("method"), message.get("params") or {}
    if method == "initialize":
        asked = params.get("protocolVersion")
        return {
            "protocolVersion": asked if asked in PROTOCOLS else PROTOCOLS[0],
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "lottie-animator", "version": VERSION},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [{"name": n, "description": t["description"], "inputSchema": t["inputSchema"]} for n, t in TOOLS.items()]}
    if method == "tools/call":
        if params.get("name") not in TOOLS:
            raise LookupError("unknown tool %r" % params.get("name"))
        return call(params["name"], params.get("arguments") or {})
    raise LookupError("method not found: %s" % method)


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        else:
            if not isinstance(message, dict):
                reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request"}}
                sys.stdout.write(json.dumps(reply) + "\n")
                sys.stdout.flush()
                continue
            if "id" not in message:  # a notification: never answered
                continue
            try:
                reply = {"jsonrpc": "2.0", "id": message["id"], "result": handle(message)}
            except LookupError as error:
                reply = {"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32601, "message": str(error)}}
        sys.stdout.write(json.dumps(reply) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
