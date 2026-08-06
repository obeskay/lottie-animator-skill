"""Tests for the SVG to Lottie converter.

The path arithmetic is the part nobody can eyeball, so it is pinned here:
geometry is checked against coordinates computed by hand, not against a
previous run of the same code.
"""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from svg2lottie import (  # noqa: E402
    ConversionError, Matrix, convert, parse_color, parse_transform,
)
from svgpath import bounds, parse_path, segments_to_lottie  # noqa: E402


class PathParsingTest(unittest.TestCase):
    def test_absolute_and_relative_lines_agree(self):
        absolute = parse_path("M10,10 L20,10 L20,20 Z")
        relative = parse_path("m10,10 l10,0 l0,10 z")
        self.assertEqual(bounds(absolute), bounds(relative))

    def test_horizontal_and_vertical(self):
        subpaths = parse_path("M0,0 H30 V40 Z")
        self.assertEqual(bounds(subpaths), (0.0, 0.0, 30.0, 40.0))

    def test_close_flag(self):
        self.assertTrue(parse_path("M0,0 L10,0 L10,10 Z")[0]["closed"])
        self.assertFalse(parse_path("M0,0 L10,0 L10,10")[0]["closed"])

    def test_quadratic_becomes_cubic(self):
        segments = parse_path("M0,0 Q10,20 20,0")[0]["segments"]
        self.assertEqual(len(segments), 1)
        _, c1, c2, end = segments[0]
        # Control points sit two thirds of the way toward the quadratic control.
        self.assertAlmostEqual(c1[0], 20.0 / 3.0)
        self.assertAlmostEqual(c1[1], 40.0 / 3.0)
        self.assertAlmostEqual(end[0], 20.0)

    def test_smooth_cubic_reflects_previous_control(self):
        segments = parse_path("M0,0 C0,10 10,10 10,0 S20,-10 20,0")[0]["segments"]
        self.assertEqual(len(segments), 2)
        # The reflection of (10,10) about (10,0) is (10,-10).
        self.assertAlmostEqual(segments[1][1][0], 10.0)
        self.assertAlmostEqual(segments[1][1][1], -10.0)

    def test_smooth_quadratic_without_previous_curve_is_a_line(self):
        segments = parse_path("M0,0 T10,0")[0]["segments"]
        self.assertEqual(len(segments), 1)

    def test_multiple_subpaths(self):
        subpaths = parse_path("M0,0 L10,0 Z M20,20 L30,20 Z")
        self.assertEqual(len(subpaths), 2)

    def test_implicit_lineto_after_moveto(self):
        subpaths = parse_path("M0,0 10,0 10,10")
        self.assertEqual(len(subpaths), 1)
        self.assertEqual(bounds(subpaths), (0.0, 0.0, 10.0, 10.0))

    def test_scientific_notation(self):
        subpaths = parse_path("M0,0 L1e2,0")
        self.assertEqual(bounds(subpaths)[2], 100.0)

    def test_bad_data_raises(self):
        from svgpath import PathError
        with self.assertRaises(PathError):
            parse_path("M0,0 X10,10")


class ArcTest(unittest.TestCase):
    def test_semicircle_arc_spans_the_diameter(self):
        subpaths = parse_path("M0,0 A50,50 0 0 1 100,0")
        min_x, min_y, max_x, max_y = bounds(subpaths)
        self.assertAlmostEqual(min_x, 0.0, places=3)
        self.assertAlmostEqual(max_x, 100.0, places=3)
        # Sweep 1 sweeps toward increasing angle, which puts this arc above the
        # baseline. Verified against Chrome's own rendering of the same path.
        self.assertLess(min_y, -40.0)
        self.assertAlmostEqual(max_y, 0.0, places=3)

    def test_full_circle_from_two_arcs(self):
        subpaths = parse_path("M0,50 A50,50 0 1 0 100,50 A50,50 0 1 0 0,50 Z")
        min_x, min_y, max_x, max_y = bounds(subpaths)
        self.assertAlmostEqual(min_x, 0.0, places=1)
        self.assertAlmostEqual(max_x, 100.0, places=1)
        self.assertAlmostEqual(max_y - min_y, 100.0, delta=1.0)

    def test_zero_radius_arc_degrades_to_a_line(self):
        segments = parse_path("M0,0 A0,0 0 0 1 10,10")[0]["segments"]
        self.assertEqual(len(segments), 1)

    def test_oversized_radii_are_scaled_up(self):
        # Radii too small to reach the endpoint must be grown, not rejected.
        subpaths = parse_path("M0,0 A1,1 0 0 1 100,0")
        self.assertAlmostEqual(bounds(subpaths)[2], 100.0, places=3)


