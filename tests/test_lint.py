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

    def test_layer_without_st_is_an_error(self):
        """st is compared against the playhead too; undefined hides the layer."""
        animation = base_animation()
        del animation["layers"][0]["st"]
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

    def test_transform_without_anchor_is_advisory_not_an_error(self):
        """lottie-web defaults a missing anchor, so this must not read as fatal."""
        animation = base_animation()
        transform = next(
            i for i in animation["layers"][0]["shapes"][0]["it"] if i["ty"] == "tr"
        )
        del transform["a"]
        found = codes(animation)
        self.assertIn("SH003", found)
        self.assertNotIn("SH001", found)

    def test_transform_without_opacity_is_an_error(self):
        animation = base_animation()
        transform = next(
            i for i in animation["layers"][0]["shapes"][0]["it"] if i["ty"] == "tr"
        )
        del transform["o"]
        self.assertIn("SH001", codes(animation))

    def test_skew_without_its_axis_is_an_error(self):
        """A skew angle with no axis blanks the layer; the axis alone is fine."""
        animation = base_animation()
        transform = next(
            i for i in animation["layers"][0]["shapes"][0]["it"] if i["ty"] == "tr"
        )
        transform["sk"] = {"a": 0, "k": 0}
        self.assertIn("SH001", codes(animation))
        transform["sa"] = {"a": 0, "k": 0}
        self.assertNotIn("SH001", codes(animation))

    def test_gradient_without_type_is_advisory(self):
        animation = base_animation()
        items = animation["layers"][0]["shapes"][0]["it"]
        items[1] = {
            "ty": "gf",
            "s": {"a": 0, "k": [0, 0]}, "e": {"a": 0, "k": [10, 10]},
            "g": {"p": 2, "k": {"a": 0, "k": [0, 1, 0, 0, 1, 0, 0, 1]}},
            "o": {"a": 0, "k": 100},
        }
        found = codes(animation)
        self.assertIn("SH003", found)
        self.assertNotIn("SH001", found)

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


