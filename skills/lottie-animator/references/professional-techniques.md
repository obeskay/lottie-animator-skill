# Professional Lottie Animation Techniques

Techniques taken from picking apart professional character animations.

## 1. Frame-by-Frame Animation (Sprite Sheet Style)

The most reliable approach for complex character motion.

### Concept

Instead of animating properties continuously, build **several distinct poses**
and switch between them in sequence.

```
Frame 0-6:   Pose 1 (visible)
Frame 6-12:  Pose 2 (visible)
Frame 12-18: Pose 3 (visible)
...
```

### JSON structure

```json
{
  "layers": [
    {
      "nm": "Cat Pose 1",
      "ip": 0,    // in point: appears at frame 0
      "op": 6,    // out point: disappears at frame 6
      "st": 0,
      "shapes": [/* cat in pose 1 */]
    },
    {
      "nm": "Cat Pose 2",
      "ip": 6,
      "op": 12,
      "st": 0,
      "shapes": [/* cat in pose 2 */]
    },
    {
      "nm": "Cat Pose 3",
      "ip": 12,
      "op": 18,
      "st": 0,
      "shapes": [/* cat in pose 3 */]
    }
  ]
}
```

Every layer needs `ip`, `op`, **and** `st`. Leave out any one of them and the
player hides the layer at every frame.

### Why use it

- **Total freedom** — each pose can be a completely different shape
- **No matching vertex count** — unlike morphing, which requires it
- **More organic** — better for characters than interpolating one shape
- Standard practice in hand-animated work

### When to reach for it

- Walk cycles and run cycles
- Any motion with drastic shape changes
- Whenever morphing produces ugly in-between frames

### Frame arithmetic

```
total frames = pose count × frames per pose
duration     = total frames / frame rate

Example:
  6 poses × 6 frames = 36 frames
  36 frames / 60 fps = 0.6s per loop
```

---

## 2. Parenting Hierarchy (Bone System)

A parent/child chain for coordinated motion.

### Concept

One parent layer drives the position and rotation of its children.

```
Shadow (parent, ind 14)
├── Head
├── Body
├── Ear Inner
├── Eye
├── Nose
└── ...
```

### JSON structure

```json
{
  "layers": [
    {
      "ind": 14,
      "nm": "Shadow",
      "ty": 4,
      "ks": {
        "p": {"a": 0, "k": [340, 195, 0]}  // the parent's own position
      }
    },
    {
      "ind": 1,
      "nm": "Head",
      "parent": 14,  // <-- points at the parent's ind
      "ty": 4,
      "ks": {
        "p": {"a": 0, "k": [88, -84, 0]}  // RELATIVE to the parent
      }
    },
    {
      "ind": 2,
      "nm": "Eye",
      "parent": 14,
      "ty": 4,
      "ks": {
        "p": {"a": 0, "k": [64, -86, 0]}
      }
    }
  ]
}
```

`parent` refers to the target layer's `ind`, not its array index. A chain that
loops back on itself will hang or break the renderer, so keep it a tree.

### Practical rigs

1. **Shadow as parent** — move the shadow, the whole character travels
2. **Body as parent** — move the body, head and limbs follow
3. **Upper arm as parent** — rotate the shoulder, forearm and hand swing with it

### Benefits

- Move one layer and every child follows
- Far fewer keyframes for coordinated motion
- Complex scenes stay manageable

---

## 3. Stroke + Fill Combination (Outline Style)

The look that reads well at small sizes: a solid fill inside a defined contour.

### Concept

Each shape carries both a **fill** and a **stroke**.

```json
{
  "shapes": [
    {
      "ty": "gr",
      "it": [
        {"ty": "sh", "ks": {}},
        {"ty": "st",
          "c": {"a": 0, "k": [0.259, 0.153, 0.141, 1]},  // dark brown
          "o": {"a": 0, "k": 100},
          "w": {"a": 0, "k": 1},
          "lc": 2,
          "lj": 2
        },
        {"ty": "fl",
          "c": {"a": 0, "k": [0.302, 0.604, 0.816, 1]},  // blue
          "o": {"a": 0, "k": 100}
        },
        {"ty": "tr",
          "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
          "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0},
          "o": {"a": 0, "k": 100}
        }
      ]
    }
  ]
}
```

A stroke needs `c`, `o` and `w`; a fill needs `c` and `o`. Omit the opacity and
the player drops the whole layer without reporting anything.

Order matters: items listed later paint on top, so putting the stroke before the
fill keeps the fill from being swallowed by a thick contour.

### Stroke properties

| Property | Value | Meaning |
|---|---|---|
| `lc` (line cap) | 1 | Butt |
| `lc` | 2 | Round |
| `lc` | 3 | Square |
| `lj` (line join) | 1 | Miter |
| `lj` | 2 | Round |
| `lj` | 3 | Bevel |

### A coherent palette

Five or six colours is usually enough for a character. Keep one dark tone for
every outline so the silhouette stays consistent.

```json
{
  "body_fill": [0.302, 0.604, 0.816, 1],
  "outline":   [0.259, 0.153, 0.141, 1],
  "eye_white": [0.902, 0.976, 1.0, 1],
  "ear_inner": [0.941, 0.757, 0.686, 1],
  "shadow":    [0.608, 0.706, 0.878, 1]
}
```

---

## 4. Bezier Paths and Tangents

### Path structure

