#!/usr/bin/env python3
"""Motion tokens, palettes and shape builders for hand-authored Lottie.

A generator imports this instead of typing handles, hex values or JSON:

    import sys; sys.path.insert(0, "<skill>/scripts")
    from motion import *

    def build(c):                                   # c is a palette: c["accent"]...
        dot = layer("Dot", group("Dot", ellipse(48), fill(c["accent"])),
                    p=(60, 60), s=track((0, [94, 94], "out"), (24, [100, 100])))
        return comp("Dot", 120, 120, [dot], op=60, bg=c["bg"])

    if __name__ == "__main__":
        main(build, __file__, palette="paper")      # --palette night -o out.json

Every keyframe `track` emits except the last carries `o` and `i`, so the KF012
freeze cannot happen, and every builder emits the properties whose absence
makes a player drop the layer. The curves are the house defaults: strong
ease-out, zero overshoot; `playful` exists for briefs that ask for bounce.
See references/motion-taste.md for when to use which, and examples/*.py for
twenty generators written this way.

Dependency-free. Python 3.8+.
"""
from __future__ import annotations

import json
from pathlib import Path

from svgpath import parse_path, segments_to_lottie

__all__ = [
    "EASE", "PALETTE", "PALETTES", "static", "handles", "track", "delay", "rgba",
    "squircle", "bezier", "comp", "layer", "null", "group", "ellipse", "rect",
    "star", "path", "svg", "fill", "stroke", "trim", "repeater", "round_corners",
    "paint", "dumps", "main",
]

# cubic-bezier(x1, y1, x2, y2) as ((x1, y1), (x2, y2)).
EASE = {
    # Moves between rests
    "out":      ((0.23, 1.0), (0.32, 1.0)),     # entrances, feedback, anything arriving
    "in-out":   ((0.77, 0.0), (0.175, 1.0)),    # on-screen travel and morphs, rest to rest
    "glide":    ((0.32, 0.72), (0.0, 1.0)),     # large surfaces: sheets, cards, hero plates
    "in":       ((0.55, 0.0), (1.0, 0.45)),     # exits only, and keep them short
    # Motion that never rests; in-out would hold at every turn and lurch between
    "linear":   ((0.333, 0.333), (0.667, 0.667)),  # constant rotation, marching offsets
    "swing":    ((0.37, 0.0), (0.63, 1.0)),     # sine: pendulums, oscillation, breathing
    "standard": ((0.4, 0.0), (0.2, 1.0)),       # a spinner's chasing arc, a level meter
    # Physics
    "strike":   ((0.61, 1.0), (0.88, 1.0)),     # the first swing after a blow, at full speed
    "fall":     ((1 / 3, 0.0), (2 / 3, 1 / 3)),   # gravity: exactly t^2, anything dropping
    "rise":     ((1 / 3, 2 / 3), (2 / 3, 1.0)),   # thrown upward, slowing to an apex
    "playful":  ((0.34, 1.56), (0.64, 1.0)),    # overshoot; only when the brief asks for it
}

# The original warm swatches, kept by name for generators written against them.
PALETTE = {
    "paper": "#F3EEE6",
    "sand":  "#E4D9C6",
    "ink":   "#1E1B18",
    "stone": "#8A8178",
    "clay":  "#C8522B",
    "sage":  "#6F8163",
    "night": "#171513",
}

