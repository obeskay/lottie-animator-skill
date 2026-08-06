#!/usr/bin/env python3
"""Convert an SVG into a Lottie composition of shape layers.

Hand-writing Lottie vertex tangents is where SVG-to-motion work goes wrong:
the arithmetic is mechanical, unforgiving, and invisible until it renders.
This does that part deterministically, so the animation work can start from a
composition that is already correct.

    python3 scripts/svg2lottie.py icon.svg -o icon.json
    python3 scripts/svg2lottie.py icon.svg --size 512 --fps 60 --frames 90

Each drawable element becomes its own named layer, anchored at its own centre,
so scale and rotation pivot where a designer expects. The result is a static
composition; add keyframes to it afterwards.

Dependency-free. Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from svgpath import PathError, bounds, parse_path, segments_to_lottie

SVG_NS = "http://www.w3.org/2000/svg"
LOTTIE_VERSION = "5.12.1"

# The subset of named colours that actually shows up in icon sets.
NAMED_COLORS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0),
    "orange": (255, 165, 0), "purple": (128, 0, 128), "gray": (128, 128, 128),
    "grey": (128, 128, 128), "silver": (192, 192, 192), "navy": (0, 0, 128),
    "teal": (0, 128, 128), "olive": (128, 128, 0), "lime": (0, 255, 0),
    "aqua": (0, 255, 255), "cyan": (0, 255, 255), "magenta": (255, 0, 255),
    "fuchsia": (255, 0, 255), "maroon": (128, 0, 0), "transparent": None,
}

INHERITED = (
    "fill", "stroke", "stroke-width", "opacity", "fill-opacity",
    "stroke-opacity", "stroke-linecap", "stroke-linejoin", "fill-rule",
)

LINE_CAP = {"butt": 1, "round": 2, "square": 3}
LINE_JOIN = {"miter": 1, "round": 2, "bevel": 3}


class ConversionError(Exception):
    pass


class Matrix:
    """A 2D affine transform: [a c e; b d f]."""

    __slots__ = ("a", "b", "c", "d", "e", "f")

    def __init__(self, a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0):
        self.a, self.b, self.c, self.d, self.e, self.f = a, b, c, d, e, f

    def multiply(self, other):
        return Matrix(
            self.a * other.a + self.c * other.b,
            self.b * other.a + self.d * other.b,
            self.a * other.c + self.c * other.d,
            self.b * other.c + self.d * other.d,
            self.a * other.e + self.c * other.f + self.e,
            self.b * other.e + self.d * other.f + self.f,
        )

    def apply(self, point):
        x, y = point
        return (self.a * x + self.c * y + self.e, self.b * x + self.d * y + self.f)

    def scale_factor(self):
        """Average scale, used to keep stroke widths visually correct."""
        return math.sqrt(abs(self.a * self.d - self.b * self.c)) or 1.0


def parse_transform(text):
    matrix = Matrix()
    if not text:
        return matrix
    for name, raw in re.findall(r"(\w+)\s*\(([^)]*)\)", text):
        values = [float(v) for v in re.findall(r"[-+]?[\d.]+(?:[eE][-+]?\d+)?", raw)]
        if name == "translate":
            matrix = matrix.multiply(Matrix(e=values[0], f=values[1] if len(values) > 1 else 0))
        elif name == "scale":
            sx = values[0]
            sy = values[1] if len(values) > 1 else sx
            matrix = matrix.multiply(Matrix(a=sx, d=sy))
        elif name == "rotate":
            angle = math.radians(values[0])
            cos, sin = math.cos(angle), math.sin(angle)
            rotation = Matrix(a=cos, b=sin, c=-sin, d=cos)
            if len(values) >= 3:
                cx, cy = values[1], values[2]
                rotation = Matrix(e=cx, f=cy).multiply(rotation).multiply(Matrix(e=-cx, f=-cy))
            matrix = matrix.multiply(rotation)
        elif name == "matrix" and len(values) >= 6:
            matrix = matrix.multiply(Matrix(*values[:6]))
        elif name == "skewX":
            matrix = matrix.multiply(Matrix(c=math.tan(math.radians(values[0]))))
        elif name == "skewY":
            matrix = matrix.multiply(Matrix(b=math.tan(math.radians(values[0]))))
    return matrix


def parse_color(value, current_color=None):
    """Return an (r, g, b) triple in 0..1, or None for no paint."""
    if not value:
        return None
    value = value.strip().lower()
    if value in ("none", "transparent"):
        return None
    if value.startswith("url("):
        raise ConversionError("gradient and pattern fills are not supported")
    if value == "currentcolor":
        # Icon sets paint with currentColor and inherit the surrounding text
        # colour. Lottie has no such context, so it has to be chosen here.
        return current_color if current_color is not None else (0.0, 0.0, 0.0)
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        if len(digits) == 8:
            digits = digits[:6]
        if len(digits) != 6:
            raise ConversionError("cannot read colour %r" % value)
        try:
            rgb = tuple(int(digits[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            raise ConversionError("cannot read colour %r" % value)
        return tuple(channel / 255.0 for channel in rgb)
    match = re.match(r"rgba?\(([^)]+)\)", value)
    if match:
        parts = [p.strip() for p in match.group(1).replace("/", ",").split(",")]
        channels = []
        for part in parts[:3]:
            if part.endswith("%"):
                channels.append(float(part[:-1]) * 255.0 / 100.0)
            else:
                channels.append(float(part))
        return tuple(min(255.0, max(0.0, c)) / 255.0 for c in channels)
    if value in NAMED_COLORS:
        rgb = NAMED_COLORS[value]
        return None if rgb is None else tuple(c / 255.0 for c in rgb)
    raise ConversionError("unknown colour %r" % value)


def local_name(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def collect_gradients(root):
    """Index every gradient definition by id, resolving xlink:href chains."""
    gradients = {}
    for element in root.iter():
        tag = local_name(element.tag)
        if tag not in ("linearGradient", "radialGradient"):
            continue
        gradient_id = element.get("id")
        if not gradient_id:
            continue
        stops = []
        for child in element:
            if local_name(child.tag) != "stop":
                continue
            style = {}
            inline = child.get("style") or ""
            for declaration in inline.split(";"):
                if ":" in declaration:
                    key, _, value = declaration.partition(":")
                    style[key.strip()] = value.strip()
            color = child.get("stop-color") or style.get("stop-color") or "black"
            opacity = child.get("stop-opacity") or style.get("stop-opacity") or "1"
            offset = child.get("offset", "0")
            offset = float(offset[:-1]) / 100.0 if offset.strip().endswith("%") else float(offset)
            stops.append({
                "offset": max(0.0, min(1.0, offset)),
                "color": parse_color(color) or (0.0, 0.0, 0.0),
                "opacity": number(opacity, 1.0),
            })
        gradients[gradient_id] = {
            "type": "radial" if tag == "radialGradient" else "linear",
            "units": element.get("gradientUnits", "objectBoundingBox"),
            "transform": element.get("gradientTransform"),
            "stops": stops,
            "coords": {key: element.get(key) for key in ("x1", "y1", "x2", "y2", "cx", "cy", "r", "fx", "fy")},
            "href": element.get("{http://www.w3.org/1999/xlink}href") or element.get("href"),
        }

    # A gradient may inherit its stops from another via href.
    for gradient in gradients.values():
        seen = set()
        current = gradient
        while not current["stops"] and current.get("href"):
            reference = current["href"].lstrip("#")
            if reference in seen or reference not in gradients:
                break
            seen.add(reference)
            current = gradients[reference]
            gradient["stops"] = current["stops"]
    return gradients


def _gradient_length(value, span, default):
    if value is None:
        return default
    text = str(value).strip()
    if text.endswith("%"):
        return float(text[:-1]) / 100.0 * span
    return float(text)


def gradient_endpoints(gradient, box, matrix):
    """Start and end points for the gradient, in composition coordinates."""
    min_x, min_y, max_x, max_y = box
    width = max_x - min_x or 1.0
    height = max_y - min_y or 1.0
    coords = gradient["coords"]
    object_space = gradient["units"] != "userSpaceOnUse"

    if gradient["type"] == "linear":
        if object_space:
            # Percentages and 0..1 fractions both map across the shape's box.
            x1 = min_x + _fraction(coords.get("x1"), 0.0) * width
            y1 = min_y + _fraction(coords.get("y1"), 0.0) * height
            x2 = min_x + _fraction(coords.get("x2"), 1.0) * width
            y2 = min_y + _fraction(coords.get("y2"), 0.0) * height
            return (x1, y1), (x2, y2)
        start = matrix.apply((number(coords.get("x1"), 0.0), number(coords.get("y1"), 0.0)))
        end = matrix.apply((number(coords.get("x2"), 0.0), number(coords.get("y2"), 0.0)))
        return start, end

    if object_space:
        cx = min_x + _fraction(coords.get("cx"), 0.5) * width
        cy = min_y + _fraction(coords.get("cy"), 0.5) * height
        radius = _fraction(coords.get("r"), 0.5) * max(width, height)
        return (cx, cy), (cx + radius, cy)
    center = matrix.apply((number(coords.get("cx"), 0.0), number(coords.get("cy"), 0.0)))
    radius = number(coords.get("r"), 0.0) * matrix.scale_factor()
    return center, (center[0] + radius, center[1])


def _is_fraction(value):
    return value is not None and not str(value).strip().endswith("%")


def _fraction(value, default):
    """Read a gradient coordinate as a 0..1 fraction of the shape's box."""
    if value is None:
        return default
    text = str(value).strip()
    if text.endswith("%"):
        return float(text[:-1]) / 100.0
    try:
        return float(text)
    except ValueError:
        return default


