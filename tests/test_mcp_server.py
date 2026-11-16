"""The MCP server speaks JSON-RPC over stdio and runs the same scripts.

One conversation, the way a client holds it: initialize, the initialized
notification (which must get no reply), tools/list, then real tool calls.
`render` needs Chrome, so it is exercised by hand, not here.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SERVER = REPO / "scripts" / "mcp_server.py"


def converse(*messages):
    lines = "".join(json.dumps(m) + "\n" for m in messages)
    done = subprocess.run([sys.executable, str(SERVER)], input=lines, capture_output=True, text=True, timeout=60)
    return [json.loads(line) for line in done.stdout.splitlines()]


def call(i, name, **arguments):
    return {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


class McpServerTest(unittest.TestCase):
    def test_a_client_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            packed = str(Path(tmp) / "set.lottie")
            replies = converse(
                {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                 "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                call(3, "lint", path=str(REPO / "examples" / "success-check.json"), strict=True),
                call(4, "pack_dotlottie", inputs=[str(REPO / "examples" / "heart-like.json")], out=packed),
                call(5, "list_colors", path=packed),
                call(6, "lint", path=str(REPO / "examples" / "nope.json")),
                call(7, "recolor", path=packed),
                {"jsonrpc": "2.0", "id": 8, "method": "resources/list"},
            )
        by_id = {r["id"]: r for r in replies}
        self.assertEqual(sorted(by_id), [1, 2, 3, 4, 5, 6, 7, 8], "the notification must not be answered")
        self.assertEqual(by_id[1]["result"]["protocolVersion"], "2025-06-18")  # echoed back
        names = {t["name"] for t in by_id[2]["result"]["tools"]}
        self.assertEqual(names, {"lint", "svg_to_lottie", "list_colors", "recolor", "pack_dotlottie", "unpack_dotlottie", "render"})
        for tool in by_id[2]["result"]["tools"]:
            self.assertEqual(tool["inputSchema"]["type"], "object")
        self.assertFalse(by_id[3]["result"]["isError"])
        self.assertIn("PASS", by_id[3]["result"]["content"][0]["text"])
        self.assertIn("1 animation", by_id[4]["result"]["content"][0]["text"])
        self.assertRegex(by_id[5]["result"]["content"][0]["text"], r"#[0-9A-F]{6}")
        self.assertIn("exit 1", by_id[6]["result"]["content"][0]["text"])  # a verdict, not a crash
        self.assertTrue(by_id[7]["result"]["isError"])  # recolor without a map
        self.assertEqual(by_id[8]["error"]["code"], -32601)

    def test_garbage_gets_a_parse_error(self):
        done = subprocess.run([sys.executable, str(SERVER)], input="{nope\n", capture_output=True, text=True, timeout=30)
        self.assertEqual(json.loads(done.stdout)["error"]["code"], -32700)


if __name__ == "__main__":
    unittest.main()
