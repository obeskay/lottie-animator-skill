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
RECOLOR = REPO / "scripts" / "recolor.py"

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
                        {"t": 0, "s": [0, 0, 0], "o": {"x": [0.33], "y": [0]},
                         "i": {"x": [0.67], "y": [1]}},
                        {"t": 30, "s": [5, 5, 0]}]}},
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


def _colourful():
    """A colour in every place one hides: static and animated paint, a gradient, a solid."""
    red, black = [1, 0, 0, 1], [0, 0, 0, 1]
    return {
        "v": "5.12.1", "fr": 60, "ip": 0, "op": 60, "w": 10, "h": 10, "nm": "Colours",
        "layers": [
            {"ind": 1, "ty": 4, "nm": "Shape", "ip": 0, "op": 60, "st": 0, "ks": {}, "shapes": [
                {"ty": "gr", "nm": "g", "it": [
                    {"ty": "fl", "c": {"a": 0, "k": red}, "o": {"a": 0, "k": 100}},
                    {"ty": "st", "c": {"a": 1, "k": [
                        {"t": 0, "s": black, "o": {"x": [0.2], "y": [1]}, "i": {"x": [0.3], "y": [1]}},
                        {"t": 30, "s": red}]}, "o": {"a": 0, "k": 100}, "w": {"a": 0, "k": 1}},
                    {"ty": "gf", "o": {"a": 0, "k": 100}, "s": {"a": 0, "k": [0, 0]},
                     "e": {"a": 0, "k": [1, 1]}, "t": 1,
                     "g": {"p": 2, "k": {"a": 0, "k": [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1]}}},
                ]}]},
            {"ind": 2, "ty": 1, "nm": "Solid", "sc": "#ff0000", "sw": 10, "sh": 10,
             "ip": 0, "op": 60, "st": 0, "ks": {}},
        ],
    }


class RecolorCliTest(unittest.TestCase):
    def test_lists_every_colour_with_its_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "in.json"
            path.write_text(json.dumps(_colourful()))
            result = run(RECOLOR, path, "--list")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("#FF0000    4 uses  Shape, Solid", result.stdout)
            self.assertIn("#000000    2 uses  Shape", result.stdout)

    def test_replaces_a_colour_wherever_it_hides(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, out = Path(tmp) / "in.json", Path(tmp) / "out.json"
            path.write_text(json.dumps(_colourful()))
            result = run(RECOLOR, path, "--map", "#F00=#C8522B", "-o", out)
            self.assertEqual(result.returncode, 0, result.stderr)
            doc = json.loads(out.read_text())
            clay = [0.7843, 0.3216, 0.1686]
            items = doc["layers"][0]["shapes"][0]["it"]
            self.assertEqual(items[0]["c"]["k"][:3], clay)
            self.assertEqual(items[0]["c"]["k"][3], 1)            # alpha untouched
            self.assertEqual(items[1]["c"]["k"][1]["s"][:3], clay)
            self.assertEqual(items[1]["c"]["k"][0]["s"][:3], [0, 0, 0])
            self.assertEqual(items[2]["g"]["k"]["k"][1:4], clay)  # first stop, offset kept
            self.assertEqual(doc["layers"][1]["sc"], "#c8522b")

    def test_a_colour_that_is_not_there_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "in.json"
            path.write_text(json.dumps(_colourful()))
            self.assertEqual(run(RECOLOR, path, "--map", "#123456=#000000").returncode, 1)
            self.assertEqual(run(RECOLOR, path, "--map", "not-a-colour=#000000").returncode, 2)


if __name__ == "__main__":
    unittest.main()
