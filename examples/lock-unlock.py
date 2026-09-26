"""Lock toggle: the shackle lifts free, the lock turns the accent, then closes.

Brief: access granted and withdrawn, product register. Hero is the shackle
lifting 18 px straight up: its short left leg leaves the body while the long
right leg stays inside, which is what reads as open. The colour follows the
shackle a few frames late, so the state change looks caused, not painted on.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

W, H = 108, 86                  # the body; the shackle is drawn from its top edge
TOP = -H / 2
LIFT = 18
# The left leg dips 3 px into the body and the right one 34, so a lift of
# LIFT frees the left leg and leaves the right one seated.
SHACKLE = "M-27 %g L-27 %g A27 27 0 0 1 27 %g L27 %g" % (TOP + 3, TOP - 20, TOP - 20, TOP + 34)


def build(c):
    ink, accent = rgba(c["ink"]), rgba(c["accent"])
    tint = track((26, ink, "in-out"), (44, accent), (87, accent, "in-out"), (101, ink))
    shackle = layer(
        "Shackle", group("Shackle", *svg(SHACKLE), stroke(tint, 13)),
        p=track((24, [120, 144], "out"), (42, [120, 144 - LIFT]),
                (84, [120, 144 - LIFT], "in-out"), (98, [120, 144])),
    )
    body = layer(
        "Body",
        group("Keyhole", ellipse(20, p=(0, -3)), rect((8, 20), p=(0, 9), r=4), fill(c["on_accent"])),
        group("Body", path(squircle(W, H, 14)), fill(tint)),
        p=(120, 144),
    )
    return comp("Lock Toggle Loop", 240, 240, [body, shackle], op=120,
                bg=c["bg"], about="The shackle lifts free and the colour follows; then it locks again.")


if __name__ == "__main__":
    main(build, __file__, palette="sky")
