"""The command-line contract.

CI decides whether a change is good by looking at exit codes, so those codes
are part of the interface: 0 for success, 1 when the content is bad, 2 when
the invocation or environment is wrong. A tool that reports a problem on
stderr and still exits 0 makes a green build meaningless.

Only the dependency-free Python tools are covered here. The renderer needs
Node and a browser, so CI exercises it in a separate job.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LINT = REPO / "scripts" / "lottie_lint.py"
CONVERT = REPO / "scripts" / "svg2lottie.py"

VALID_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
    '<rect width="10" height="10" fill="#f00"/></svg>'
)


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *[str(a) for a in args]],
        capture_output=True, text=True,
    )


class LinterCliTest(unittest.TestCase):
    def test_clean_examples_exit_zero(self):
        result = run(LINT, REPO / "examples")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unreadable_file_is_a_failure(self):
        result = run(LINT, REPO / "examples" / "does-not-exist.json")
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_json_is_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not json")
            result = run(LINT, path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid JSON", result.stdout + result.stderr)

    def test_broken_animation_is_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(json.dumps({
                "v": "5.12.1", "fr": 60, "ip": 0, "op": 60, "w": 10, "h": 10,
                "layers": [{"ind": 1, "ty": 4, "nm": "X", "ks": {}, "shapes": []}],
            }))
            result = run(LINT, path)
            self.assertEqual(result.returncode, 1)

    def test_json_output_is_machine_readable(self):
        result = run(LINT, REPO / "examples" / "shape-morph.json", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 1)
        self.assertTrue(payload[0]["ok"])
        self.assertIn("findings", payload[0])

    def test_strict_promotes_warnings_to_failures(self):
        """A file that passes normally must fail under --strict if it warns."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "warns.json"
            path.write_text(json.dumps({
                "v": "5.12.1", "fr": 60, "ip": 0, "op": 60, "w": 10, "h": 10,
                "nm": "Warns", "layers": [{
                    "ind": 1, "ty": 4, "nm": "X", "ip": 0, "op": 60, "st": 0,
                    "ks": {"o": {"a": 0, "k": 100}, "p": {"a": 1, "k": [
                        {"t": 0, "s": [0, 0, 0]}, {"t": 30, "s": [5, 5, 0]}]}},
                    "shapes": [{"ty": "gr", "nm": "g", "it": [
                        {"ty": "rc", "p": {"a": 0, "k": [0, 0]},
                         "s": {"a": 0, "k": [4, 4]}, "r": {"a": 0, "k": 0}},
                        {"ty": "fl", "c": {"a": 0, "k": [1, 0, 0, 1]},
                         "o": {"a": 0, "k": 100}},
                        # No anchor: advisory only, so this warns without failing.
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]},
                         "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0},
                         "o": {"a": 0, "k": 100}},
                    ]}],
                }],
            }))
            self.assertEqual(run(LINT, path).returncode, 0)
            self.assertEqual(run(LINT, path, "--strict").returncode, 1)

    def test_no_input_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(LINT)], cwd=tmp, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 2)


class ConverterCliTest(unittest.TestCase):
    def test_converts_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "in.svg"
            svg.write_text(VALID_SVG)
            out = Path(tmp) / "nested" / "out.json"
            result = run(CONVERT, svg, "-o", out)
            self.assertEqual(result.returncode, 0, result.stderr)
            # The output directory is created rather than reported as an error.
            self.assertTrue(out.exists())
            json.loads(out.read_text())

    def test_missing_source_is_an_environment_error(self):
        result = run(CONVERT, REPO / "nope.svg", "-o", "/tmp/unused.json")
        self.assertEqual(result.returncode, 2)

    def test_document_with_nothing_to_draw_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "empty.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>')
            result = run(CONVERT, svg, "-o", Path(tmp) / "out.json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("no drawable elements", result.stderr)

    def test_non_svg_input_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "page.svg"
            src.write_text("<html><body>not a drawing</body></html>")
            result = run(CONVERT, src, "-o", Path(tmp) / "out.json")
            self.assertEqual(result.returncode, 1)

    def test_converted_output_passes_the_linter(self):
        """The two tools have to agree, or the documented workflow breaks."""
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "in.svg"
            svg.write_text(VALID_SVG)
            out = Path(tmp) / "out.json"
            self.assertEqual(run(CONVERT, svg, "-o", out).returncode, 0)
            self.assertEqual(run(LINT, out, "--allow-static").returncode, 0)


if __name__ == "__main__":
    unittest.main()
