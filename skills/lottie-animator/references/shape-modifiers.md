# Shape Modifiers

Modifiers transform the geometry that precedes them **inside the same group**. Order
matters: a modifier only sees the shape items listed before it in `it`.

```
"it": [ sh (paths) , tm (modifier) , st/fl (paint) , tr (transform) ]
```

Put the modifier after the paths it should affect and before the paint. A trim path
placed after the stroke, or in a different group, silently does nothing.

---

## Trim Path (`tm`) — draw-on

The workhorse for stroke icons, signatures, checkmarks, and progress rings. It reveals
a stroke between a start and end percentage.

| Key | Meaning |
|---|---|
| `s` | start of the visible span, 0–100 |
| `e` | end of the visible span, 0–100 |
| `o` | offset in degrees; rotates the trim window around the path |
| `m` | 1 = apply to all paths together, 2 = apply to each path separately |

**Required:** `s`, `e`, `o`. Omitting any of them makes the player drop the layer.

Draw a stroke on over 30 frames:

```json
{
  "ty": "tm", "nm": "Draw On",
  "s": {"a": 0, "k": 0},
  "e": {"a": 1, "k": [
    {"t": 18, "s": [0], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
    {"t": 48, "s": [100]}
  ]},
  "o": {"a": 0, "k": 0},
  "m": 1
}
```

Direction is controlled by which end you animate. Animating `e` from 0 draws forward;
animating `s` from 100 down to 0 draws backward.

`m: 1` treats every path in the group as one continuous line, so a multi-path icon
draws as a single gesture. `m: 2` draws each path on its own — use it when the paths
are separate strokes that should appear together rather than in sequence.

### Loader ring

A spinner is a trim window of fixed width chased around a circle by the offset:

```json
{
  "ty": "tm",
  "s": {"a": 0, "k": 15},
  "e": {"a": 0, "k": 85},
  "o": {"a": 1, "k": [{"t": 0, "s": [0]}, {"t": 60, "s": [360]}]},
  "m": 1
}
```

Rotating `o` by exactly 360 closes the loop perfectly, so the cycle never jumps.

---

## Repeater (`rp`) — radial and linear patterns

Duplicates the preceding shapes, applying its transform cumulatively to each copy.
Good for tick marks, loading dots, bursts, and dials.

| Key | Meaning |
|---|---|
| `c` | number of copies |
| `o` | offset applied to the first copy |
| `tr` | transform applied cumulatively, including `so` and `eo` |
| `so` | opacity of the first copy |
| `eo` | opacity of the last copy |

**Required:** `c`, `o`, `tr`.

Eight marks around a circle, fading out:

```json
{
  "ty": "rp", "nm": "Radial",
  "c": {"a": 0, "k": 8},
  "o": {"a": 0, "k": 0},
  "tr": {
    "ty": "tr",
    "p": {"a": 0, "k": [0, 0]},
    "a": {"a": 0, "k": [0, 0]},
    "s": {"a": 0, "k": [100, 100]},
    "r": {"a": 0, "k": 45},
    "o": {"a": 0, "k": 100},
    "so": {"a": 0, "k": 100},
    "eo": {"a": 0, "k": 20}
  }
}
```

The rotation must divide evenly into 360 (`360 / c`) or the ring will not close.
Because the transform compounds, a scale of 90% shrinks each copy relative to the
previous one, not relative to the original.

---

## Offset Path (`op`) — outline and thickness

Grows or shrinks a shape along its normals. Useful for glow rings and weight changes
that a stroke cannot express.

| Key | Meaning |
|---|---|
| `a` | offset amount; negative shrinks |
| `lj` | line join: 1 miter, 2 round, 3 bevel |
| `ml` | miter limit |

```json
{
  "ty": "op", "nm": "Grow",
  "a": {"a": 1, "k": [{"t": 0, "s": [0]}, {"t": 30, "s": [8]}]},
  "lj": 2
}
```

Support is thinner than for trim and repeater: older `lottie-web` builds and some
native players ignore it. Render before relying on it, and prefer an animated stroke
width when the target runtime is unknown.

---

## Merge Paths (`mm`)

Boolean operations on the preceding paths: `mm: 1` merge, `2` add, `3` subtract,
`4` intersect, `5` exclude.

```json
{"ty": "mm", "nm": "Subtract", "mm": 3}
```

**Not supported by the SVG renderer in lottie-web** — it works in canvas and in some
native players. Treat it as a last resort and verify on the actual target. Producing
the shape you want directly in the source SVG is almost always the better answer.

---

## Rounded Corners (`rd`)

Rounds the corners of the preceding paths.

```json
{"ty": "rd", "nm": "Round", "r": {"a": 0, "k": 8}}
```

Only affects actual corners; it does nothing to a path that is already smooth.

---

## Checklist

- The modifier sits after its geometry and before the paint, in the same group.
- Every required property is present — a missing one drops the whole layer.
- Repeater rotation divides evenly into 360.
- Trim offsets that loop travel exactly 360.
- You rendered it and looked at it. Modifier support varies by player more than any
  other part of the format.
