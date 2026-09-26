"""Rocket launch: an SVG icon assembles part by part, ignites, and lifts off.

Brief: anticipation, product register. The art comes straight from
rocket-icon.svg through svg2lottie, one layer per path, named by its id. Hero
is the lift, one in-out move up the rocket's own axis; the accent flame lands
last in the cascade, and its flicker during the lift is a few percent that
settles before the hold.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403
from svg2lottie import convert  # noqa: E402

SVG = Path(__file__).resolve().with_name("rocket-icon.svg")
CENTRE = (122.5, 117.4)   # the middle of the converted art on its 240 canvas
NOZZLE = [68, 172, 0]     # where the flame leaves the body; it flickers from here
OP = 150


def build(c):
    doc, _ = convert(SVG.read_text(), size=240, frames=OP, current_color=c["ink"])
    parts = {part["nm"]: part for part in doc["layers"]}
    paint(parts["flame"], c["accent"])

    arrive = track((0, [94, 94, 100], "out"), (26, [100, 100, 100]))
    for i, name in enumerate(("body", "fin-left", "fin-right", "flame")):
        ks = parts[name]["ks"]
        ks["s"] = delay(arrive, 3 * i)
        ks["o"] = delay(track((0, 0, "out"), (13, 100)), 3 * i)
        parts[name]["parent"] = "Rocket"

    # The flame scales from the nozzle, so only its tip moves: thrust as the
    # lift gathers speed, two smaller breaths, then rest before the hold.
    flame = parts["flame"]["ks"]
    flame["a"] = flame["p"] = static(NOZZLE)
    flame["s"] = track(
        (9, [94, 94, 100], "out"), (35, [100, 100, 100], "in-out"),
        (48, [100, 100, 100], "in-out"), (62, [114, 114, 100], "in-out"),
        (74, [104, 104, 100], "in-out"), (86, [110, 110, 100], "in-out"),
        (106, [100, 100, 100]),
    )

    # The converted layers keep their own pivots; one null places, sizes and
    # lifts them together. 45 degrees is the axis the icon is drawn on.
    rocket = null("Rocket", a=CENTRE, s=76,
                  p=track((48, [107, 134], "in-out"), (100, [119, 122])))
    return comp("Rocket Launch", 240, 240, [rocket] + doc["layers"], op=OP, bg=c["bg"],
                about="An SVG icon, converted part by part, assembles and lifts off its own axis.")


if __name__ == "__main__":
    main(build, __file__, palette="paper")
