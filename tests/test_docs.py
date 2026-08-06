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