def _group(name, shape, fill=True, offset=(0, 0)):
    """A shape group holding one ellipse or rectangle, optionally filled."""
    items = [shape]
    if fill:
        items.append({"ty": "fl", "c": {"a": 0, "k": [1, 1, 1, 1]},
                      "o": {"a": 0, "k": 100}})
    items.append({"ty": "tr", "p": {"a": 0, "k": list(offset)},
                  "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]},
                  "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}})
    return {"ty": "gr", "nm": name, "it": items}


def _ellipse(cx, cy, w, h):
    return {"ty": "el", "p": {"a": 0, "k": [cx, cy]}, "s": {"a": 0, "k": [w, h]}}


def _rect(cx, cy, w, h, r=0):
    return {"ty": "rc", "p": {"a": 0, "k": [cx, cy]},
            "s": {"a": 0, "k": [w, h]}, "r": {"a": 0, "k": r}}


def _with_groups(*groups):
    animation = base_animation()
    animation["layers"][0]["shapes"] = list(groups)
    return animation


class OcclusionTest(unittest.TestCase):
    """panda-loader.json shipped for two releases with its face painted and
    then covered: Lottie draws shapes[0] on top, and the file was authored
    back-to-front. Nothing was malformed, so every other check passed."""

    def test_group_hidden_under_an_opaque_sibling_above_it(self):
        animation = _with_groups(
            _group("Face Base", _ellipse(0, 0, 80, 80)),
            _group("Pupils", _ellipse(0, 0, 10, 10)),
        )
        self.assertIn("SH004", codes(animation))

    def test_correct_order_is_not_reported(self):
        """The same two groups, authored front-to-back, are fine."""
        animation = _with_groups(
            _group("Pupils", _ellipse(0, 0, 10, 10)),
            _group("Face Base", _ellipse(0, 0, 80, 80)),
        )
        self.assertNotIn("SH004", codes(animation))

    def test_corner_of_an_ellipse_is_not_treated_as_covered(self):
        """An ellipse leaves its bounding-box corners visible, so a shape out
        there is still on screen. Using the bbox rather than the inscribed box
        would report this."""
        animation = _with_groups(
            _group("Disc", _ellipse(0, 0, 80, 80)),
            _group("Corner", _ellipse(36, 36, 6, 6)),
        )
        self.assertNotIn("SH004", codes(animation))

    def test_translucent_cover_is_not_reported(self):
        animation = _with_groups(
            _group("Glass", _ellipse(0, 0, 80, 80)),
            _group("Behind", _ellipse(0, 0, 10, 10)),
        )
        animation["layers"][0]["shapes"][0]["it"][1]["o"]["k"] = 40
        self.assertNotIn("SH004", codes(animation))

    def test_unfilled_cover_is_not_reported(self):
        """Geometry with no fill paints nothing and hides nothing."""
        animation = _with_groups(
            _group("Outline", _ellipse(0, 0, 80, 80), fill=False),
            _group("Behind", _ellipse(0, 0, 10, 10)),
        )
        self.assertNotIn("SH004", codes(animation))

    def test_animated_cover_is_not_reported(self):
        """A shape that moves may expose what is under it at some frame."""
        animation = _with_groups(
            _group("Sliding plate", _ellipse(0, 0, 80, 80)),
            _group("Behind", _ellipse(0, 0, 10, 10)),
        )
        animation["layers"][0]["shapes"][0]["it"][2]["p"] = {
            "a": 1, "k": [{"t": 0, "s": [0, 0]}, {"t": 30, "s": [200, 0]}],
        }
        self.assertNotIn("SH004", codes(animation))

    def test_rotated_cover_is_not_reported(self):
        animation = _with_groups(
            _group("Tilted", _rect(0, 0, 80, 80)),
            _group("Behind", _ellipse(0, 0, 10, 10)),
        )
        animation["layers"][0]["shapes"][0]["it"][2]["r"]["k"] = 45
        self.assertNotIn("SH004", codes(animation))

    def test_rounded_rectangle_shrinks_by_its_radius(self):
        """The rounded corner is not solid, so content there stays visible."""
        animation = _with_groups(
            _group("Card", _rect(0, 0, 80, 80, r=30)),
            _group("In the corner", _ellipse(34, 34, 4, 4)),
        )
        self.assertNotIn("SH004", codes(animation))

    def test_group_offset_by_its_transform_is_placed_correctly(self):
        """The covered group sits at the origin only after its transform."""
        animation = _with_groups(
            _group("Plate", _ellipse(0, 0, 80, 80)),
            _group("Moved out", _ellipse(0, 0, 6, 6), offset=(200, 200)),
        )
        self.assertNotIn("SH004", codes(animation))

    def test_path_geometry_is_never_claimed_to_be_covered(self):
        """An arbitrary path has no cheap bounds, so it is left alone."""
        animation = _with_groups(
            _group("Plate", _ellipse(0, 0, 80, 80)),
            {"ty": "gr", "nm": "Squiggle", "it": [
                {"ty": "sh", "ks": {"a": 0, "k": {"c": False, "v": [[0, 0]],
                                                  "i": [[0, 0]], "o": [[0, 0]]}}},
                {"ty": "fl", "c": {"a": 0, "k": [0, 0, 0, 1]},
                 "o": {"a": 0, "k": 100}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0},
                 "o": {"a": 0, "k": 100}},
            ]},
        )
        self.assertNotIn("SH004", codes(animation))

    def test_the_shipped_panda_is_ordered_correctly(self):
        """Regression pin for the file this check was written from."""
        data = json.loads((REPO / "examples" / "panda-loader.json").read_text())
        found = [f for f in Linter(data).run() if f.code == "SH004"]
        self.assertEqual(found, [], [f.message for f in found])



if __name__ == "__main__":
    unittest.main()
