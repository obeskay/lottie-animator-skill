"""Play/pause: the triangle splits in two and each half squares off into a bar.

Brief: a media toggle, product register. Hero is the glyph's shape: the play
triangle is cut into a thin strip and a smaller triangle, each drawn with the
four points of one pause bar, so the morph is a straight tween of matching
vertices. round_corners() softens every state at render time. Both states
hold long enough to read.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

W, H = 46, 52            # play triangle
BAR, GAP, TALL = 15, 12, 46  # pause bars
ROUND = 4.5


def poly(*points):
    return {"c": True, "v": [list(p) for p in points],
            "i": [[0, 0] for _ in points], "o": [[0, 0] for _ in points]}


def glyphs():
    # A right-pointing triangle looks centred when the point halfway between
    # its box centre and its centroid sits on the button's centre.
    left = -5 * W / 12
    tip = left + W
    edge = lambda x: -H / 2 * (1 - (x - left) / W)  # noqa: E731  top edge; the bottom mirrors it
    # Cut where both halves hold equal area; overlap them by the corner radius
    # so the rounding at the cut hides inside the other half.
    cut = left + W * (1 - 0.5 ** 0.5)
    a, b = cut + ROUND, cut - ROUND
    # The tip is two points 2 px apart: they open into the bar's right edge, and
    # round_corners() cannot round a point that sits on its twin.
    play = (poly((left, -H / 2), (a, edge(a)), (a, -edge(a)), (left, H / 2)),
            poly((b, edge(b)), (tip, -1), (tip, 1), (b, -edge(b))))
    x0, x1 = GAP / 2, GAP / 2 + BAR
    pause = (poly((-x1, -TALL / 2), (-x0, -TALL / 2), (-x0, TALL / 2), (-x1, TALL / 2)),
             poly((x0, -TALL / 2), (x1, -TALL / 2), (x1, TALL / 2), (x0, TALL / 2)))
    return play, pause


def build(c):
    play, pause = glyphs()
    halves = [
        path(track((40, play[i], "in-out"), (60, pause[i], "hold"), (100, pause[i], "in-out"), (120, play[i])))
        for i in (0, 1)
    ]
    glyph = layer("Glyph", group("Glyph", *halves, round_corners(ROUND), fill(c["on_accent"])), p=(120, 120))
    button = layer("Button", group("Disc", ellipse(128), fill(c["accent"])), p=(120, 120))
    return comp("Play Pause Loop", 240, 240, [glyph, button], op=120,
                bg=c["bg"], about="Each half of the play triangle squares off into a pause bar, and back.")


if __name__ == "__main__":
    main(build, __file__, palette="dusk")
