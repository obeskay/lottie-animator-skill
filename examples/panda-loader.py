"""Panda loader: a panda munches bamboo inside a slow loading ring.

Brief: patience, gentle and a little charming. Hero is the ring, one constant
turn per loop with an arc that breathes; the panda is secondary action at a
fraction of its presence: four chews, a small nod with each, one blink.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

LEAF = "M0 0 C9 -6 23 -6 32 0 C23 6 9 6 0 0 Z"


def fur(c):
    """Dark and light fur: the darker and the lighter of ink and surface.

    On a light ground that is ink and surface; on a dark one it flips, so the
    face keeps its black patches and the black fur sinks into the night.
    """
    return sorted((c["ink"], c["surface"]), key=lambda color: sum(rgba(color)[:3]))


def chew(shut, open_):
    """Four bites a loop: open over 8 frames, close over 10, rest 12."""
    frames = []
    for t in range(0, 120, 30):
        frames += [(t, shut, "in-out"), (t + 8, open_, "in-out"), (t + 18, shut, "in-out")]
    return track(*frames, (120, shut))


def build(c):
    dark, light = fur(c)

    ring = layer(
        "Ring",
        group("Arc", ellipse(196), stroke(c["accent"], 8),
              trim(0, track((0, 16, "in-out"), (60, 30, "in-out"), (120, 16))),
              r=track((0, 0, "linear"), (120, 360))),
        group("Track", ellipse(196), stroke(c["surface"], 8)),
        p=(120, 120),
    )

    eyes = group("Eyes", ellipse(8, p=(-19, 0)), ellipse(8, p=(19, 0)), fill(light),
                 p=(0, -2), s=track((84, [100, 100], "in-out"), (88, [100, 10], "in-out"),
                                    (94, [100, 100])))
    patches = group(
        "Patches",
        group("Left", ellipse((22, 30)), fill(dark), p=(-21, 0), r=35),
        group("Right", ellipse((22, 30)), fill(dark), p=(21, 0), r=-35),
    )
    mouth = group("Mouth", ellipse((10, 8), p=(0, 4)), fill(dark), p=(0, 22),
                  s=chew([100, 45], [100, 100]))
    head = layer(
        "Head",
        eyes, patches,
        group("Nose", ellipse((16, 10)), fill(dark), p=(0, 14)),
        mouth,
        group("Face", ellipse((100, 86)), fill(light)),
        group("Ears", ellipse(30, p=(-36, -38)), ellipse(30, p=(36, -38)), fill(dark)),
        p=chew([120, 104], [120, 105.5]),
    )
    body = layer(
        "Body",
        group("Belly", ellipse((60, 44), p=(0, 10)), fill(light)),
        group("Body", ellipse((108, 76)), fill(dark)),
        p=(120, 162),
    )
    bamboo = layer(
        "Bamboo",
        group("Leaf", *svg(LEAF), fill(c["support"]), p=(78, -68), r=-24),
        group("Leaf", *svg(LEAF), fill(c["support"]), p=(74, -65), r=28),
        group("Stalk", *svg("M0 0 L82 -72"), stroke(c["support"], 10, cap="butt", dash=(20, 3))),
        p=(84, 194),
    )
    paws = layer(
        "Paws",
        group("Paws", ellipse(22, p=(24, -22)), ellipse(22, p=(50, -45)), fill(dark)),
        parent="Bamboo",  # the paws grip the stalk: move one, the other follows
    )
    return comp("Panda Loader Loop", 240, 240, [paws, head, bamboo, body, ring], op=120,
                bg=c["bg"], about="A panda chews bamboo inside a slow, breathing loading ring.")


if __name__ == "__main__":
    main(build, __file__, palette="paper")