class LottieShapeTest(unittest.TestCase):
    def test_tangents_are_relative_to_their_vertex(self):
        shape = segments_to_lottie(parse_path("M0,0 C10,0 20,10 20,20")[0])
        self.assertEqual(shape["v"][0], [0, 0])
        self.assertEqual(shape["o"][0], [10, 0])       # 10,0 minus 0,0
        self.assertEqual(shape["v"][1], [20, 20])
        self.assertEqual(shape["i"][1], [0, -10])      # 20,10 minus 20,20

    def test_closed_path_drops_the_duplicated_start_vertex(self):
        shape = segments_to_lottie(parse_path("M0,0 L10,0 L10,10 L0,10 Z")[0])
        self.assertTrue(shape["c"])
        self.assertEqual(len(shape["v"]), 4)
        self.assertEqual(len(shape["i"]), 4)
        self.assertEqual(len(shape["o"]), 4)

    def test_open_path_keeps_every_vertex(self):
        shape = segments_to_lottie(parse_path("M0,0 L10,0 L10,10")[0])
        self.assertFalse(shape["c"])
        self.assertEqual(len(shape["v"]), 3)

    def test_transform_is_applied_to_vertices(self):
        matrix = Matrix(a=2, d=2, e=5, f=5)
        shape = segments_to_lottie(parse_path("M0,0 L10,0")[0], matrix.apply)
        self.assertEqual(shape["v"][0], [5, 5])
        self.assertEqual(shape["v"][1], [25, 5])


class TransformTest(unittest.TestCase):
    def test_translate(self):
        self.assertEqual(parse_transform("translate(5,7)").apply((0, 0)), (5.0, 7.0))

    def test_scale_with_one_argument_is_uniform(self):
        self.assertEqual(parse_transform("scale(3)").apply((2, 2)), (6.0, 6.0))

    def test_rotate_about_a_point(self):
        point = parse_transform("rotate(90,10,10)").apply((20, 10))
        self.assertAlmostEqual(point[0], 10.0)
        self.assertAlmostEqual(point[1], 20.0)

    def test_composition_applies_left_to_right(self):
        point = parse_transform("translate(10,0) scale(2)").apply((5, 0))
        self.assertEqual(point, (20.0, 0.0))

    def test_matrix(self):
        self.assertEqual(parse_transform("matrix(1,0,0,1,4,5)").apply((0, 0)), (4.0, 5.0))


class ColorTest(unittest.TestCase):
    def test_hex_forms(self):
        self.assertEqual(parse_color("#ffffff"), (1.0, 1.0, 1.0))
        self.assertEqual(parse_color("#fff"), (1.0, 1.0, 1.0))
        self.assertEqual(parse_color("#000000ff"), (0.0, 0.0, 0.0))

    def test_rgb_form(self):
        red = parse_color("rgb(255, 0, 0)")
        self.assertAlmostEqual(red[0], 1.0)
        self.assertAlmostEqual(red[1], 0.0)

    def test_named_and_none(self):
        self.assertEqual(parse_color("black"), (0.0, 0.0, 0.0))
        self.assertIsNone(parse_color("none"))

    def test_current_color_is_substitutable(self):
        self.assertEqual(parse_color("currentColor"), (0.0, 0.0, 0.0))
        self.assertEqual(parse_color("currentColor", (1.0, 0.0, 0.0)), (1.0, 0.0, 0.0))

    def test_unknown_colour_raises(self):
        with self.assertRaises(ConversionError):
            parse_color("chartreuse-ish")


