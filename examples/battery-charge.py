"""Battery charging: the charge climbs in four steps, the bolt settles, it drains.

Brief: charging, steady; functional register. Hero is the charge level. It
rises a quarter at a time with a rest after each step; that stepping is what
reads as charging rather than loading. The bolt sits across the level line,
so it is drawn twice, ink on the empty side and on_accent on the charge. At
full the light bolt sinks into the charge: nothing left to do.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

BOLT = "M3.3 -22 L-15.4 3.3 L-1.1 3.3 L-3.3 22 L15.4 -3.3 L1.1 -3.3 Z"
BODY_W, BODY_H, WEIGHT = 132, 72, 7
CELL_W, CELL_H = BODY_W - 2 * WEIGHT, BODY_H - 2 * WEIGHT   # inset by a stroke's width
X = 115          # body centre; the terminal nub pushes the whole to the right


def bolt(color, **transform):
    return group("Bolt", *svg(BOLT), round_corners(2.5), fill(color), **transform)


def build(c):
    # 18 frames up, 18 at rest; the drain resets it while the charge is invisible.
    level = track((14, [0, 100], "in-out"), (32, [25, 100]), (50, [25, 100], "in-out"),
                  (68, [50, 100]), (86, [50, 100], "in-out"), (104, [75, 100]),
                  (122, [75, 100], "in-out"), (140, [100, 100]), (222, [100, 100], "hold"),
                  (223, [0, 100]))
    # Level is the matte: a sharp rectangle scaled from the cell's left edge.
    # The Charge layer below it shows only where the rectangle is.
    matte = layer(
        "Level", group("Level", rect((CELL_W, CELL_H + 4), p=(CELL_W / 2, 0)), fill(c["ink"]),
                       p=(-CELL_W / 2, 0), s=level),
        p=(X, 120), td=1,
    )
    charge = layer(
        "Charge",
        bolt(c["on_accent"],
             s=track((146, [100, 100], "out"), (166, [88, 88], "hold"), (223, [100, 100])),
             o=track((146, 100, "out"), (162, 0, "hold"), (223, 100))),
        group("Cell", path(squircle(CELL_W, CELL_H, 6)), fill(c["accent"])),
        p=(X, 120), tt=1,
        o=track((196, 100, "in-out"), (222, 0, "hold"), (223, 100)),
    )
    body = layer(
        "Body",
        group("Nub", *svg("M0 -9 V9"), stroke(c["ink"], WEIGHT), p=(BODY_W / 2 + WEIGHT + 4, 0)),
        group("Body", path(squircle(BODY_W, BODY_H, 14)), stroke(c["ink"], WEIGHT)),
        p=(X, 120),
    )
    return comp("Battery Charge Loop", 240, 240,
                [matte, charge, layer("Bolt", bolt(c["ink"]), p=(X, 120)), body], op=240,
                bg=c["bg"], about="Charge climbs in eased steps, the bolt settles, then it drains.")


if __name__ == "__main__":
    main(build, __file__, palette="forest")