# Palettes by role, so one generator renders in any of them (`--palette`).
#   bg        the ground the animation sits on; not painted, stored as meta.tc
#   surface   a quiet mass on the ground: cards, tracks, the unlit half of a toggle
#   ink       contour and glyphs, >= 7:1 on bg
#   muted     secondary lines, >= 3:1 on bg
#   accent    the one colour that carries meaning, >= 3:1 on bg
#   on_accent a glyph drawn on top of an accent mass, >= 3:1 on accent
#   support   a second hue for masses only (sun, confetti, a leaf); never a thin
#             line alone on the ground, where it can fall under 2:1
# tests/test_motion.py enforces the ratios, so a palette cannot ship illegible.
PALETTES = {
    "paper":  {"bg": "#F3EEE6", "surface": "#E4D9C6", "ink": "#1E1B18", "muted": "#8A8178",
               "accent": "#C8522B", "on_accent": "#F3EEE6", "support": "#6F8163"},
    "night":  {"bg": "#171513", "surface": "#2A2622", "ink": "#F3EEE6", "muted": "#8F867C",
               "accent": "#E0A458", "on_accent": "#171513", "support": "#7FA39A"},
    "dusk":   {"bg": "#121A26", "surface": "#1F2A3A", "ink": "#EDE6DA", "muted": "#7F8DA3",
               "accent": "#F0A04B", "on_accent": "#121A26", "support": "#6FA3C7"},
    "harbor": {"bg": "#EAF1F2", "surface": "#D2E1E4", "ink": "#10242C", "muted": "#5F7C87",
               "accent": "#1E6E86", "on_accent": "#F4F8F8", "support": "#E07A5F"},
    "citrus": {"bg": "#FBF5E6", "surface": "#F2E5C2", "ink": "#2A2211", "muted": "#8C7F5C",
               "accent": "#E4572E", "on_accent": "#FBF5E6", "support": "#E9A91B"},
    "berry":  {"bg": "#FBEFF1", "surface": "#F3DADF", "ink": "#2B1519", "muted": "#93717A",
               "accent": "#B8325A", "on_accent": "#FBEFF1", "support": "#F0A35E"},
    "forest": {"bg": "#EDF1EA", "surface": "#D7E0D0", "ink": "#17231A", "muted": "#6C7F68",
               "accent": "#2F6B4F", "on_accent": "#EDF1EA", "support": "#D9A441"},
    "mono":   {"bg": "#F4F4F2", "surface": "#E3E3DF", "ink": "#121212", "muted": "#85857F",
               "accent": "#E5484D", "on_accent": "#F4F4F2", "support": "#B5B5AF"},
    "sky":    {"bg": "#EDF3FA", "surface": "#D6E3F2", "ink": "#14202E", "muted": "#687D96",
               "accent": "#3569C9", "on_accent": "#F5F8FC", "support": "#F2B544"},
}

LOTTIE_VERSION = "5.12.1"


# -- properties and keyframes ------------------------------------------------

def static(value):
    return {"a": 0, "k": value}


def handles(name):
    (x1, y1), (x2, y2) = EASE[name]
    return {"o": {"x": [x1], "y": [y1]}, "i": {"x": [x2], "y": [y2]}}


def track(*frames):
    """(t, value, ease[, extra]) tuples -> an animated property.

    The ease on a frame shapes the move *leaving* it; the last frame's is unused
    and may be omitted. `"hold"` snaps to the next value. `extra` is merged into
    the keyframe, for spatial tangents on a curved path:
    `(0, [40, 200], "in-out", {"to": [60, -80], "ti": [-60, 0]})`.
    """
    if len(frames) < 2:
        raise ValueError("a track needs at least two frames")
    keys = []
    for index, frame in enumerate(frames):
        t, value = frame[0], frame[1]
        ease = frame[2] if len(frame) > 2 and frame[2] else "out"
        if isinstance(value, tuple):
            value = list(value)
        key = {"t": t, "s": value if isinstance(value, list) else [value]}
        if index < len(frames) - 1:
            if ease == "hold":
                key["h"] = 1
            else:
                key.update(handles(ease))
        if len(frame) > 3:
            key.update(frame[3])
        keys.append(key)
    return {"a": 1, "k": keys}


def delay(prop, frames):
    """The same track, `frames` later. Cascades are one track, delayed per sibling."""
    if not prop.get("a"):
        return prop
    return {"a": 1, "k": [dict(key, t=key["t"] + frames) for key in prop["k"]]}


def rgba(hex_color, alpha=1.0):
    """'#C8522B' -> [0.784, 0.322, 0.169, 1.0]"""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError("expected #RRGGBB, got %r" % hex_color)
    return [round(int(h[i:i + 2], 16) / 255.0, 4) for i in (0, 2, 4)] + [alpha]


def _prop(value):
    """A static value, or a property already built with track()."""
    if isinstance(value, dict) and "a" in value and "k" in value:
        return value
    return static(list(value) if isinstance(value, tuple) else value)


