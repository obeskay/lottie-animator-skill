"""Card stack: three cards settle into a stack, then the front one fills in.

Brief: a message arriving, quiet/premium register. The cards are the stage:
each rises 16 px from 96% on the glide ease, back to front, 6 frames apart.
Then the front card's content writes itself in reading order, 3 frames apart,
and the hero, an accent chip, lands last. No overshoot anywhere.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

W, H, R = 176, 96, 14
TOP = 81        # the front card's top edge; the cards behind peek out above it
CONTENT = 40    # the front card is settled enough to write on


def card(nm, size, peek, tone, start, c):
    """A squircle on a hairline one pixel larger, heavier below: a crisp edge
    on any ground. Rises 16 px from 96% of its size, to peek `peek` px above
    the front card. `tone` is a list of fills, the first painted on top."""
    y = TOP - peek + H * size / 200
    return layer(
        nm,
        group("Card", path(squircle(W, H, R)), *tone),
        group("Edge", path(squircle(W + 2, H + 3, R + 1)), fill(c["ink"], 12), p=(0, 0.5)),
        p=track((start, [120, y + 16], "glide"), (start + 36, [120, y])),
        s=track((start, [size * 0.96] * 2, "glide"), (start + 36, [size, size])),
        o=track((start, 0, "out"), (start + 12, 100)),
    )


def line(nm, x0, x1, y, colour, o, start):
    """A text line: a round-capped stroke drawn from the left. The cap would
    paint a dot at zero length, so it starts a few percent in and fades up."""
    return layer(
        nm, group(nm, *svg("M%g %g L%g %g" % (x0, y, x1, y)), stroke(colour, 7, o),
                  trim(0, track((start, 4, "out"), (start + 24, 100)))),
        parent="Front", o=track((start, 0, "out"), (start + 4, 100)),
    )


def build(c):
    cards = [
        card("Front", 100, 0, [fill(c["bg"])], 12, c),
        card("Middle", 94, 9, [fill(c["surface"])], 6, c),
        # Halfway between surface and ground, from roles only: a half-strength
        # surface over an opaque ground, so the tone re-skins with the palette.
        card("Back", 88, 18, [fill(c["surface"], 50), fill(c["bg"])], 0, c),
    ]
    avatar = layer(
        "Avatar", group("Avatar", ellipse(28), fill(c["muted"], 50)),
        parent="Front", p=(-58, -18),
        s=track((CONTENT, [92, 92], "out"), (CONTENT + 18, [100, 100])),
        o=track((CONTENT, 0, "out"), (CONTENT + 8, 100)),
    )
    lines = [
        line("Name", -28.5, 20.5, -18, c["ink"], 80, CONTENT + 3),
        line("Body 1", -68.5, 68.5, 13.5, c["muted"], 75, CONTENT + 6),
        line("Body 2", -68.5, 26.5, 28.5, c["muted"], 75, CONTENT + 9),
    ]
    land = CONTENT + 22
    chip = layer(
        "Chip", group("Chip", path(squircle(30, 16, 8)), fill(c["accent"])),
        parent="Front",
        p=track((land, [57, -14], "out"), (land + 20, [57, -18])),
        s=track((land, [94, 94], "out"), (land + 20, [100, 100])),
        o=track((land, 0, "out"), (land + 8, 100)),
    )
    return comp("Card Stack", 240, 240, [chip, *lines, avatar, *cards], op=120, bg=c["bg"],
                about="Three cards settle back to front; the content writes in; the chip lands last.")


if __name__ == "__main__":
    main(build, __file__, palette="mono")
