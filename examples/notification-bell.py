"""Notification bell: struck once, it swings itself still, the badge answers.

Brief: something arrived, calm, product register. Hero is the swing about the
hanging point, decaying 14, -10, 6, -3 degrees to rest. The clapper swings a
third as far again on top of it, four frames late: overlap, not wobble. The
badge swells once. Then the bell rests for the second half of the loop.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

# Drawn on a 100-unit grid, hanging from the knob at (50, 12).
BODY = ("M50 15 C62.7 15 73 25.3 73 38 C73 56 77 65 85 70.5 "
        "C89.5 73.5 88.5 79 83.5 79 L16.5 79 C11.5 79 10.5 73.5 15 70.5 "
        "C23 65 27 56 27 38 C27 25.3 37.3 15 50 15 Z")
S = 1.35                     # grid units to pixels
PIVOT = (120, 67)            # the knob, in the composition
BADGE = (154, 81)
BADGE_D = 27
GAP = 5


# A struck pendulum moves like a sine: it leaves rest at full speed (`strike`)
# and turns slowly at each end (`swing`). `in-out` is built for travel between
# rests; it would park the bell at every turn and snap it through the middle.


def swing(scale=1.0):
    """The ring: 14 degrees one way, then turns that decay to rest."""
    return track((0, 0, "strike"), (6, 14 * scale, "swing"), (17, -10 * scale, "swing"),
                 (28, 6 * scale, "swing"), (38, -3 * scale, "swing"), (48, 0))


def build(c):
    pivot = null("Pivot", p=PIVOT, r=swing())
    bell = layer(
        "Bell",
        group("Bell", *svg(BODY, S, (50, 12)), ellipse(10 * S), fill(c["ink"])),
        parent="Pivot", tt=2,
    )
    # The clapper rides on the bell and adds a third of its swing, four frames
    # late: it trails through each turn and settles after the bell does.
    clapper = layer(
        "Clapper", group("Clapper", ellipse(14 * S, p=(0, 77.5 * S)), fill(c["ink"])),
        parent="Pivot", r=delay(swing(1 / 3), 4),
    )
    pulse = track((4, [100, 100], "in-out"), (18, [114, 114], "in-out"), (42, [100, 100]))
    badge = layer("Badge", group("Badge", ellipse(BADGE_D), fill(c["accent"])), p=BADGE, s=pulse)
    # An inverted alpha matte cuts a ring of ground around the badge out of the
    # bell, so the two read apart on any background without painting one.
    gap = layer("Gap", group("Gap", ellipse(BADGE_D + 2 * GAP), fill(c["accent"])),
                p=BADGE, s=pulse, td=1)
    return comp("Notification Bell Loop", 240, 240, [badge, gap, bell, clapper, pivot], op=120,
                bg=c["bg"], about="One ring that swings itself still, the clapper a beat behind.")


if __name__ == "__main__":
    main(build, __file__, palette="citrus")