def gradient_item(gradient, box, matrix, opacity):
    stops = gradient["stops"]
    if not stops:
        raise ConversionError("gradient has no colour stops")
    ordered = sorted(stops, key=lambda s: s["offset"])
    colors = []
    for stop in ordered:
        colors.extend([round(stop["offset"], 4)] + [round(c, 4) for c in stop["color"]])
    alphas = []
    for stop in ordered:
        alphas.extend([round(stop["offset"], 4), round(stop["opacity"], 4)])

    start, end = gradient_endpoints(gradient, box, matrix)
    return {
        "ty": "gf", "nm": "Gradient Fill",
        "t": 2 if gradient["type"] == "radial" else 1,
        "s": static([round(start[0], 3), round(start[1], 3)]),
        "e": static([round(end[0], 3), round(end[1], 3)]),
        "g": {"p": len(ordered), "k": static(colors + alphas)},
        "o": static(round(opacity * 100, 2)),
        "r": 1,
    }


def style_of(element, inherited):
    """Presentation attributes merged with inline style, child wins."""
    style = dict(inherited)
    for key in INHERITED:
        value = element.get(key)
        if value is not None:
            style[key] = value
    inline = element.get("style")
    if inline:
        for declaration in inline.split(";"):
            if ":" in declaration:
                key, _, value = declaration.partition(":")
                key = key.strip()
                if key in INHERITED:
                    style[key] = value.strip()
    return style


