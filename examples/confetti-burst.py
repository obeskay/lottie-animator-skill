"""Confetti: the badge gathers itself, pops, and throws a handful of confetti.

Brief: celebration, playful register (on request only), kept restrained. Hero
is the burst: fourteen pieces in three colours leave from behind the badge on
ballistic arcs, x slowing under drag while y rises and falls, spinning and
shrinking out long before the loop comes round. The badge's pop is the one
overshoot, 6%; the press before it is the anticipation.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

BURST = 12      # the press releases and the pieces leave
AIR = 40        # frames from a piece's apex to its exit

# Gravity: y decelerates to the apex and accelerates away from it, quadratically
# (the `rise` and `fall` tokens). Drag: x only ever slows down, on `rise` too.
WAVE = "M-7 2 C-5 -3 -2 -3 0 0 C2 3 5 3 7 -2"

# kind, colour, x travel, apex, exit height (px from the badge centre), spin, delay
PIECES = [
    ("rect", "accent", -96, -52, 70, 380, 0),
    ("dot", "support", -78, -88, 56, 0, 1),
    ("wave", "ink", -58, -104, 40, -160, 2),
    ("rect", "support", -40, -76, 74, -420, 1),
    ("dot", "accent", -22, -104, 46, 0, 3),
    ("rect", "accent", -70, -30, 84, 300, 2),
    ("wave", "accent", -6, -98, 60, 180, 0),
    ("rect", "support", 96, -60, 66, -380, 1),
    ("dot", "accent", 76, -94, 52, 0, 0),
    ("wave", "accent", 56, -100, 36, 200, 2),
    ("rect", "accent", 36, -84, 72, 440, 1),
    ("dot", "support", 18, -102, 50, 0, 2),
    ("rect", "ink", 64, -34, 86, -300, 3),
    ("dot", "ink", -50, -66, 78, 0, 3),
]


def paint(kind, colour):
    if kind == "rect":
        return [rect([6, 12], r=1.5), fill(colour)]
    if kind == "dot":
        return [ellipse(8), fill(colour)]
    return [*svg(WAVE), stroke(colour, 3)]


def piece(n, kind, colour, dx, apex, exit_y, spin, lag):
    """One piece; x and y live in separate groups so each gets its own easing."""
    start = BURST + lag
    top = start + round(2.1 * abs(apex) ** 0.5)     # time to apex grows with sqrt(height)
    end = top + AIR
    spinning = group("Spin", *paint(kind, colour),
                     r=track((start, 0, "rise"), (end, spin)),
                     s=track((end - 18, [100, 100], "in"), (end, [0, 0])))
    rise_fall = group("Y", spinning,
                      p=track((start, [0, 0], "rise"), (top, [0, apex], "fall"), (end, [0, exit_y])))
    return group("Piece %d" % n, rise_fall, p=track((start, [0, 0], "rise"), (end, [dx, 0])))


def build(c):
    confetti = layer(
        "Confetti",
        *[piece(n + 1, kind, c[role], *rest) for n, (kind, role, *rest) in enumerate(PIECES)],
        p=(120, 132), ip=BURST,
    )
    badge = layer(
        "Badge", group("Star", star(5, 44, 23), round_corners(8), fill(c["accent"])),
        p=(120, 132),
        s=track((4, [100, 100], "in-out"), (BURST, [93, 93], "out"),
                (BURST + 10, [106, 106], "in-out"), (40, [100, 100])),
    )
    return comp("Confetti Loop", 240, 240, [badge, confetti], op=120, bg=c["bg"],
                about="Playful but restrained: one pop, fourteen pieces on ballistic arcs.")


if __name__ == "__main__":
    main(build, __file__, palette="berry")