def _pair(value):
    return [value, value] if isinstance(value, (int, float)) else value


def _color(value):
    """'#RRGGBB', an [r, g, b, a] list, or a track of rgba() values."""
    if isinstance(value, str):
        return static(rgba(value))
    return _prop(value)


def _pad(prop, fill):
    """Layer transforms carry a third component, as After Effects exports them."""
    def grow(value):
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return list(value) + [fill]
        return value
    if prop.get("a"):
        return {"a": 1, "k": [dict(key, s=grow(key["s"])) for key in prop["k"]]}
    return static(grow(prop["k"]))


# -- geometry ----------------------------------------------------------------

def squircle(width, height, radius):
    """A continuous-curvature rounded rectangle as a Lottie path, centred on 0,0.

    A circular corner jumps from zero curvature on the edge to 1/r on the arc,
    which the eye reads as a pinch. Here each corner is one cubic whose handles
    both sit on the corner point, so curvature is zero where the curve meets the
    straight edge. The corner starts 2.34 radii from the corner point, which
    puts its midpoint where a circular corner of `radius` would be.
    """
    w2, h2 = width / 2.0, height / 2.0
    p = min(radius * 2.343, w2, h2)
    corners = [(w2, -h2), (w2, h2), (-w2, h2), (-w2, -h2)]  # clockwise from top-right
    vertices, ins, outs = [], [], []
    for cx, cy in corners:
        sx = -1 if cx > 0 else 1   # direction back along the horizontal edge
        sy = -1 if cy > 0 else 1   # direction back along the vertical edge
        clockwise_top_or_bottom_first = (cx > 0) == (cy < 0)
        a = (cx + sx * p, cy) if clockwise_top_or_bottom_first else (cx, cy + sy * p)
        b = (cx, cy + sy * p) if clockwise_top_or_bottom_first else (cx + sx * p, cy)
        vertices += [list(a), list(b)]
        ins += [[0, 0], [round(cx - b[0], 3), round(cy - b[1], 3)]]
        outs += [[round(cx - a[0], 3), round(cy - a[1], 3)], [0, 0]]
    return {"c": True, "v": [[round(x, 3), round(y, 3)] for x, y in vertices], "i": ins, "o": outs}


def bezier(d, scale=1.0, center=(0, 0)):
    """SVG path data -> Lottie bezier dicts, one per subpath.

    Draw on whatever grid is convenient (a 24-unit icon, a 100-unit sketch);
    `center` moves to 0,0 and `scale` sizes it, so the shape pivots on its own
    middle. Morph between two of these with track() when their vertex counts
    match.
    """
    cx, cy = center
    move = lambda point: ((point[0] - cx) * scale, (point[1] - cy) * scale)  # noqa: E731
    shapes = [segments_to_lottie(sub, move) for sub in parse_path(d)]
    return [shape for shape in shapes if shape]


# -- shape items ---------------------------------------------------------------
# Inside a group, the first item paints on top; fills and strokes paint every
# path above them in the same group.

def ellipse(size, p=(0, 0)):
    return {"ty": "el", "nm": "Ellipse", "d": 1, "p": _prop(p), "s": _prop(_pair(size))}


def rect(size, p=(0, 0), r=0):
    """A rectangle with circular corners; prefer path(squircle(...)) for surfaces."""
    return {"ty": "rc", "nm": "Rect", "d": 1, "p": _prop(p), "s": _prop(_pair(size)), "r": _prop(r)}


def star(points, outer, inner=None, p=(0, 0), r=0, roundness=0):
    """A star, or a polygon when `inner` is None."""
    item = {"ty": "sr", "nm": "Star" if inner else "Polygon", "sy": 1 if inner else 2, "d": 1,
            "p": _prop(p), "r": _prop(r), "pt": _prop(points),
            "or": _prop(outer), "os": _prop(roundness)}
    if inner:
        item.update({"ir": _prop(inner), "is": _prop(roundness)})
    return item


def path(shape):
    """One path item from a bezier dict, squircle(), or a track of either."""
    return {"ty": "sh", "nm": "Path", "ks": _prop(shape)}


