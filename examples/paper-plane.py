"""Paper plane: it glides in along a curve, turning with it, and leaves a trail.

Brief: sent, light and a little whimsical, editorial register. Hero is the
plane's position on one curved path: it cruises at a steady speed, then eases
into a level landing and holds. Auto-orient turns it to face along the curve,
and the dashed trail is the same curve revealed by a trim that keeps pace.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

WING = "M32 0 L-28 -18 L-15 3 Z"
KEEL = "M32 0 L-15 3 L-19 15 Z"
# One cubic from the lower left to a level landing. Level matters: lottie-web
# aims an auto-oriented layer from two float32 positions 0.05 frames apart,
# which an ease brought to rest makes equal, and then it faces 0 degrees.
FLIGHT = ((50, 178), (86, 98), (100, 85), (160, 85))
SPLIT, CRUISE, LAG, HOLD = 0.65, 32, 6, 30


def split(cubic, t):
    """de Casteljau: the same curve as two cubics that meet on one tangent."""
    mix = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)  # noqa: E731
    p0, p1, p2, p3 = cubic
    q0, q1, q2 = mix(p0, p1), mix(p1, p2), mix(p2, p3)
    r0, r1 = mix(q0, q1), mix(q1, q2)
    m = mix(r0, r1)
    return (p0, q0, r0, m), (m, r1, q2, p3)


def length(cubic, steps=64):
    p0, p1, p2, p3 = cubic
    at = lambda t: [(1 - t) ** 3 * p0[k] + 3 * (1 - t) ** 2 * t * p1[k]  # noqa: E731
                    + 3 * (1 - t) * t * t * p2[k] + t ** 3 * p3[k] for k in (0, 1)]
    points = [at(i / steps) for i in range(steps + 1)]
    return sum(math.dist(points[i], points[i + 1]) for i in range(steps))


def tangents(cubic):
    """A cubic's two handles, relative to the ends they leave: Lottie's to and ti."""
    p0, p1, p2, p3 = cubic
    return [p1[0] - p0[0], p1[1] - p0[1]], [p2[0] - p3[0], p2[1] - p3[1]]


def leave(t, cubic, ease):
    """A position keyframe that sets off along `cubic`."""
    out, back = tangents(cubic)
    return (t, list(cubic[0]), ease, {"to": out + [0], "ti": back + [0]})


def build(c):
    cruise, land = split(FLIGHT, SPLIT)
    near, far = length(cruise), length(land)
    # The landing leaves at the cruise's speed and eases to rest. An ease sets
    # off at y1/x1 times its average speed, so giving the landing half that much
    # more time per pixel than the cruise makes the hand-over seamless. `strike`
    # (a sine) starts at 1.6x and has no tail; `out` starts at 4.3x and creeps
    # for a second before it stops.
    (x1, y1), _ = EASE["strike"]
    stop = CRUISE + round(y1 / x1 * CRUISE * far / near)
    flight = track(leave(0, cruise, "linear"), leave(CRUISE, land, "strike"), (stop, list(FLIGHT[3])))
    reveal = track((0, 0, "linear"), (CRUISE, 100 * near / (near + far), "strike"), (stop, 100))

    # The trail is the flight as a path: the same handles, as a vertex's o and i.
    out, back = tangents(FLIGHT)
    curve = {"c": False, "v": [list(FLIGHT[0]), list(FLIGHT[3])], "o": [out, [0, 0]], "i": [[0, 0], back]}
    trail = layer(
        "Trail",
        group("Trail", path(curve), trim(0, delay(reveal, LAG)), stroke(c["muted"], 3, dash=(5, 8))),
    )
    # ao=1 is auto-orient: the layer's x axis follows the path's tangent. The
    # fold is the accent thinned over on_accent, so it stays opaque.
    plane = layer(
        "Plane",
        group("Wing", *svg(WING, 1.15), fill(c["accent"])),
        group("Keel", *svg(KEEL, 1.15), fill(c["accent"], o=55), fill(c["on_accent"])),
        p=flight, o=track((0, 0, "out"), (LAG, 100)), ao=1,
    )
    return comp("Paper Plane", 240, 240, [plane, trail], op=stop + LAG + HOLD,
                bg=c["bg"], about="A paper plane cruises in on a curve, turning with it, and leaves a dashed trail.")


if __name__ == "__main__":
    main(build, __file__, palette="paper")
