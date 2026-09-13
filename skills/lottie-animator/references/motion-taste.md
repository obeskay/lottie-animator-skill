# Motion taste

The linter proves an animation renders. This page is about whether it is worth
watching. The defaults below are a house style: quiet, precise, warm — the register of
Linear, Raycast and Apple rather than a cartoon. Depart from them when the brief asks
for it, and say so.

Tokens for everything here live in `scripts/motion.py`, so a generator never types a
handle or a hex value:

```python
import sys; sys.path.insert(0, "<skill>/scripts")
from motion import track, static, rgba, squircle, PALETTE

"o": track((0, 0, "out"), (14, 100)),
"s": track((0, [94, 94, 100], "out"), (26, [100, 100, 100])),
```

`track` puts `o`/`i` handles on every keyframe but the last, so the frozen-canvas
defect (`KF012`) cannot happen.

## Defaults

1. **Zero overshoot.** Nothing travels past where it lands. Weight comes from strong
   deceleration, not from bouncing. Overshoot is quarantined to the `playful` token and
   used only when the brief says playful, bouncy or cartoon.
2. **Nothing appears from nothing.** Enter from 92–96% scale with opacity, never from
   `[0, 0]`. A small offset (2–4% of the composition) reads as arrival; a large one
   reads as travel and needs its own easing.
3. **One hero property.** Pick position, scale, rotation, opacity or shape. Anything
   else that moves supports it at under a third of the amplitude and a few frames late.
4. **Rest is part of the motion.** Hold the settled state. A loop needs a pause at each
   end of its cycle; an entrance needs its final pose on screen long enough to read.
5. **Stillness beats decoration.** If a part does not need to move, it does not move.

## Easing tokens

| Token | cubic-bezier | Use for |
|---|---|---|
| `out` | `0.23, 1, 0.32, 1` | Anything arriving: entrances, feedback, draw-ons that should feel instant |
| `in-out` | `0.77, 0, 0.175, 1` | Travel on screen, morphs, loops, a stroke drawn like handwriting |
| `glide` | `0.32, 0.72, 0, 1` | Large surfaces: sheets, cards, hero plates |
| `in` | `0.55, 0, 1, 0.45` | Exits only, at about 70% of the entrance duration |
| `linear` | `0.333, 0.333, 0.667, 0.667` | Constant rotation, progress, a marquee — nothing that starts or stops |
| `playful` | `0.34, 1.56, 0.64, 1` | Overshoot. Only on request, once per composition, ≤ 8% |

The ease on a keyframe shapes the move leaving it. An entrance puts `out` on its first
keyframe; a return trip puts `in-out` on the keyframe where it turns around.

As Lottie handles, `out` is `"o": {"x": [0.23], "y": [1]}, "i": {"x": [0.32], "y": [1]}`.

## Timing, in frames at 60 fps

| Motion | Frames | ms |
|---|---|---|
| Press or toggle feedback | 6–10 | 100–170 |
| Icon change, small entrance | 12–18 | 200–300 |
| Card or logo entrance | 18–30 | 300–500 |
| Hero reveal | 30–42 | 500–700 |
| Stagger between siblings | 3 | 50 |
| Hold before a loop repeats | ≥ 12 | ≥ 200 |
| Ambient loop cycle | 90–180 | 1.5–3 s |

Opacity finishes before scale: fade over about half the duration of the move it
accompanies, so the shape is solid while it settles. At 30 fps halve every frame count.

## Choreography

- **Cascade, do not flash.** Siblings arrive 3 frames apart, in reading order or
  outward from the hero. Everything at once reads as a render, not a reveal.
- **Overlap instead of bounce.** Follow-through comes from parts settling at different
  times, not from any one part wobbling.
- **Background before hero.** The stage settles first; the hero lands 6–12 frames later.
- **Arcs for long travel.** Movement over more than a quarter of the canvas follows a
  curve (`to`/`ti` spatial tangents); short offsets can stay straight.
- **Exits are quieter than entrances.** Shorter, `in`-eased, smaller offset.

## Art direction

- **Palette.** `motion.PALETTE` is warm and low-chroma: paper `#F3EEE6`, sand
  `#E4D9C6`, ink `#1E1B18`, stone `#8A8178`, clay `#C8522B`, sage `#6F8163`, night
  `#171513`. One accent per composition. Bring a brand palette when there is one;
  keep the discipline.
- **No slop.** No purple or indigo gradients, no neon on black, no glows, no rainbow
  confetti. Flat fills first; a gradient only when it stays within one hue and about
  10% lightness.
- **Ink is contour.** Dark ink sits inside a mass of colour or on a light ground.
  Against a dark background of the same value it is invisible, so render on every
  background the host uses.
- **One stroke weight** per composition, round caps and joins. On an icon grid that
  is about a twelfth of the icon's size.
- **Squircle surfaces.** `squircle(w, h, r)` gives a continuous-curvature corner. A
  circular corner (`rc` with `r`) pinches where the edge meets the arc; use it only when
  the brand asks for it.

## The taste pass

After the render proves nothing is broken, render for judgement on the real background:

```bash
node scripts/render.mjs a.json --bg "#F3EEE6" --onion --width 480
```

`onion.png` stacks twelve sampled frames, oldest faintest. Read it with the filmstrip
and answer each question honestly:

1. **Spacing.** Do the ghosts bunch up at the end of each move? Even spacing is linear
   motion; bunching at the start is an ease-in on an arrival.
2. **Arcs.** Does long travel curve? A ruler-straight diagonal looks mechanical.
3. **Origin.** Does anything grow from a point or pop from nothing?
4. **Hierarchy.** Is there one hero, and does it land last?
5. **Restraint.** Is anything moving that would be better still?
6. **Rest.** Is there a readable hold at the end, and at both ends of a loop?
7. **Colour.** One accent, no slop, legible on every background it will sit on?
8. **Final frame.** Alone, as a still, is it a good image?

Fix the first failing answer and render again. Report which questions you checked.

## Register, when the brief asks for one

| Register | Easing | Entrance | Overshoot | Squash |
|---|---|---|---|---|
| Quiet / premium (default) | `out`, `glide` | 24–36 f, scale from 96% | none | never |
| Product / functional | `out` | 12–18 f, scale from 94% | none | never |
| Editorial / expressive | `in-out`, `out` | 30–42 f, offsets and arcs | none | never |
| Playful (on request) | `playful` once, `out` elsewhere | 18–24 f | ≤ 8% | volume-preserving, on impact only |

The craft principles that apply in every register — staging, arcs, secondary action,
follow-through — are in [disney-principles.md](disney-principles.md).