def number(value, default=0.0):
    if value is None:
        return default
    try:
        return float(re.sub(r"(px|pt|mm|cm|in)$", "", str(value).strip()))
    except ValueError:
        return default


def viewbox_matrix(root, target_width, target_height):
    """Map the SVG user space onto the requested canvas."""
    viewbox = root.get("viewBox")
    if viewbox:
        parts = [float(v) for v in re.split(r"[\s,]+", viewbox.strip()) if v]
        if len(parts) != 4:
            raise ConversionError("viewBox must have four numbers")
        min_x, min_y, width, height = parts
    else:
        width = number(root.get("width"), 0) or target_width
        height = number(root.get("height"), 0) or target_height
        min_x = min_y = 0.0
    if width <= 0 or height <= 0:
        raise ConversionError("the SVG has no usable dimensions")

    # preserveAspectRatio defaults to meet, so use one uniform scale and centre.
    scale = min(target_width / width, target_height / height)
    offset_x = (target_width - width * scale) / 2.0
    offset_y = (target_height - height * scale) / 2.0
    return Matrix(a=scale, d=scale, e=offset_x - min_x * scale, f=offset_y - min_y * scale), (width, height)


# -- geometry to subpaths --------------------------------------------------
def rect_subpaths(element):
    x, y = number(element.get("x")), number(element.get("y"))
    width, height = number(element.get("width")), number(element.get("height"))
    if width <= 0 or height <= 0:
        return []
    rx = number(element.get("rx"), -1)
    ry = number(element.get("ry"), -1)
    if rx < 0 and ry < 0:
        rx = ry = 0.0
    elif rx < 0:
        rx = ry
    elif ry < 0:
        ry = rx
    rx = min(rx, width / 2.0)
    ry = min(ry, height / 2.0)

    if rx == 0 and ry == 0:
        data = "M%g,%g H%g V%g H%g Z" % (x, y, x + width, y + height, x)
    else:
        data = (
            "M%g,%g H%g A%g,%g 0 0 1 %g,%g V%g A%g,%g 0 0 1 %g,%g "
            "H%g A%g,%g 0 0 1 %g,%g V%g A%g,%g 0 0 1 %g,%g Z"
            % (
                x + rx, y, x + width - rx,
                rx, ry, x + width, y + ry,
                y + height - ry,
                rx, ry, x + width - rx, y + height,
                x + rx,
                rx, ry, x, y + height - ry,
                y + ry,
                rx, ry, x + rx, y,
            )
        )
    return parse_path(data)