def svg(d, scale=1.0, center=(0, 0)):
    """Path items for every subpath in SVG path data. Spread them: group(*svg(...))."""
    return [path(shape) for shape in bezier(d, scale, center)]


def fill(color, o=100, evenodd=False):
    """`evenodd=True` punches holes where subpaths overlap: a pin's eye, a ring."""
    return {"ty": "fl", "nm": "Fill", "c": _color(color), "o": _prop(o), "r": 2 if evenodd else 1}


def stroke(color, width, o=100, cap="round", join="round", dash=None):
    """`dash=(length, gap)` or `(length, gap, offset)`; animate the offset to march."""
    caps = {"butt": 1, "round": 2, "square": 3}
    joins = {"miter": 1, "round": 2, "bevel": 3}
    item = {"ty": "st", "nm": "Stroke", "c": _color(color), "o": _prop(o), "w": _prop(width),
            "lc": caps[cap], "lj": joins[join], "ml": 4}
    if dash:
        length, gap = dash[0], dash[1]
        offset = dash[2] if len(dash) > 2 else 0
        item["d"] = [{"n": "d", "nm": "dash", "v": _prop(length)},
                     {"n": "g", "nm": "gap", "v": _prop(gap)},
                     {"n": "o", "nm": "offset", "v": _prop(offset)}]
    return item


def trim(start=0, end=100, offset=0):
    """Reveal part of every path above it. A round cap at ~0 length still paints a dot."""
    return {"ty": "tm", "nm": "Trim", "s": _prop(start), "e": _prop(end), "o": _prop(offset), "m": 1}


def repeater(copies, p=(0, 0), r=0, s=(100, 100), so=100, eo=100, offset=0):
    """Copies of everything above it, each moved by this transform from the last."""
    return {"ty": "rp", "nm": "Repeater", "c": _prop(copies), "o": _prop(offset), "m": 1,
            "tr": {"ty": "tr", "p": _prop(p), "a": static([0, 0]), "s": _prop(_pair(s)),
                   "r": _prop(r), "o": static(100), "so": _prop(so), "eo": _prop(eo)}}


def paint(item, color):
    """Recolour every fill and stroke under a layer, group or list, e.g. a layer
    converted from SVG: paint(parts["flame"], c["accent"]). Returns the item."""
    if isinstance(item, dict):
        if item.get("ty") in ("fl", "st"):
            item["c"] = _color(color)
        for value in list(item.values()):
            paint(value, color)
    elif isinstance(item, list):
        for value in item:
            paint(value, color)
    return item


def round_corners(radius):
    """Rounds every corner of the paths above it: a friendlier triangle or star."""
    return {"ty": "rd", "nm": "Round Corners", "r": _prop(radius)}


def group(nm, *items, p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100):
    """Geometry, then paint, then this transform. Loose geometry draws at zero size."""
    transform = {"ty": "tr", "p": _prop(p), "a": _prop(a), "s": _prop(_pair(s)),
                 "r": _prop(r), "o": _prop(o)}
    return {"ty": "gr", "nm": nm, "it": list(items) + [transform]}


# -- layers and the composition ------------------------------------------------

def _transform(p, a, s, r, o):
    return {"o": _prop(o), "r": _prop(r), "p": _pad(_prop(p), 0),
            "a": _pad(_prop(a), 0), "s": _pad(_prop(_pair(s)), 100)}


def layer(nm, *shapes, p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100, parent=None,
          ip=None, op=None, **extra):
    """A shape layer. `parent` is another layer's name; comp() resolves it.

    `extra` lands on the layer as-is: `td=1` makes it a matte for the layer below
    it, `tt=1` (alpha) or `tt=3` (luma) makes this layer use the one above.
    """
    item = {"ddd": 0, "ty": 4, "nm": nm, "sr": 1, "ks": _transform(p, a, s, r, o), "ao": 0,
            "shapes": list(shapes), "ip": ip, "op": op, "st": 0, "bm": 0}
    if parent:
        item["parent"] = parent
    item.update(extra)
    return item