```json
{
  "ty": "sh",
  "ks": {
    "a": 0,
    "k": {
      "c": true,
      "v": [[0, 0], [100, 0], [100, 100], [0, 100]],
      "i": [[0, -10], [10, 0], [0, 10], [-10, 0]],
      "o": [[10, 0], [0, 10], [-10, 0], [0, -10]]
    }
  }
}
```

### Tangents

- `i` is the control point **entering** the vertex
- `o` is the control point **leaving** the vertex
- Both are **relative to their own vertex**, not absolute
- `[0, 0]` on both sides gives a straight corner

`v`, `i` and `o` must be the same length. On a closed path (`c: true`) the
start point is not repeated at the end; the tangents carry across the seam.

Deriving these by hand is where most SVG conversions go wrong. Use
`scripts/svg2lottie.py` instead — see [svg-to-lottie.md](svg-to-lottie.md).

---

## 5. Pre-compositions (Assets)

Group a complex animation into a reusable composition.

```json
{
  "assets": [
    {
      "id": "comp_0",
      "nm": "Cat Animation",
      "fr": 60,
      "layers": [/* the character's layers */]
    }
  ],
  "layers": [
    {
      "ty": 0,           // type 0 = precomp reference
      "refId": "comp_0", // must match an asset id
      "nm": "Cat",
      "ip": 0,
      "op": 36,
      "st": 0
    }
  ]
}
```

A `refId` with no matching asset renders as empty space, so check the id spelling
if a precomp layer disappears.

### Benefits

- Reuse one animation in several places
- Keep a large layer list organised
- Transform the whole group at once

---

## 6. Professional Timing

### Frame rate and duration

| Type | FPS | Frames | Duration | Use |
|---|---|---|---|---|
| Fast loop | 60 | 36 | 0.6s | Run cycles |
| Normal loop | 30 | 24 | 0.8s | Walk cycles |
| Slow loop | 30 | 60 | 2.0s | Idle animations |
| Transition | 60 | 45 | 0.75s | Entrances |

### A loop that closes

```
Frame 0:   state A
...
Frame N-1: state A' (all but identical to A)
Frame N:   [wraps back to frame 0]
```

**The key point**: the final frame (`op`) is not rendered — it only marks the
wrap point. If the first and last frames differ, the wrap will visibly jump.

---

## 7. Layer Order is Z-Depth

Position in the `layers` array decides what sits in front.

```json
{
  "layers": [
    {"ind": 1, "nm": "Foreground"},
    {"ind": 2, "nm": "Character"},
    {"ind": 3, "nm": "Background"}
  ]
}
```

**Note**: the first layer in the array paints on top — the opposite of SVG,
where later elements win. Converting between the two means reversing the order.

---

## Complete Example: Walk Cycle

```json
{
  "v": "5.12.1",
  "fr": 30,
  "ip": 0,
  "op": 24,
  "w": 200,
  "h": 200,
  "nm": "Character Walk",
  "ddd": 0,
  "assets": [],
  "layers": [
    // Shadow, the parent for every pose
    {
      "ind": 1,
      "ty": 4,
      "nm": "Shadow",
      "ks": {
        "o": {"a": 0, "k": 30},
        "p": {"a": 0, "k": [100, 180, 0]},
        "s": {"a": 1, "k": [
          {"t": 0, "s": [100, 100, 100]},
          {"t": 6, "s": [95, 100, 100]},
          {"t": 12, "s": [100, 100, 100]},
          {"t": 18, "s": [95, 100, 100]},
          {"t": 24, "s": [100, 100, 100]}
        ]}
      },
      "shapes": [
        {
          "ty": "gr",
          "it": [
            {"ty": "el", "s": {"a": 0, "k": [60, 12]}, "p": {"a": 0, "k": [0, 0]}},
            {"ty": "fl", "c": {"a": 0, "k": [0.2, 0.2, 0.2, 1]}, "o": {"a": 0, "k": 100}},
            {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
             "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
          ]
        }
      ],
      "ip": 0,
      "op": 24,
      "st": 0
    },
    // Pose 1 (frames 0-6)
    {
      "ind": 2,
      "ty": 4,
      "nm": "Pose 1",
      "parent": 1,
      "ip": 0,
      "op": 6,
      "st": 0,
      "shapes": [/* character pose 1 shapes */]
    },
    // Pose 2 (frames 6-12)
    {
      "ind": 3,
      "ty": 4,
      "nm": "Pose 2",
      "parent": 1,
      "ip": 6,
      "op": 12,
      "st": 0,
      "shapes": [/* character pose 2 shapes */]
    },
    // Pose 3 (frames 12-18)
    {
      "ind": 4,
      "ty": 4,
      "nm": "Pose 3",
      "parent": 1,
      "ip": 12,
      "op": 18,
      "st": 0,
      "shapes": [/* character pose 3 shapes */]
    },
    // Pose 4 (frames 18-24)
    {
      "ind": 5,
      "ty": 4,
      "nm": "Pose 4",
      "parent": 1,
      "ip": 18,
      "op": 24,
      "st": 0,
      "shapes": [/* character pose 4 shapes */]
    }
  ]
}
```

The shadow squashing on every second pose is what sells the weight of the steps.

---

## Checklist

- [ ] Pose count chosen for the frame-by-frame cycle
- [ ] Timing worked out: poses × frames per pose / fps = duration
- [ ] Parent/child hierarchy established, with no cycles
- [ ] Stroke and fill both present, each with its opacity
- [ ] Palette held to five or six colours, one shared outline tone
- [ ] Shadow reacts to the steps
- [ ] Loop closes: the first and last frames match
- [ ] Linted and rendered, and the filmstrip actually looked at
