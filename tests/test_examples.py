"""Every example is a generator and the JSON it writes, and both ship.

The JSON is what a reader downloads and what the GIFs are rendered from; the
generator is what a reader copies. If they drift apart, the gallery shows
something the source no longer makes. And an example that only works in its
own palette is not the recipe the README says it is, so each one is linted in
every palette.
"""
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "examples"
sys.path.insert(0, str(REPO / "scripts"))

from lottie_lint import ERROR, WARN, Linter  # noqa: E402
from motion import PALETTES, dumps  # noqa: E402
from recolor import inventory  # noqa: E402

DEFAULT = re.compile(r'main\(build, __file__, palette="(\w+)"\)')


def generators():
    return sorted(EXAMPLES.glob("*.py"))


def load(path):
    spec = importlib.util.spec_from_file_location("example_" + path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def default_palette(path):
    match = DEFAULT.search(path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


class ExamplesTest(unittest.TestCase):
    def test_every_example_has_a_generator(self):
        made = {p.stem for p in generators()}
        shipped = {p.stem for p in EXAMPLES.glob("*.json")}
        self.assertEqual(shipped - made, set(), "JSON without the generator that writes it")
        self.assertEqual(made - shipped, set(), "generator whose JSON was never committed")

    def test_committed_json_is_what_the_generator_writes(self):
        for path in generators():
            with self.subTest(example=path.stem):
                palette = default_palette(path)
                self.assertIn(palette, PALETTES, "main() must name its default palette")
                built = dumps(load(path).build(PALETTES[palette])) + "\n"
                shipped = (EXAMPLES / (path.stem + ".json")).read_text(encoding="utf-8")
                self.assertEqual(built, shipped, "run: python3 examples/%s.py" % path.stem)

    def test_every_example_lints_clean_in_every_palette(self):
        for path in generators():
            build = load(path).build
            for name, colours in PALETTES.items():
                with self.subTest(example=path.stem, palette=name):
                    doc = json.loads(dumps(build(colours)))
                    self.assertEqual(doc["meta"]["tc"], colours["bg"])
                    findings = Linter(doc, source_name=path.stem + ".json").run()
                    bad = ["%s %s %s" % (f.code, f.where, f.message)
                           for f in findings if f.severity in (ERROR, WARN)]
                    self.assertEqual(bad, [])

    def test_colours_come_from_the_palette(self):
        """A hex literal in a generator is a colour that ignores --palette, and a
        computed blend is one the landing page cannot re-skin: every colour in
        every example is one of its palette's roles (tints are opacity)."""
        for path in generators():
            build = load(path).build
            with self.subTest(example=path.stem):
                self.assertEqual(re.findall(r"#[0-9A-Fa-f]{6}\b", path.read_text(encoding="utf-8")), [])
            for name, colours in PALETTES.items():
                with self.subTest(example=path.stem, palette=name):
                    used = set(inventory(json.loads(dumps(build(colours)))))
                    self.assertEqual(used - set(colours.values()), set())

    def test_every_example_is_in_the_gallery(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        for path in generators():
            with self.subTest(example=path.stem):
                self.assertTrue((REPO / "assets" / (path.stem + ".gif")).exists(),
                                "run: node scripts/make-gifs.mjs %s" % path.stem)
                self.assertIn("examples/%s.py" % path.stem, readme)


if __name__ == "__main__":
    unittest.main()
