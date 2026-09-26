"""Toggle switch: the knob crosses the track and the track takes the accent.

Brief: a setting turned on, then off, product register, shown on a dark
ground. Hero is the knob's travel, in-out because it moves on screen from one
rest to another. The track and the knob change colour on exactly the same
curve, so the switch reads as one event rather than three. No squash.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

W, H, INSET = 132, 74, 8
TRAVEL = (W - H) / 2          # the knob's centre, either side of the track's


def build(c):
    def flip(off, on):
        """Off, on, off again, on the knob's beats."""
        return track((20, off, "in-out"), (38, on), (80, on, "in-out"), (96, off))

    # Lit, the knob is the brighter of ink and on_accent. On a dark ground
    # on_accent is dark as well, and a dark knob on the accent reads as a hole.
    lit = max(c["ink"], c["on_accent"], key=lambda hex_color: sum(rgba(hex_color)[:3]))
    knob = group("Knob", ellipse(H - 2 * INSET), fill(flip(rgba(c["muted"]), rgba(lit))),
                 p=flip([-TRAVEL, 0], [TRAVEL, 0]))
    # A true capsule keeps the round knob concentric with the track's ends. A
    # squircle this round clamps flat at the ends and leaves the inset uneven.
    # Off, the track is muted at a third of its strength: a surface-coloured
    # track all but vanishes on a dark ground, and a control you cannot see the
    # edge of does not read as one.
    pill = group("Track", rect((W, H), r=H / 2),
                 fill(flip(rgba(c["muted"]), rgba(c["accent"])), o=flip(34, 100)))
    return comp("Toggle Switch Loop", 240, 240, [layer("Switch", knob, pill, p=(120, 120))], op=120,
                bg=c["bg"], about="Off, on, off: the knob and both colours move on one curve.")


if __name__ == "__main__":
    main(build, __file__, palette="night")
