"""Like: the outline presses in, the filled heart pops, a burst clears the way.

Brief: delight, playful register (on request only). The single overshoot is
the heart's 8% pop; the press before it is the anticipation. The ring and the
sparks are follow-through: they leave as the heart settles, so the rest is
just the heart.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

HEART = ("M50 86 C24 68 8 52 8 34 C8 20 19 10 32 10 C40 10 46 14 50 21 "
         "C54 14 60 10 68 10 C81 10 92 20 92 34 C92 52 76 68 50 86 Z")


def spark(color, size, origin, reach, start):
    """One dot flying out from the heart; the repeater makes eight."""
    return [
        ellipse(track((start, [size, size], "in-out"), (start + 28, [0, 0]))),
        fill(color),
    ], track((start, [0, -origin], "out"), (start + 28, [0, -reach]))


def build(c):
    press = track((10, [100, 100], "in-out"), (18, [88, 88]))
    outline = layer(
        "Outline", group("Heart", *svg(HEART, 1.08, (50, 48)), stroke(c["muted"], 6)),
        p=(120, 122), s=press, o=track((18, 100, "hold"), (19, 0)),
    )
    heart = layer(
        "Heart", group("Heart", *svg(HEART, 1.08, (50, 48)), fill(c["accent"])),
        p=(120, 122),
        s=track((18, [88, 88], "out"), (30, [108, 108], "in-out"), (46, [100, 100])),
        o=track((18, 0, "hold"), (19, 100)),
    )
    ring = layer(
        "Ring", group("Ring", ellipse(track((18, [60, 60], "out"), (34, [164, 164]))),
                      stroke(c["accent"], track((18, 16, "out"), (34, 0)))),
        p=(120, 120), o=track((18, 0, "hold"), (19, 100)),
    )
    big, big_p = spark(c["accent"], 11, 72, 106, 23)
    small, small_p = spark(c["support"], 8, 66, 94, 25)
    sparks = layer(
        "Sparks",
        group("Accent", group("Dot", *big, p=big_p), repeater(8, r=45)),
        group("Support", group("Dot", *small, p=small_p), repeater(8, r=45), r=22.5),
        p=(120, 120), o=track((23, 0, "hold"), (24, 100)),
    )
    return comp("Heart Like", 240, 240, [sparks, heart, outline, ring], op=100,
                bg=c["bg"], about="Press, pop, burst: the one playful example, labelled as such.")


if __name__ == "__main__":
    main(build, __file__, palette="berry")
