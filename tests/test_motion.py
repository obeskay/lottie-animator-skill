"""motion.py is what generators are told to use, so its promises are pinned.

A token that emits a bare keyframe would reintroduce the KF012 freeze in every
file written with it; a house curve with overshoot would quietly undo the
taste defaults; a builder that forgets a required property blanks the layer;
a palette whose ink sits too close to its ground makes art that disappears.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lottie_lint import ERROR, SHAPE_REQUIRED, Linter  # noqa: E402
from motion import (  # noqa: E402
    EASE, PALETTES, comp, ellipse, fill, group, layer, null, path, rect, repeater,
    squircle, star, stroke, svg, track, trim,
)


def luminance(hex_color):
    channels = [int(hex_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class MotionTokensTest(unittest.TestCase):
    def test_track_never_emits_a_bare_keyframe(self):
        for name in list(EASE) + ["hold"]:
            keys = track((0, 0, name), (10, 50, name), (20, 100))["k"]
            for key in keys[:-1]:
                self.assertTrue(key.get("h") or ("o" in key and "i" in key), (name, key))

    def test_house_curves_do_not_overshoot(self):
        for name, ((x1, y1), (x2, y2)) in EASE.items():
            self.assertTrue(0 <= x1 <= 1 and 0 <= x2 <= 1, name)
            if name != "playful":
                self.assertTrue(0 <= y1 <= 1 and 0 <= y2 <= 1, name)

    def test_squircle_is_closed_centred_and_stays_in_bounds(self):
        shape = squircle(100, 60, 10)
        self.assertTrue(shape["c"])
        self.assertEqual(len(shape["v"]), 8)
        self.assertAlmostEqual(sum(v[0] for v in shape["v"]), 0, places=6)
        self.assertAlmostEqual(sum(v[1] for v in shape["v"]), 0, places=6)
        for (x, y), (ox, oy), (ix, iy) in zip(shape["v"], shape["o"], shape["i"]):
            for px, py in ((x + ox, y + oy), (x + ix, y + iy)):
                self.assertTrue(abs(px) <= 50 and abs(py) <= 30, (px, py))


class BuildersTest(unittest.TestCase):
    def test_every_builder_emits_its_required_properties(self):
        items = [ellipse(10), rect(10), star(5, 10, 5), star(6, 10), path(squircle(10, 10, 2)),
                 fill("#C8522B"), stroke("#1E1B18", 2, dash=(4, 2)), trim(0, 50),
                 repeater(3, r=30), group("G", ellipse(4))["it"][-1]]
        for item in items:
            missing = [k for k in SHAPE_REQUIRED.get(item["ty"], ()) if k not in item]
            self.assertEqual(missing, [], item["ty"])

    def test_a_built_composition_lints_clean(self):
        spin = track((0, 0, "linear"), (60, 360))
        doc = comp("Builder Loop", 120, 120, [
            layer("Mark", group("Mark", *svg("M-10 0 L0 10 L12 -8"), stroke("#1E1B18", 4), trim(0, 60)),
                  p=(60, 60), parent="Pivot"),
            null("Pivot", p=(0, 0), r=spin),
            layer("Disc", group("Disc", ellipse(track((0, [40, 40], "in-out"), (30, [44, 44], "in-out"),
                                                      (60, [40, 40]))), fill("#C8522B")), p=(60, 60)),
        ], op=60, bg="#F3EEE6")
        self.assertEqual(doc["layers"][0]["parent"], 2)
        errors = [f for f in Linter(doc, source_name="builder-loop.json").run() if f.severity == ERROR]
        self.assertEqual(errors, [])

    def test_layer_names_must_be_unique(self):
        with self.assertRaises(ValueError):
            comp("Twins", 10, 10, [layer("A"), layer("A")], op=10)


class PalettesTest(unittest.TestCase):
    """The roles promise legibility; these are the promises, measured (WCAG ratios)."""

    def test_every_palette_fills_every_role(self):
        roles = {"bg", "surface", "ink", "muted", "accent", "on_accent", "support"}
        for name, colours in PALETTES.items():
            self.assertEqual(set(colours), roles, name)

    def test_roles_stay_legible_on_their_ground(self):
        for name, c in PALETTES.items():
            with self.subTest(palette=name):
                self.assertGreaterEqual(contrast(c["ink"], c["bg"]), 7, "ink on bg")
                self.assertGreaterEqual(contrast(c["muted"], c["bg"]), 3, "muted on bg")
                self.assertGreaterEqual(contrast(c["accent"], c["bg"]), 3, "accent on bg")
                self.assertGreaterEqual(contrast(c["on_accent"], c["accent"]), 3, "on_accent on accent")
                self.assertGreaterEqual(contrast(c["support"], c["bg"]), 1.5, "support on bg")
                # A surface is a quiet mass: visible against the ground, never loud.
                self.assertTrue(1.08 <= contrast(c["surface"], c["bg"]) <= 1.6, "surface on bg")


if __name__ == "__main__":
    unittest.main()
