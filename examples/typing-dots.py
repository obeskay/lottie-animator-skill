"""Typing indicator: three dots lift in a wave, then the bubble rests.

Brief: someone is writing, calm. Hero is the wave; each dot rises 7 px and
darkens from muted to ink at the top, 8 frames after its neighbour. The pause
after the wave is what makes it read as typing rather than a spinner.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

TAIL = "M-52 24 C-53 39 -60 48 -71 54 C-53 55 -39 50 -31 39 Z"


def build(c):
    lift = track((6, [0, 0], "in-out"), (18, [0, -8], "in-out"), (32, [0, 0]))
    tint = track((6, rgba(c["muted"]), "in-out"), (18, rgba(c["ink"]), "in-out"), (32, rgba(c["muted"])))
    dots = [
        group("Dot %d" % (i + 1), ellipse(18), fill(delay(tint, 8 * i)),
              p=delay(lift, 8 * i), a=(0, 0))
        for i in range(3)
    ]
    # Each dot's resting place is its group anchor; the lift moves the group.
    for i, dot in enumerate(dots):
        dot["it"][0]["p"] = static([(i - 1) * 29, 0])
    bubble = layer(
        "Bubble",
        group("Tail", *svg(TAIL), fill(c["surface"])),
        group("Body", path(squircle(152, 90, 28)), fill(c["surface"])),
        p=(120, 116),
    )
    return comp("Typing Dots Loop", 240, 240, [layer("Dots", *dots, p=(120, 116)), bubble],
                op=80, bg=c["bg"], about="A three-dot wave with a rest, so it reads as typing.")


if __name__ == "__main__":
    main(build, __file__, palette="harbor")
