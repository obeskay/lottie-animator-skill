"""Success check: a disc settles, the check writes itself, one quiet ripple.

Brief: reassurance, product register. Hero is the check stroke; the disc and
the ripple support it at a fraction of its presence. No overshoot: weight
comes from the disc decelerating hard into place.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403


def build(c):
    disc = layer(
        "Disc", group("Disc", ellipse(128), fill(c["accent"])),
        p=(120, 120),
        s=track((0, [92, 92], "out"), (22, [100, 100])),
        o=track((0, 0, "out"), (10, 100)),
    )
    # A trim with a round cap paints a dot at zero length, so the stroke starts
    # a few percent drawn and fades in over the first frames of the gesture.
    check = layer(
        "Check",
        group("Check", *svg("M-27 1 L-9 19 L28 -18"),
              stroke(c["on_accent"], 12),
              trim(0, track((12, 8, "out"), (36, 100)))),
        p=(120, 122),
        o=track((12, 0, "out"), (15, 100)),
    )
    # The ripple leaves the disc edge as the check lands, and is gone by the hold.
    ripple = layer(
        "Ripple",
        group("Ripple", ellipse(track((30, [128, 128], "out"), (66, [188, 188]))),
              stroke(c["accent"], track((30, 5, "out"), (66, 1)))),
        p=(120, 120),
        o=track((30, 0, "out"), (34, 45, "out"), (66, 0)),
    )
    return comp("Success Check", 240, 240, [check, disc, ripple], op=96,
                bg=c["bg"], about="Disc settles, check writes itself, one quiet ripple.")


if __name__ == "__main__":
    main(build, __file__, palette="forest")
