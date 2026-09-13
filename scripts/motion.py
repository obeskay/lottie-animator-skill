#!/usr/bin/env python3
"""Motion and art-direction tokens for hand-authored Lottie.

Import it from a generator script instead of typing handles and colours:

    import sys; sys.path.insert(0, "<skill>/scripts")
    from motion import track, static, rgba, squircle, PALETTE

    "s": track((0, [92, 92, 100], "out"), (24, [100, 100, 100]))

Every keyframe `track` emits except the last carries `o` and `i`, so the
KF012 freeze cannot happen. The curves are the house defaults: strong
ease-out, zero overshoot. `playful` exists for briefs that ask for bounce
and nothing else. See references/motion-taste.md for when to use which.

Dependency-free. Python 3.8+.
"""
from __future__ import annotations

# cubic-bezier(x1, y1, x2, y2) as ((x1, y1), (x2, y2)).
EASE = {
    "out":     ((0.23, 1.0), (0.32, 1.0)),     # entrances, feedback, anything arriving
    "in-out":  ((0.77, 0.0), (0.175, 1.0)),    # on-screen travel, morphs, loops
    "glide":   ((0.32, 0.72), (0.0, 1.0)),     # large surfaces: sheets, cards, hero plates
    "in":      ((0.55, 0.0), (1.0, 0.45)),     # exits only, and keep them short
    "linear":  ((0.333, 0.333), (0.667, 0.667)),  # spinners, progress, constant drift
    "playful": ((0.34, 1.56), (0.64, 1.0)),    # overshoot; only when the brief asks for it
}

# Warm, low-chroma. One accent per composition; ink is for contour inside a mass
# of colour, never alone against a background of similar value.
PALETTE = {
    "paper": "#F3EEE6",
    "sand":  "#E4D9C6",
    "ink":   "#1E1B18",
    "stone": "#8A8178",
    "clay":  "#C8522B",
    "sage":  "#6F8163",
    "night": "#171513",
}


def static(value):
    return {"a": 0, "k": value}


def handles(name):
    (x1, y1), (x2, y2) = EASE[name]
    return {"o": {"x": [x1], "y": [y1]}, "i": {"x": [x2], "y": [y2]}}


def track(*frames):
    """(t, value, ease) tuples -> an animated property.

    The ease on a frame shapes the move *leaving* it; the last frame's is unused
    and may be omitted. `"hold"` snaps to the next value.
    """
    if len(frames) < 2:
        raise ValueError("a track needs at least two frames")
    keys = []
    for index, frame in enumerate(frames):
        t, value = frame[0], frame[1]
        ease = frame[2] if len(frame) > 2 else "out"
        key = {"t": t, "s": value if isinstance(value, list) else [value]}
        if index < len(frames) - 1:
            if ease == "hold":
                key["h"] = 1
            else:
                key.update(handles(ease))
        keys.append(key)
    return {"a": 1, "k": keys}


def rgba(hex_color, alpha=1.0):
    """'#C8522B' -> [0.784, 0.322, 0.169, 1.0]"""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError("expected #RRGGBB, got %r" % hex_color)
    return [round(int(h[i:i + 2], 16) / 255.0, 4) for i in (0, 2, 4)] + [alpha]


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


if __name__ == "__main__":
    t = track((0, 0, "out"), (10, 100))
    assert t["k"][0]["o"] == {"x": [0.23], "y": [1.0]} and "o" not in t["k"][1], t
    assert track((0, 1, "hold"), (5, 2))["k"][0]["h"] == 1
    assert rgba("#C8522B")[:3] == [0.7843, 0.3216, 0.1686]
    shape = squircle(100, 60, 10)
    assert len(shape["v"]) == 8 and shape["v"][0] == [26.57, -30.0], shape["v"]
    # every corner handle points at its corner
    assert shape["o"][0] == [23.43, 0.0] and shape["i"][1] == [0.0, -23.43], (shape["o"][0], shape["i"][1])
    print("self-test OK")