def ellipse_subpaths(cx, cy, rx, ry):
    if rx <= 0 or ry <= 0:
        return []
    data = (
        "M%g,%g A%g,%g 0 1 0 %g,%g A%g,%g 0 1 0 %g,%g Z"
        % (cx - rx, cy, rx, ry, cx + rx, cy, rx, ry, cx - rx, cy)
    )
    return parse_path(data)


def points_subpaths(element, close):
    raw = element.get("points", "")
    values = [float(v) for v in re.findall(r"[-+]?[\d.]+(?:[eE][-+]?\d+)?", raw)]
    if len(values) < 4:
        return []
    pairs = list(zip(values[0::2], values[1::2]))
    data = "M%g,%g " % pairs[0] + " ".join("L%g,%g" % p for p in pairs[1:])
    if close:
        data += " Z"
    return parse_path(data)


def element_subpaths(element):
    """Geometry for one drawable element, in its own user space."""
    tag = local_name(element.tag)
    if tag == "path":
        data = element.get("d")
        return parse_path(data) if data else []
    if tag == "rect":
        return rect_subpaths(element)
    if tag == "circle":
        r = number(element.get("r"))
        return ellipse_subpaths(number(element.get("cx")), number(element.get("cy")), r, r)
    if tag == "ellipse":
        return ellipse_subpaths(
            number(element.get("cx")), number(element.get("cy")),
            number(element.get("rx")), number(element.get("ry")),
        )
    if tag == "line":
        return parse_path(
            "M%g,%g L%g,%g"
            % (number(element.get("x1")), number(element.get("y1")),
               number(element.get("x2")), number(element.get("y2")))
        )
    if tag == "polygon":
        return points_subpaths(element, close=True)
    if tag == "polyline":
        return points_subpaths(element, close=False)
    return []


# -- Lottie assembly -------------------------------------------------------
def static(value):
    return {"a": 0, "k": value}


def fill_item(color, opacity):
    return {
        "ty": "fl", "nm": "Fill",
        "c": static([round(c, 4) for c in color] + [1]),
        "o": static(round(opacity * 100, 2)),
        "r": 1,
    }


def stroke_item(color, opacity, width, cap, join):
    return {
        "ty": "st", "nm": "Stroke",
        "c": static([round(c, 4) for c in color] + [1]),
        "o": static(round(opacity * 100, 2)),
        "w": static(round(width, 3)),
        "lc": LINE_CAP.get(cap, 2),
        "lj": LINE_JOIN.get(join, 2),
    }


def transform_item():
    # Identity. The pivot lives on the layer transform instead, which is the
    # one an animator actually keyframes.
    return {
        "ty": "tr",
        "p": static([0, 0]),
        "a": static([0, 0]),
        "s": static([100, 100]),
        "r": static(0),
        "o": static(100),
        "sk": static(0),
        "sa": static(0),
    }


