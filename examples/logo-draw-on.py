"""Logo draw-on: a sun-over-water mark writes its lines, then the sun rises out of the horizon.

Brief: a signature with a small story, quiet register. The mark is logo.svg
converted by svg2lottie, one layer per element, named by its id and painted by
role. The lines open from their middles, top to bottom, 6 frames apart; the
hero is the sun, which rises from behind the horizon through a track matte
whose edge hides under the horizon stroke, and lands last.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403
from svg2lottie import convert  # noqa: E402

SVG = Path(__file__).resolve().with_name("logo.svg")
ROLES = {"sun": "accent", "horizon": "ink", "swell": "muted", "shore": "muted"}
RISE = (22, 76)     # the sun leaves as the last line opens, and settles slowly


def build(c):
    doc, _ = convert(SVG.read_text(), size=240, frames=130)
    parts = {part["nm"]: part for part in doc["layers"]}
    for name, role in ROLES.items():
        paint(parts[name], c[role])

    # Trim start and end part from the middle, so each line opens outward. A
    # round cap at zero length paints a dot: start 4% drawn, fade in over 4 frames.
    for i, name in enumerate(("horizon", "swell", "shore")):
        t = 6 * i
        parts[name]["shapes"][0]["it"].insert(-1, trim(
            track((t, 48, "out"), (t + 26, 0)), track((t, 52, "out"), (t + 26, 100))))
        parts[name]["ks"]["o"] = track((t, 0, "out"), (t + 4, 100))

    # Only the sky shows the sun: an alpha matte down to the horizon's centre
    # line, which the horizon stroke (layered above) covers, so the sun seems to
    # come up from behind it. Converted layers sit on their element centres.
    horizon = parts["horizon"]["ks"]["p"]["k"][1]
    sky = layer("Sky", group("Sky", rect([240, horizon], p=(120, horizon / 2)), fill(c["ink"])), td=1)
    sun = parts["sun"]
    x, y = sun["ks"]["p"]["k"][:2]
    sun["ks"]["p"] = track((RISE[0], [x, y + 100, 0], "glide"), (RISE[1], [x, y, 0]))
    sun["tt"] = 1
    layers = [part for part in doc["layers"] if part is not sun] + [sky, sun]
    return comp("Logo Draw On", 240, 240, layers, op=130, bg=c["bg"],
                about="An SVG mark writes its lines; the sun rises out of the horizon, last.")


if __name__ == "__main__":
    main(build, __file__, palette="paper")
