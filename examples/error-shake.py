"""Error: a disc settles, an X crosses it out, the whole mark shakes its head.

Brief: refusal, product register. Hero is the shake: four turns decaying from
10 px to rest in under half a second, eased in-out between turns so each one
snaps and stops rather than wobbling. The disc and the X only set the stage;
the shake starts the moment the X is complete.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403


def bar(c, d, start):
    """One stroke of the X, written with a trim; it fades in so the cap never pops."""
    return group("Bar", *svg(d), stroke(c["on_accent"], 12),
                 trim(0, track((start, 8, "out"), (start + 16, 100))),
                 o=track((start, 0, "out"), (start + 3, 100)))


def build(c):
    # The first leg is `out`: struck from rest, fastest at the start. Every turn
    # after it is `in-out`, and the turns land on even frames so a 30 fps GIF
    # still shows each extreme.
    shake = null("Shake", p=track(
        (30, [120, 120], "out"), (34, [110, 120], "in-out"), (40, [128, 120], "in-out"),
        (46, [115, 120], "in-out"), (52, [122, 120], "in-out"), (58, [120, 120])))
    disc = layer(
        "Disc", group("Disc", ellipse(128), fill(c["accent"])),
        parent="Shake",
        s=track((0, [94, 94], "out"), (22, [100, 100])),
        o=track((0, 0, "out"), (10, 100)),
    )
    cross = layer("Cross", bar(c, "M-19 -19 L19 19", 12), bar(c, "M19 -19 L-19 19", 15),
                  parent="Shake")
    return comp("Error Shake", 240, 240, [cross, disc, shake], op=90,
                bg=c["bg"], about="Disc settles, X writes itself, then one crisp decaying shake.")


if __name__ == "__main__":
    main(build, __file__, palette="mono")