def resolve_paint(value, gradients, name, role, warnings, current_color=None):
    """Return an (r, g, b) triple, a gradient definition, or None."""
    if value is None:
        return None
    text = str(value).strip()
    match = re.match(r"url\(\s*#([^)\s]+)\s*\)", text)
    if match:
        gradient = gradients.get(match.group(1))
        if gradient and gradient["stops"]:
            return gradient
        warnings.append(
            "%s: %s references gradient %r, which has no stops; painting nothing"
            % (name, role, match.group(1))
        )
        return None
    try:
        return parse_color(text, current_color)
    except ConversionError as error:
        warnings.append("%s: %s (%s)" % (name, error, role))
        return None


def build_layer(index, name, subpaths, style, matrix, frames, gradients=None,
                warnings=None, current_color=None):
    """One SVG element becomes one shape layer anchored at its own centre."""
    gradients = gradients or {}
    warnings = warnings if warnings is not None else []
    box = bounds(subpaths, matrix.apply)
    if box is None:
        return None
    center = ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)

    shapes = []
    for subpath in subpaths:
        shape = segments_to_lottie(subpath, matrix.apply)
        if shape:
            shapes.append({"ty": "sh", "nm": "Path", "ks": static(shape)})
    if not shapes:
        return None

    fill_paint = resolve_paint(
        style.get("fill", "black"), gradients, name, "fill", warnings, current_color)
    stroke_paint = resolve_paint(
        style.get("stroke"), gradients, name, "stroke", warnings, current_color)
    fill = fill_paint if not isinstance(fill_paint, dict) else None
    stroke = stroke_paint if not isinstance(stroke_paint, dict) else None
    element_opacity = number(style.get("opacity"), 1.0)
    fill_opacity = number(style.get("fill-opacity"), 1.0)
    stroke_opacity = number(style.get("stroke-opacity"), 1.0)
    stroke_width = number(style.get("stroke-width"), 1.0) * matrix.scale_factor()

    paints = []
    if stroke is not None and stroke_width > 0:
        paints.append(
            stroke_item(stroke, stroke_opacity, stroke_width,
                        style.get("stroke-linecap", "round"),
                        style.get("stroke-linejoin", "round"))
        )
    if isinstance(fill_paint, dict):
        paints.append(gradient_item(fill_paint, box, matrix, fill_opacity))
    elif fill is not None:
        paints.append(fill_item(fill, fill_opacity))
    if not paints:
        # Geometry with no paint renders nothing; make that explicit upstream.
        return None

    group = {
        "ty": "gr", "nm": name,
        # Stroke before fill so the fill sits on top, matching SVG paint order.
        "it": shapes + paints + [transform_item()],
    }

    # Anchor and position both sit at the element's centre: the art stays put,
    # and scale/rotation pivot where a designer expects them to.
    pivot = [round(center[0], 3), round(center[1], 3), 0]
    return {
        "ddd": 0,
        "ind": index,
        "ty": 4,
        "nm": name,
        "sr": 1,
        "ks": {
            "o": static(round(element_opacity * 100, 2)),
            "r": static(0),
            "p": static(list(pivot)),
            "a": static(list(pivot)),
            "s": static([100, 100, 100]),
        },
        "ao": 0,
        "shapes": [group],
        "ip": 0,
        "op": frames,
        "st": 0,
        "bm": 0,
    }


def walk(element, inherited_style, inherited_matrix, out, warnings):
    for child in element:
        tag = local_name(child.tag)
        if tag in ("defs", "title", "desc", "metadata", "style", "clipPath", "mask"):
            if tag in ("clipPath", "mask"):
                warnings.append("%s is ignored; flatten it in the source SVG" % tag)
            elif tag == "style":
                warnings.append("<style> blocks are ignored; use presentation attributes")
            continue
        if tag == "use":
            warnings.append("<use> is ignored; inline the referenced shape")
            continue
        if tag == "text":
            warnings.append("<text> is ignored; convert type to outlines first")
            continue

        style = style_of(child, inherited_style)
        matrix = inherited_matrix.multiply(parse_transform(child.get("transform")))

        if tag in ("g", "svg", "a", "switch"):
            walk(child, style, matrix, out, warnings)
            continue

        try:
            subpaths = element_subpaths(child)
        except (PathError, ConversionError) as error:
            warnings.append("skipped <%s>: %s" % (tag, error))
            continue
        if not subpaths:
            continue
        out.append((child, tag, subpaths, style, matrix))


