"""Weather sun: the rays turn slowly while a cloud drifts across and back.

Brief: a fair day, ambient register. Hero is the cloud's drift, in-out and
slow; the rays turn at a constant, barely noticed rate and draw in a little
while the cloud covers the sun, a few frames behind it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

# Three circles resting on one baseline: the outline is their arcs, so a
# stroke traces the silhouette instead of every overlap.
CLOUD = "M0 0 A17 17 0 1 1 2.61 -33.8 A28 28 0 0 1 55.25 -40.09 A21 21 0 1 1 64 0 Z"
RAYS = 10


def ray(outer):
    return bezier("M0 -46 L0 %g" % -outer)[0]


def build(c):
    sun = layer("Sun", group("Disc", ellipse(68), fill(c["support"])), p=(101, 113))
    # Ten rays make every 36 degrees look the same, so the loop turns exactly
    # that far; a full turn takes ten loops, which is what lets the file close.
    rays = layer(
        "Rays",
        group("Ray", path(track((30, ray(60), "in-out"), (118, ray(55), "in-out"),
                                (158, ray(55), "in-out"), (238, ray(60)))),
              stroke(c["support"], 7), repeater(RAYS, r=360 / RAYS)),
        p=(101, 113),
        r=track((0, 0, "linear"), (240 * RAYS, 360)),
    )
    home, over = [147, 159], [123, 159]
    cloud = layer(
        "Cloud",
        group("Cloud", *svg(CLOUD, 1.0, (34, -28)), stroke(c["muted"], 3), fill(c["surface"])),
        p=track((24, home, "in-out"), (112, over, "in-out"), (152, over, "in-out"), (232, home)),
    )
    return comp("Weather Sun Loop", 240, 240, [cloud, rays, sun], op=240,
                bg=c["bg"], about="Rays turn slowly while a cloud drifts across the sun and back.")


if __name__ == "__main__":
    main(build, __file__, palette="sky")
