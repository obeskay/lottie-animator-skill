"""Tests for the Lottie linter.

Each test pins a defect that shipped in this repository at some point and
rendered as a blank canvas while the old smoke test reported OK.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lottie_lint import Linter  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def base_animation():
    return {
        "v": "5.12.1", "fr": 60, "ip": 0, "op": 60, "w": 100, "h": 100,
        "nm": "Test", "ddd": 0, "assets": [],
        "layers": [
            {
                "ddd": 0, "ind": 1, "ty": 4, "nm": "Square", "sr": 1,
                "ks": {
                    "o": {"a": 0, "k": 100},
                    "r": {"a": 0, "k": 0},
                    "p": {"a": 1, "k": [
                        {"t": 0, "s": [50, 50, 0], "o": {"x": [0.33], "y": [0]},
                         "i": {"x": [0.67], "y": [1]}},
                        {"t": 59, "s": [60, 50, 0]},
                    ]},
                    "a": {"a": 0, "k": [0, 0, 0]},
                    "s": {"a": 0, "k": [100, 100, 100]},
                },
                "ao": 0,
                "shapes": [{
                    "ty": "gr", "nm": "Group", "it": [
                        {"ty": "rc", "p": {"a": 0, "k": [0, 0]},
                         "s": {"a": 0, "k": [20, 20]}, "r": {"a": 0, "k": 0}},
                        {"ty": "fl", "c": {"a": 0, "k": [1, 0, 0, 1]},
                         "o": {"a": 0, "k": 100}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]},
                         "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]},
                         "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}},
                    ],
                }],
                "ip": 0, "op": 60, "st": 0, "bm": 0,
            }
        ],
    }


def codes(animation, **kwargs):
    return {finding.code for finding in Linter(animation, **kwargs).run()}


class BaselineTest(unittest.TestCase):
    def test_clean_animation_reports_no_errors(self):
        findings = Linter(base_animation()).run()
        errors = [f for f in findings if f.severity == "error"]
        self.assertEqual(errors, [], [f.message for f in errors])


class DocumentTest(unittest.TestCase):
    def test_missing_top_level_key(self):
        animation = base_animation()
        del animation["fr"]
        self.assertIn("LT001", codes(animation))

    def test_op_must_exceed_ip(self):
        animation = base_animation()
        animation["op"] = 0
        self.assertIn("LT005", codes(animation))

    def test_empty_layers(self):
        animation = base_animation()
        animation["layers"] = []
        self.assertIn("LT008", codes(animation))


class LayerTest(unittest.TestCase):
    def test_layer_without_ip_op_is_an_error(self):
        """The morphing-star defect: the layer silently never renders."""
        animation = base_animation()
        del animation["layers"][0]["ip"]
        del animation["layers"][0]["op"]
        self.assertIn("LY005", codes(animation))

    def test_shape_layer_without_shapes(self):
        animation = base_animation()
        animation["layers"][0]["shapes"] = []
        self.assertIn("LY013", codes(animation))

    def test_duplicate_ind(self):
        animation = base_animation()
        animation["layers"].append(copy.deepcopy(animation["layers"][0]))
        self.assertIn("LY002", codes(animation))

    def test_unknown_parent(self):
        animation = base_animation()
        animation["layers"][0]["parent"] = 99
        self.assertIn("LY011", codes(animation))

    def test_parent_cycle(self):
        animation = base_animation()
        second = copy.deepcopy(animation["layers"][0])
        second["ind"] = 2
        animation["layers"][0]["parent"] = 2
        second["parent"] = 1
        animation["layers"].append(second)
        self.assertIn("LY012", codes(animation))

    def test_layer_outside_composition_range(self):
        animation = base_animation()
        animation["layers"][0]["ip"] = 90
        animation["layers"][0]["op"] = 120
        self.assertIn("LY008", codes(animation))

    def test_permanently_transparent_layer(self):
        animation = base_animation()
        animation["layers"][0]["ks"]["o"] = {"a": 0, "k": 0}
        self.assertIn("LY016", codes(animation))

    def test_geometry_without_paint(self):
        animation = base_animation()
        items = animation["layers"][0]["shapes"][0]["it"]
        animation["layers"][0]["shapes"][0]["it"] = [i for i in items if i["ty"] != "fl"]
        self.assertIn("LY015", codes(animation))


class ShapeSchemaTest(unittest.TestCase):
    """Missing shape properties make a player drop the whole layer."""

    def test_stroke_without_opacity(self):
        animation = base_animation()
        animation["layers"][0]["shapes"][0]["it"].insert(
            1, {"ty": "st", "c": {"a": 0, "k": [0, 0, 0, 1]}, "w": {"a": 0, "k": 2}}
        )
        self.assertIn("SH001", codes(animation))

    def test_polystar_without_outer_roundness(self):
        animation = base_animation()
        animation["layers"][0]["shapes"][0]["it"][0] = {
            "ty": "sr", "sy": 1,
            "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 0},
            "pt": {"a": 0, "k": 5}, "or": {"a": 0, "k": 10},
            "ir": {"a": 0, "k": 5}, "is": {"a": 0, "k": 0},
        }
        self.assertIn("SH001", codes(animation))

    def test_complete_polystar_passes(self):
        animation = base_animation()
        animation["layers"][0]["shapes"][0]["it"][0] = {
            "ty": "sr", "sy": 1,
            "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 0},
            "pt": {"a": 0, "k": 5}, "or": {"a": 0, "k": 10}, "os": {"a": 0, "k": 0},
            "ir": {"a": 0, "k": 5}, "is": {"a": 0, "k": 0},
        }
        self.assertNotIn("SH001", codes(animation))

    def test_polygon_does_not_need_inner_radius(self):
        animation = base_animation()
        animation["layers"][0]["shapes"][0]["it"][0] = {
            "ty": "sr", "sy": 2,
            "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 0},
            "pt": {"a": 0, "k": 6}, "or": {"a": 0, "k": 10}, "os": {"a": 0, "k": 0},
        }
        self.assertNotIn("SH001", codes(animation))


class KeyframeTest(unittest.TestCase):
    def test_misplaced_easing_handles(self):
        """The rocket defect: handles on the property blank the whole render."""
        animation = base_animation()
        prop = animation["layers"][0]["ks"]["p"]
        prop["o"] = {"x": [0.33], "y": [0]}
        prop["i"] = {"x": [0.67], "y": [1]}
        self.assertIn("KF011", codes(animation))

    def test_keyframe_times_must_increase(self):
        animation = base_animation()
        animation["layers"][0]["ks"]["p"]["k"][1]["t"] = -5
        self.assertIn("KF004", codes(animation))

    def test_single_keyframe_warns(self):
        animation = base_animation()
        animation["layers"][0]["ks"]["p"]["k"] = [{"t": 0, "s": [50, 50, 0]}]
        self.assertIn("KF005", codes(animation))

    def test_easing_x_outside_unit_range(self):
        animation = base_animation()
        animation["layers"][0]["ks"]["p"]["k"][0]["o"] = {"x": [1.8], "y": [0]}
        self.assertIn("KF009", codes(animation))

    def test_easing_y_may_overshoot(self):
        """Overshoot on y is how a bounce is built; it must not be an error."""
        animation = base_animation()
        animation["layers"][0]["ks"]["p"]["k"][0]["o"] = {"x": [0.34], "y": [1.56]}
        self.assertNotIn("KF009", codes(animation))

    def test_static_property_flagged_as_animated(self):
        animation = base_animation()
        animation["layers"][0]["ks"]["p"] = {"a": 1, "k": [50, 50, 0]}
        self.assertIn("KF002", codes(animation))


class LoopTest(unittest.TestCase):
    def test_open_loop_warns_when_looping(self):
        animation = base_animation()
        animation["nm"] = "Spinner Loop"
        self.assertIn("KF010", codes(animation))

    def test_open_loop_ignored_for_one_shot(self):
        animation = base_animation()
        animation["nm"] = "Rocket Launch"
        self.assertNotIn("KF010", codes(animation))

    def test_full_rotation_counts_as_closed(self):
        animation = base_animation()
        animation["nm"] = "Spinner Loop"
        animation["layers"][0]["ks"]["p"] = {"a": 0, "k": [50, 50, 0]}
        animation["layers"][0]["ks"]["r"] = {"a": 1, "k": [
            {"t": 0, "s": [0]}, {"t": 59, "s": [360]},
        ]}
        self.assertNotIn("KF010", codes(animation))


class MotionTest(unittest.TestCase):
    def test_static_composition_is_an_error(self):
        animation = base_animation()
        animation["layers"][0]["ks"]["p"] = {"a": 0, "k": [50, 50, 0]}
        self.assertIn("MQ001", codes(animation))

    def test_static_allowed_when_requested(self):
        animation = base_animation()
        animation["layers"][0]["ks"]["p"] = {"a": 0, "k": [50, 50, 0]}
        self.assertNotIn("MQ001", codes(animation, allow_static=True))

    def test_frame_switching_is_not_static(self):
        """A walk cycle animates via ip/op, not via keyframes."""
        animation = base_animation()
        animation["layers"][0]["ks"]["p"] = {"a": 0, "k": [50, 50, 0]}
        animation["layers"][0]["op"] = 30
        self.assertNotIn("MQ001", codes(animation))


class ShippedExamplesTest(unittest.TestCase):
    """Everything committed to the repository must lint clean."""

    def test_examples_are_clean(self):
        failures = []
        for path in sorted((REPO / "examples").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            findings = Linter(data, source_name=path.name).run()
            for finding in findings:
                if finding.severity == "error":
                    failures.append("%s: %s %s" % (path.name, finding.code, finding.message))
        self.assertEqual(failures, [], "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