def convert(svg_text, size=None, fps=60, frames=60, name=None, current_color=None):
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as error:
        raise ConversionError("the file is not valid XML: %s" % error)
    if local_name(root.tag) != "svg":
        raise ConversionError("the root element is <%s>, not <svg>" % local_name(root.tag))

    intrinsic_width = number(root.get("width"), 0)
    intrinsic_height = number(root.get("height"), 0)
    if size:
        target_width = target_height = float(size)
    elif intrinsic_width > 0 and intrinsic_height > 0:
        target_width, target_height = intrinsic_width, intrinsic_height
    else:
        viewbox = root.get("viewBox")
        if viewbox:
            parts = [float(v) for v in re.split(r"[\s,]+", viewbox.strip()) if v]
            target_width, target_height = parts[2], parts[3]
        else:
            target_width = target_height = 512.0

    matrix, _ = viewbox_matrix(root, target_width, target_height)
    warnings = []
    collected = []
    gradients = collect_gradients(root)
    # Icon sets put fill/stroke on the <svg> element itself; children inherit it.
    walk(root, style_of(root, {}), matrix, collected, warnings)
    if not collected:
        raise ConversionError("no drawable elements found")

    layers = []
    # Lottie paints the first layer on top; SVG paints the last element on top.
    for order, (element, tag, subpaths, style, element_matrix) in enumerate(reversed(collected)):
        label = element.get("id") or element.get("class") or "%s %d" % (tag, len(collected) - order)
        layer = build_layer(
            order + 1, label, subpaths, style, element_matrix, frames,
            gradients=gradients, warnings=warnings, current_color=current_color,
        )
        if layer is None:
            warnings.append("skipped <%s> %r: it has no fill or stroke" % (tag, label))
            continue
        layers.append(layer)
    if not layers:
        raise ConversionError("every element was skipped; nothing to render")

    return {
        "v": LOTTIE_VERSION,
        "fr": fps,
        "ip": 0,
        "op": frames,
        "w": int(round(target_width)),
        "h": int(round(target_height)),
        "nm": name or "Converted SVG",
        "ddd": 0,
        "assets": [],
        "layers": layers,
    }, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert an SVG into a Lottie composition of shape layers."
    )
    parser.add_argument("svg", help="source SVG file")
    parser.add_argument("-o", "--out", help="output path (default: alongside the SVG)")
    parser.add_argument("--size", type=float, help="square canvas size in px")
    parser.add_argument("--fps", type=float, default=60, help="frame rate (default 60)")
    parser.add_argument("--frames", type=float, default=60, help="duration in frames (default 60)")
    parser.add_argument("--name", help="composition name")
    parser.add_argument(
        "--current-color",
        help="colour to substitute for currentColor, e.g. '#a855f7' (default black)",
    )
    args = parser.parse_args(argv)

    source = Path(args.svg)
    try:
        svg_text = source.read_text(encoding="utf-8")
    except OSError as error:
        print("svg2lottie: cannot read %s: %s" % (source, error), file=sys.stderr)
        return 2

    try:
        animation, warnings = convert(
            svg_text, size=args.size, fps=args.fps, frames=args.frames,
            name=args.name or source.stem.replace("-", " ").replace("_", " ").title(),
            current_color=parse_color(args.current_color) if args.current_color else None,
        )
    except ConversionError as error:
        print("svg2lottie: %s" % error, file=sys.stderr)
        return 1

    destination = Path(args.out) if args.out else source.with_suffix(".json")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(animation, indent=2) + "\n", encoding="utf-8")
    except OSError as error:
        print("svg2lottie: cannot write %s: %s" % (destination, error), file=sys.stderr)
        return 2

    for warning in warnings:
        print("  ! %s" % warning, file=sys.stderr)
    print(
        "%s -> %s  (%d layers, %dx%d)"
        % (source, destination, len(animation["layers"]), animation["w"], animation["h"])
    )
    print("Next: lint it, then render it and look at the filmstrip before animating.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
