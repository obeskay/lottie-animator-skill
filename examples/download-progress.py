"""Download: the arrow drops into its tray, a ring fills, the ring becomes a check.

Brief: a file on its way, then arrived; functional register. Hero is the ring.
It fills at an uneven pace, quick, slower, quick to finish, because a constant
rate reads as a fake progress bar. Every phase starts before the last has
finished: the ring appears around the fading icon, and the full ring closes
inward into the disc the check is written on.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

ARROW = "M0 -37 V7 M-16.5 -10 L0 7 L16.5 -10"
TRAY = "M-35 9 V23 C-35 29 -30 33 -24 33 H24 C30 33 35 29 35 23 V9"
CHECK = "M-25 1 L-8 18 L26 -17"
RING, WEIGHT = 112, 8
EDGE = RING / 2 + WEIGHT / 2     # outer radius of the ring, and of the disc it becomes


def paced(*keys):
    """(t, value, speed) keys -> a track whose speed carries through every key.

    A token ease stops at each keyframe, which turns progress into a stepper.
    Handles a third of the way along each segment make every segment a cubic
    Hermite: it slows down and speeds up between keys without stopping. Speed
    is value per frame; 0 eases that end.
    """
    frames = []
    for (t0, v0, s0), (t1, v1, s1) in zip(keys, keys[1:]):
        k = (t1 - t0) / (3.0 * (v1 - v0))
        frames.append((t0, v0, "linear", {"o": {"x": [1 / 3], "y": [s0 * k]},
                                          "i": {"x": [2 / 3], "y": [1 - s1 * k]}}))
    return track(*frames, keys[-1][:2])


def build(c):
    arrow = group(
        "Arrow", *svg(ARROW), stroke(c["ink"], WEIGHT),
        p=track((4, [0, -12], "out"), (24, [0, 0]), (42, [0, 0], "in-out"), (52, [0, 7])),
        o=track((4, 0, "out"), (12, 100)),
    )
    # Fits inside the ring, so the two can cross-fade without touching.
    icon = layer(
        "Icon", arrow, group("Tray", *svg(TRAY), stroke(c["ink"], WEIGHT)),
        p=(120, 122),
        s=track((0, [94, 94], "out"), (16, [100, 100]), (50, [100, 100], "in"), (62, [95, 95])),
        o=track((0, 0, "out"), (8, 100), (50, 100, "in"), (62, 0)),
    )
    fill_up = paced((62, 0, 0), (88, 38, 0.55), (124, 60, 0.5), (156, 100, 0))
    # Size and width share one curve, so the outer edge holds still while the
    # ring thickens inward into a disc. The width runs past the centre, so the
    # hole shuts while the ease is still moving instead of lingering as a pinhole.
    size = track((156, [RING, RING], "out"), (184, [EDGE - 5, EDGE - 5]))
    width = track((156, WEIGHT, "out"), (184, EDGE + 5))
    ring = layer(
        "Ring",
        group("Progress", ellipse(size), stroke(c["accent"], width), trim(0, fill_up)),
        group("Track", ellipse(RING), stroke(c["surface"], WEIGHT)),
        p=(120, 120),
        s=track((52, [96, 96], "out"), (70, [100, 100])),
        o=track((52, 0, "out"), (62, 100)),
    )
    check = layer(
        "Check",
        group("Check", *svg(CHECK), stroke(c["on_accent"], WEIGHT),
              trim(0, track((166, 8, "out"), (190, 100)))),
        p=(120, 121),
        o=track((166, 0, "out"), (169, 100)),
    )
    return comp("Download Progress", 240, 240, [check, ring, icon], op=224, bg=c["bg"],
                about="Arrow into tray, a ring that fills at an uneven pace, then a check.")


if __name__ == "__main__":
    main(build, __file__, palette="harbor")
