"""Location ping: rings spread across the ground from a pin that stays put.

Brief: you are here, calm and certain. Hero is the rings' size: flattened
ellipses, so they lie on the ground plane and read as a place on a map. They
spread at one steady speed, like a ripple, and thin and fade as they go. The
pin does not move; it is what the eye rests on.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

PIN = ("M0 0 C-7 -11 -26 -27 -26 -48 A26 26 0 1 1 26 -48 C26 -27 7 -11 0 0 Z "
       "M0 -58 A10 10 0 1 0 0 -38 A10 10 0 1 0 0 -58 Z")
BASE = (120, 146)
LIFE, EVERY = 120, 40


def build(c):
    size = track((0, [30, 10], "linear"), (LIFE, [184, 60]))
    fade = track((0, 0, "out"), (10, 90, "linear"), (LIFE, 0))
    weight = track((0, 3.5, "out"), (LIFE, 1.5))
    # A ring leaves every 40 frames, the first at frame 20 so the opening frame
    # already shows three. Rings that start before frame 0 are the tail of the
    # previous loop, which is what makes frame 120 frame 0 again.
    rings = layer("Rings", *[
        group("Ring", ellipse(delay(size, t)),
              stroke(c["accent"], delay(weight, t), o=delay(fade, t)))
        for t in range(20 - LIFE, 120, EVERY)
    ], p=BASE)
    # Even-odd fill turns the second subpath into a hole: the ground shows through.
    pin = layer("Pin", group("Pin", *svg(PIN, 1.15), fill(c["accent"], evenodd=True)), p=BASE)
    shadow = layer("Shadow", group("Shadow", ellipse([30, 10]), fill(c["surface"])), p=BASE)
    return comp("Location Ping Loop", 240, 240, [pin, rings, shadow], op=120,
                bg=c["bg"], about="A still pin; rings spread across the ground, thin and fade.")


if __name__ == "__main__":
    main(build, __file__, palette="dusk")
