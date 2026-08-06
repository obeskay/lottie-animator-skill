"""The documentation must not teach patterns that render blank.

Five of the six complete compositions in references/examples.md once carried
the same defects the linter exists to catch: layers with no ip/op/st, shape
items missing required properties, transforms applied twice. A reader copying
them would have produced an empty canvas.

Every complete composition embedded in the docs is linted here, so the prose
and the tooling cannot drift apart again.
"""
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lottie_lint import Linter  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
DOCS = sorted((REPO / "skills" / "lottie-animator" / "references").glob("*.md")) + [
    REPO / "skills" / "lottie-animator" / "SKILL.md"
]

FENCE = re.compile(r"```json\n(.*?)```", re.S)

# Shape items whose absence blanks the layer, mirrored from the linter so a
# fragment is held to the same standard as a whole file.
from lottie_lint import SHAPE_NAMES, SHAPE_REQUIRED, STAR_REQUIRED  # noqa: E402


def _strip_annotations(snippet):
    """Docs annotate snippets with // comments and trailing commas."""
    snippet = re.sub(r"//[^\n]*", "", snippet)
    snippet = re.sub(r"/\*.*?\*/", "", snippet, flags=re.S)
    return re.sub(r",(\s*[}\]])", r"\1", snippet)


def fragments():
    """Every json snippet that parses once its annotations are removed."""
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        for match in FENCE.finditer(text):
            line = text[: match.start()].count("\n") + 1
            try:
                yield path, line, json.loads(_strip_annotations(match.group(1)))
            except json.JSONDecodeError:
                continue


def _shape_defects(node, out):
    if isinstance(node, dict):
        ty = node.get("ty")
        if isinstance(ty, str) and ty in SHAPE_REQUIRED:
            required = list(SHAPE_REQUIRED[ty])
            if ty == "sr" and node.get("sy", 1) == 1:
                required.extend(STAR_REQUIRED)
            if ty == "tr" and "sk" in node:
                required.append("sa")
            missing = [k for k in required if k not in node]
            if missing:
                out.append("%s missing %s" % (SHAPE_NAMES.get(ty, ty), ", ".join(missing)))
        if "k" in node and isinstance(node.get("a"), int) and not isinstance(node.get("a"), bool):
            stray = [k for k in ("i", "o", "t", "s", "h") if k in node]
            if stray:
                out.append("keyframe fields %s on the property" % ", ".join(stray))
        for value in node.values():
            _shape_defects(value, out)
    elif isinstance(node, list):
        for value in node:
            _shape_defects(value, out)


def complete_compositions():
    """Every fenced json block that is a whole Lottie file, not a fragment."""
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        for match in FENCE.finditer(text):
            line = text[: match.start()].count("\n") + 1
            try:
                data = json.loads(match.group(1))
            except json.JSONDecodeError:
                # Fragments and commented snippets are illustrative, not runnable.
                continue
            if isinstance(data, dict) and "layers" in data and "op" in data:
                yield path, line, data


class DocumentedExamplesTest(unittest.TestCase):
    def test_documented_compositions_lint_clean(self):
        checked = 0
        failures = []
        for path, line, data in complete_compositions():
            checked += 1
            for finding in Linter(data, source_name=path.name).run():
                if finding.severity == "error":
                    failures.append(
                        "%s:%d %s %s" % (path.name, line, finding.code, finding.message)
                    )
        self.assertGreater(checked, 0, "no complete compositions found in the docs")
        self.assertEqual(failures, [], "\n".join(failures))

    def test_snippet_fragments_carry_required_properties(self):
        """A partial snippet is still copied verbatim, so it must be correct.

        The walk-cycle example shipped a fill and a transform with no opacity,
        which drops the layer in every player.
        """
        checked = 0
        failures = []
        for path, line, data in fragments():
            checked += 1
            defects = []
            _shape_defects(data, defects)
            failures.extend("%s:%d %s" % (path.name, line, d) for d in defects)
        self.assertGreater(checked, 0, "no parseable snippets found in the docs")
        self.assertEqual(failures, [], "\n".join(failures))

    def test_every_reference_link_resolves(self):
        """SKILL.md linked shape-modifiers.md for months before it existed."""
        missing = []
        base = REPO / "skills" / "lottie-animator"
        for path in DOCS:
            for target in re.findall(r"\((references/[a-z0-9-]+\.md)\)", path.read_text()):
                if not (base / target).exists():
                    missing.append("%s -> %s" % (path.name, target))
        self.assertEqual(missing, [], "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