class ConvertTest(unittest.TestCase):
    RECT = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<rect x="10" y="10" width="80" height="80" fill="#ff0000"/></svg>'
    )

    def test_produces_a_valid_composition(self):
        animation, warnings = convert(self.RECT)
        self.assertEqual(animation["w"], 100)
        self.assertEqual(len(animation["layers"]), 1)
        self.assertEqual(warnings, [])
        layer = animation["layers"][0]
        self.assertIn("ip", layer)
        self.assertIn("op", layer)
        self.assertTrue(layer["shapes"])

    def test_output_passes_the_linter(self):
        from lottie_lint import Linter
        animation, _ = convert(self.RECT)
        errors = [f for f in Linter(animation, allow_static=True).run() if f.severity == "error"]
        self.assertEqual(errors, [], [f.message for f in errors])

    def test_pivot_sits_at_the_element_centre(self):
        animation, _ = convert(self.RECT)
        anchor = animation["layers"][0]["ks"]["a"]["k"]
        self.assertAlmostEqual(anchor[0], 50.0, places=1)
        self.assertAlmostEqual(anchor[1], 50.0, places=1)
        # Position must match the anchor or the art shifts by -anchor.
        self.assertEqual(animation["layers"][0]["ks"]["p"]["k"], anchor)

    def test_root_presentation_attributes_are_inherited(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'fill="none" stroke="#00ff00" stroke-width="2">'
            '<path d="M2,2 L22,22"/></svg>'
        )
        animation, _ = convert(svg)
        items = animation["layers"][0]["shapes"][0]["it"]
        kinds = [item["ty"] for item in items]
        self.assertIn("st", kinds)
        self.assertNotIn("fl", kinds)

    def test_viewbox_is_scaled_to_the_requested_size(self):
        animation, _ = convert(self.RECT, size=200)
        self.assertEqual(animation["w"], 200)
        anchor = animation["layers"][0]["ks"]["a"]["k"]
        self.assertAlmostEqual(anchor[0], 100.0, places=1)

    def test_gradient_fill_is_converted(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>'
            '<linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="0%">'
            '<stop offset="0%" stop-color="#ff0000"/>'
            '<stop offset="100%" stop-color="#0000ff"/>'
            '</linearGradient></defs>'
            '<rect x="0" y="0" width="100" height="100" fill="url(#g)"/></svg>'
        )
        animation, _ = convert(svg)
        items = animation["layers"][0]["shapes"][0]["it"]
        gradient = next(item for item in items if item["ty"] == "gf")
        self.assertEqual(gradient["g"]["p"], 2)
        self.assertEqual(gradient["t"], 1)
        # Two colour stops: 4 numbers each, then 2 numbers each of alpha.
        self.assertEqual(len(gradient["g"]["k"]["k"]), 2 * 4 + 2 * 2)

    def test_paint_order_puts_fill_above_stroke(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            '<rect width="10" height="10" fill="#fff" stroke="#000" stroke-width="1"/></svg>'
        )
        animation, _ = convert(svg)
        kinds = [i["ty"] for i in animation["layers"][0]["shapes"][0]["it"]]
        self.assertLess(kinds.index("st"), kinds.index("fl"))

    def test_svg_paint_order_is_preserved_across_layers(self):
        """SVG paints later elements on top; Lottie paints earlier layers on top."""
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            '<rect id="under" width="10" height="10" fill="#f00"/>'
            '<rect id="over" width="5" height="5" fill="#00f"/></svg>'
        )
        animation, _ = convert(svg)
        self.assertEqual(animation["layers"][0]["nm"], "over")
        self.assertEqual(animation["layers"][1]["nm"], "under")

    def test_unpaintable_element_is_skipped_with_a_warning(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            '<rect width="10" height="10" fill="#f00"/>'
            '<rect width="4" height="4" fill="none"/></svg>'
        )
        animation, warnings = convert(svg)
        self.assertEqual(len(animation["layers"]), 1)
        self.assertTrue(any("no fill or stroke" in w for w in warnings))

    def test_text_is_reported_rather_than_dropped_silently(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            '<rect width="10" height="10" fill="#f00"/>'
            '<text x="0" y="5">hi</text></svg>'
        )
        _, warnings = convert(svg)
        self.assertTrue(any("text" in w for w in warnings))

    def test_group_transforms_accumulate(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<g transform="translate(10,10)"><g transform="scale(2)">'
            '<rect width="10" height="10" fill="#f00"/></g></g></svg>'
        )
        animation, _ = convert(svg)
        anchor = animation["layers"][0]["ks"]["a"]["k"]
        # scale(2) then translate(10,10): centre 5,5 -> 10,10 -> 20,20
        self.assertAlmostEqual(anchor[0], 20.0, places=1)

    def test_empty_document_raises(self):
        with self.assertRaises(ConversionError):
            convert('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>')

    def test_non_svg_root_raises(self):
        with self.assertRaises(ConversionError):
            convert("<html></html>")

    def test_malformed_xml_raises(self):
        with self.assertRaises(ConversionError):
            convert("<svg><rect")


class ShippedSourcesTest(unittest.TestCase):
    def test_repository_svgs_convert_cleanly(self):
        from lottie_lint import Linter
        repo = Path(__file__).resolve().parents[1]
        for svg in sorted((repo / "examples").glob("*.svg")):
            with self.subTest(svg=svg.name):
                animation, _ = convert(svg.read_text(encoding="utf-8"))
                errors = [
                    f for f in Linter(animation, allow_static=True).run()
                    if f.severity == "error"
                ]
                self.assertEqual(errors, [], [f.message for f in errors])


if __name__ == "__main__":
    unittest.main()
