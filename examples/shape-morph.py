"""Shape morph: a squircle softens into a circle and back, a quarter turn per cycle.

Brief: calm transformation, quiet register. Hero is the outline itself, one
path morphing between eight-vertex shapes, in-out, with a rest at each end.
The turn supports it: 45 degrees per leg, so the squircle comes back rotated
90 degrees, which is the same shape.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403


def circle(diameter):
    """A circle laid out like squircle(), so the two morph vertex for vertex.

    With the corner as wide as the half side, squircle() puts its eight
    vertices in pairs on the axes and its edges shrink to nothing; shortening
    the handles to 0.5523 of the radius turns each corner into a quarter arc.
    Every handle keeps its direction, so every frame between is smooth.
    """
    shape = squircle(diameter, diameter, diameter)
    for key in ("i", "o"):
        shape[key] = [[round(x * 0.5523, 3) for x in handle] for handle in shape[key]]
    return shape


def build(c):
    # The circle is a little wider than the squircle so the two carry the same
    # weight; at equal widths the circle reads as shrinking.
    square, disc = squircle(132, 132, 18), circle(142)
    shape = track((10, square, "in-out"), (50, disc, "in-out"),
                  (70, disc, "in-out"), (110, square))
    # The turn trails the softening by 4 frames and leads the sharpening by 4,
    # so it only runs while there are corners to see. A squircle is symmetric
    # under a quarter turn: the snap from 90 back to 0 on the last frame is
    # invisible, and the loop closes exactly.
    turn = track((14, 0, "in-out"), (54, 45, "in-out"), (66, 45, "in-out"),
                 (106, 90, "hold"), (119, 0))
    morph = layer("Shape", group("Shape", path(shape), fill(c["accent"]), r=turn), p=(120, 120))
    return comp("Shape Morph Loop", 240, 240, [morph], op=120, bg=c["bg"],
                about="A squircle softens into a circle and back, a quarter turn per cycle.")


if __name__ == "__main__":
    main(build, __file__, palette="sky")
