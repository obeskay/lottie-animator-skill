"""Equalizer: five bars rise and fall like a track playing, low end left.

Brief: music is on; functional register, on a dark ground. Hero is the bar
heights. Each bar is a line drawn from the bottom, so a trim end is its level
and the round caps stay round at any height. The bars share the downbeat at
the loop point and go their own way in between, the low end slow and tall,
the treble quick and low, which is what keeps it from reading as a sine wave.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

# (frame, level %) per bar. Every list starts and ends on the same level, and
# nothing drops under 16 %, so a bar never shrinks to a dot.
LEVELS = [
    [(0, 64), (20, 24), (40, 58), (62, 22), (80, 70), (100, 28), (120, 64)],
    [(0, 86), (12, 48), (26, 74), (42, 38), (60, 100), (72, 56), (86, 80), (104, 42), (120, 86)],
    [(0, 58), (18, 92), (34, 50), (50, 78), (66, 44), (80, 88), (98, 54), (110, 70), (120, 58)],
    [(0, 40), (10, 66), (24, 32), (38, 58), (56, 28), (70, 62), (84, 36), (100, 60), (120, 40)],
    [(0, 22), (8, 42), (20, 18), (34, 36), (48, 20), (58, 44), (74, 16), (88, 38), (104, 20),
     (112, 30), (120, 22)],
]

# `in-out` holds each level, then snaps to the next: a stepper, not a meter.
# `standard` gets going sooner and settles longer, so a bar is always on its
# way somewhere, and it peaks under three times its mean speed.


def build(c):
    bars = [
        group("Bar %d" % (i + 1), *svg("M0 48 V-48"), stroke(c["accent"], 16),
              trim(0, track(*[(t, v, "standard") for t, v in keys])), p=((i - 2) * 28, 0))
        for i, keys in enumerate(LEVELS)
    ]
    return comp("Equalizer Loop", 240, 240, [layer("Bars", *bars, p=(120, 98))], op=120,
                bg=c["bg"], about="Five bars, each on its own tempo, bass slow and treble quick.")


if __name__ == "__main__":
    main(build, __file__, palette="night")
