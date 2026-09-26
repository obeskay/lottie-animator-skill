"""Indeterminate spinner: one arc whose head and tail chase each other round.

Brief: working, don't worry; functional register. Hero is the arc's length,
which grows as the head runs ahead and shrinks as the tail catches up, while
the ring turns at a constant speed underneath. It never rests, so the ease
on each sweep is what gives it a pulse. Ink, not the accent: a loader carries
no meaning, and ink reads on every ground.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from motion import *  # noqa: E402,F403

SWEEP, REACH = 40, 240      # frames, degrees: three sweeps of 240 make two whole turns
SHORT = 4                   # the shortest arc, in percent of the ring
LONG = SHORT + REACH / 3.6  # 360 degrees is 100 percent

# `in-out` peaks at five times its mean speed: right for one move, a strobe on
# a head that sweeps 240 degrees in 40 frames. `standard` peaks under three,
# and decelerates longer than it accelerates.


def build(c):
    # The tail rides the group's rotation and the length is the trim, so the
    # head is their sum. While the tail sweeps, the length shrinks on the same
    # curve and the head stands still; each cycle starts where the last ended
    # without a trim offset, which the loop check would read as open.
    length, tail = [], []
    for i in range(7):
        t = i * SWEEP
        length.append((t, LONG if i % 2 == 0 else SHORT, "standard"))
        tail.append((t, REACH * ((i + 1) // 2), "standard"))
    arc = group("Arc", ellipse(104), stroke(c["ink"], 10), trim(0, track(*length)),
                r=track(*tail))
    spinner = layer("Spinner", arc, p=(120, 120), r=track((0, 0, "linear"), (6 * SWEEP, 720)))
    ring = layer("Track", group("Track", ellipse(104), stroke(c["surface"], 10)), p=(120, 120))
    return comp("Spinner Arc Loop", 240, 240, [spinner, ring], op=6 * SWEEP, bg=c["bg"],
                about="Head leads, tail follows, the ring turns: a seamless indeterminate spinner.")


if __name__ == "__main__":
    main(build, __file__, palette="mono")