def null(nm, p=(0, 0), a=(0, 0), s=(100, 100), r=0, parent=None):
    """An invisible layer to parent others to: a pivot, a rig bone, a shared drift."""
    item = {"ddd": 0, "ty": 3, "nm": nm, "sr": 1, "ks": _transform(p, a, s, r, 100), "ao": 0,
            "ip": None, "op": None, "st": 0, "bm": 0}
    if parent:
        item["parent"] = parent
    return item


def comp(nm, w, h, layers, op, fr=60, bg=None, about=None):
    """The document. The first layer paints on top.

    `bg` is the ground the animation was designed on. Lottie has no background,
    so it is stored as meta.tc, where the renderer and the GIF builder find it.
    """
    index = {}
    for number, item in enumerate(layers, 1):
        if item["nm"] in index:
            raise ValueError("two layers are named %r; parent= cannot tell them apart" % item["nm"])
        index[item["nm"]] = number
        item["ind"] = number
        item["ip"] = 0 if item["ip"] is None else item["ip"]
        item["op"] = op if item["op"] is None else item["op"]
    for item in layers:
        if isinstance(item.get("parent"), str):
            item["parent"] = index[item["parent"]]
    meta = {"g": "lottie-animator motion.py"}
    if bg:
        meta["tc"] = bg
    if about:
        meta["d"] = about
    return {"v": LOTTIE_VERSION, "fr": fr, "ip": 0, "op": op, "w": w, "h": h, "nm": nm,
            "ddd": 0, "assets": [], "meta": meta, "layers": layers}


def _tidy(value):
    if isinstance(value, float):
        value = round(value, 3)
        return int(value) if value.is_integer() else value
    if isinstance(value, list):
        return [_tidy(v) for v in value]
    if isinstance(value, dict):
        return {k: _tidy(v) for k, v in value.items()}
    return value


def dumps(doc):
    """Compact JSON, numbers rounded to 3 places: what ships to a player."""
    return json.dumps(_tidy(doc), separators=(",", ":"), ensure_ascii=False)


def main(build, source, palette="paper"):
    """The command line every example shares.

        python3 examples/heart-like.py                   rebuild examples/heart-like.json
        python3 examples/heart-like.py --palette night   write heart-like-night.json here
        python3 examples/heart-like.py -o out.json       choose the path
    """
    import argparse

    parser = argparse.ArgumentParser(description=(build.__doc__ or "").strip().split("\n")[0])
    parser.add_argument("--palette", default=palette, choices=sorted(PALETTES))
    parser.add_argument("-o", "--out", help="output path")
    args = parser.parse_args()
    own = Path(source).resolve().with_suffix(".json")
    if args.out:
        out = Path(args.out)
    elif args.palette == palette:
        out = own
    else:
        out = Path.cwd() / ("%s-%s.json" % (own.stem, args.palette))
    out.write_text(dumps(build(PALETTES[args.palette])) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    t = track((0, 0, "out"), (10, 100))
    assert t["k"][0]["o"] == {"x": [0.23], "y": [1.0]} and "o" not in t["k"][1], t
    assert track((0, 1, "hold"), (5, 2))["k"][0]["h"] == 1
    assert delay(t, 5)["k"][1]["t"] == 15 and t["k"][1]["t"] == 10
    assert rgba("#C8522B")[:3] == [0.7843, 0.3216, 0.1686]
    shape = squircle(100, 60, 10)
    assert len(shape["v"]) == 8 and shape["v"][0] == [26.57, -30.0], shape["v"]
    # every corner handle points at its corner
    assert shape["o"][0] == [23.43, 0.0] and shape["i"][1] == [0.0, -23.43], (shape["o"][0], shape["i"][1])
    assert bezier("M0 0 L10 0 L10 10 Z", center=(5, 5))[0]["v"][0] == [-5, -5]
    dot = layer("Dot", group("Dot", ellipse(10), fill("#C8522B")), p=(5, 5))
    doc = comp("Self Test", 10, 10, [dot, layer("Halo", parent="Dot")], op=10, bg="#F3EEE6")
    assert doc["layers"][1]["parent"] == 1 and doc["layers"][0]["ks"]["p"]["k"] == [5, 5, 0]
    assert json.loads(dumps(doc))["meta"]["tc"] == "#F3EEE6"
    print("self-test OK")
