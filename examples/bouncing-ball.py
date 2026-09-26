"""Bouncing ball: the classic squash-and-stretch exercise, bouncing in place.

Brief: play, playful register (on request only). Hero is the ball's height,
and gravity sets its spacing: tight at the top, where the ball hangs, wide at
the floor. It stretches as it falls, squashes on contact and stretches again
leaving, always at constant volume (sx * sy = 10000), pivoting on its contact
point so the squash stays on the floor. The shadow tracks the height. No
overshoot: the squash is the only exaggeration.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

# Gravity is a parabola: the `fall` token is exactly t^2, so frame to frame the
# ball covers 1, 3, 5, 7... units falling, and `rise` mirrors it going up.

BALL = 56
TOP, FLOOR = 78, 198    # y of the ball's underside at the apex and on the floor
LAND, LEAVE, LOOP = 28, 32, 60


def bounce(top, floor):
    """A value that follows the ball's height: `top` at the apex, `floor` on contact."""
    return track((0, top, "fall"), (LAND, floor, "hold"),
                 (LEAVE, floor, "rise"), (LOOP, top))


def build(c):
    ball = layer(
        "Ball", group("Ball", ellipse(BALL), fill(c["accent"])),
        p=bounce([120, TOP], [120, FLOOR]),
        a=(0, BALL / 2),        # pivot on the contact point
        s=track((0, [100, 100], "hold"),
                (12, [100, 100], "in"),
                (LAND, [92, 108], "out"),       # stretched by speed as it arrives
                (LAND + 2, [125, 80], "in-out"),  # squash: the floor takes the impact
                (LEAVE + 2, [90, 112], "out"),  # push off, stretched leaving
                (48, [100, 100], "hold"),
                (LOOP, [100, 100])),
    )
    shadow = layer(
        "Shadow", group("Shadow", ellipse([64, 10]), fill(c["muted"], 40)),
        p=(120, FLOOR + 1),
        s=bounce([50, 50], [100, 100]),
        o=bounce(45, 100),
    )
    return comp("Bouncing Ball Loop", 240, 240, [ball, shadow], op=LOOP, bg=c["bg"],
                about="Playful: squash and stretch at constant volume, spaced by gravity.")


if __name__ == "__main__":
    main(build, __file__, palette="citrus")
