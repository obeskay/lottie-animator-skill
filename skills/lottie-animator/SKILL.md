---
name: lottie-animator
description: >-
  Create, inspect, and repair Lottie animations, including converting SVG art into
  animated Lottie JSON. Use when asked to animate a logo, icon, or SVG; build motion
  graphics, micro-interactions, loaders, spinners, or entrance animations; produce or
  edit a .json/.lottie animation file; add wiggle, bounce, pulse, fade, scale, rotate,
  morph, or trim-path draw-on effects; build walk cycles or character rigs; or debug a
  Lottie that renders blank, jumps at the loop, or looks wrong in a player.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Lottie Animator

Lottie is JSON, which makes it easy to write and easy to write wrongly. The failure
mode is specific and nasty: **a broken Lottie still parses.** A missing `os` on a
polystar, an easing handle one level too high, a layer without `ip`/`op` — the file
loads, the player reports no error, and the canvas stays empty.

So do not judge an animation by whether the JSON is valid. Judge it by looking at it.

## The loop

```
convert  →  lint  →  render  →  LOOK  →  revise
```

Never skip the render. "The JSON is valid" is not a claim about what the user sees.

```bash
python3 scripts/svg2lottie.py logo.svg -o build/logo.json --size 512
python3 scripts/lottie_lint.py build/logo.json --allow-static
node scripts/render.mjs build/logo.json
# then Read the filmstrip PNG it prints and actually look at it
```

`render.mjs` writes `filmstrip.png`: labelled frames across the timeline, each with a
shape count and canvas coverage. Read that image. It reports `EMPTY FRAME` when
nothing paints, `off canvas` when the art has left the frame, and `clipped` when it
runs past an edge.

If the tools are unavailable (another repository, no Node), say so and fall back to
`python3 -c "import json; json.load(open('a.json'))"` — but tell the user the result
is unverified rather than implying it was checked.

## Start from real geometry

Do not hand-write bezier vertices. `svg2lottie.py` converts SVG paths, rects,
circles, ellipses, lines, polygons, polylines, groups, transforms, strokes, and
linear/radial gradients into Lottie shape layers. Each element becomes its own named
layer anchored at its own centre, so scale and rotation pivot correctly.

```bash
python3 scripts/svg2lottie.py icon.svg -o icon.json --size 512 --current-color "#a855f7"
```

Icon sets paint with `currentColor`; pass `--current-color` or the art comes out
black. `<text>`, `<use>`, `clipPath`, and `mask` are reported as warnings — flatten
them in the source SVG first. The output is deliberately static; you add the motion.

When there is no SVG, write the JSON directly — but lint and render it the same way.

## Before keyframing, decide the motion

Answer these before touching a keyframe. It takes thirty seconds and prevents most
revision cycles:

1. **Feeling** — what should the viewer feel? (trust, delight, urgency, calm)
2. **Personality** — pick exactly one: Playful, Premium, Corporate, or Energetic.
   See [references/motion-personality.md](references/motion-personality.md).
3. **Hero property** — one of position, scale, rotation, opacity. One. The rest support it.
4. **Timing** — functional feedback under 150 ms; expressive motion 300–600 ms.
5. **Easing** — entrance eases out, exit eases in, loop eases in-out.
6. **Staging** — the hero enters 100–200 ms after its background.

Motion that competes with the subject is noise. Cut it.

## Technique by intent

| Intent | Technique | Reference |
|---|---|---|
| Stroke icon draws itself | Trim path (`tm`) | [shape-modifiers.md](references/shape-modifiers.md) |
| Logo or button appears | Scale + opacity, overshoot | [disney-principles.md](references/disney-principles.md) |
| Icon becomes another icon | Path keyframes, equal vertex counts | [professional-techniques.md](references/professional-techniques.md) |
| Several elements arrive | Staggered `ip` and keyframe offsets | [disney-principles.md](references/disney-principles.md) |
| Spinner or loader | Rotation 0→360, or trim path offset | [shape-modifiers.md](references/shape-modifiers.md) |
| Character or mascot | Parenting and bone hierarchy | [professional-techniques.md](references/professional-techniques.md) |
| Walk or run cycle | Per-pose layers switched via `ip`/`op` | [professional-techniques.md](references/professional-techniques.md) |
| Radial or repeated pattern | Repeater (`rp`) | [shape-modifiers.md](references/shape-modifiers.md) |
| Scroll-driven playback | Scrub via GSAP ScrollTrigger | [lottie-gsap-integration.md](references/lottie-gsap-integration.md) |

Structure, property names, and worked JSON:
[lottie-structure.md](references/lottie-structure.md) ·
[svg-to-lottie.md](references/svg-to-lottie.md) ·
[bezier-easing.md](references/bezier-easing.md) ·
[examples.md](references/examples.md) ·
[lottie-tools-ecosystem.md](references/lottie-tools-ecosystem.md)

## Easing

Handles belong **inside a keyframe**, never on the property that holds them. `x` must
stay within 0–1; `y` may overshoot, and that overshoot is exactly what makes a bounce.
Handles on keyframe *n* shape the segment from *n* to *n+1* — putting them on the
wrong keyframe eases the wrong half of the move.

| Use | out (`o`) | in (`i`) |
|---|---|---|
| Entrance (ease out) | `{"x":[0.33],"y":[0]}` | `{"x":[0.67],"y":[1]}` |
| Exit (ease in) | `{"x":[0.55],"y":[0.055]}` | `{"x":[0.675],"y":[0.19]}` |
| Loop (ease in-out) | `{"x":[0.645],"y":[0.045]}` | `{"x":[0.355],"y":[1]}` |
| Bounce | `{"x":[0.34],"y":[1.56]}` | `{"x":[0.64],"y":[1]}` |

## The defects that render blank

Every one of these shipped in this repository at some point and passed a JSON-parse
check. The linter now catches all of them; the tests pin them.

| Symptom | Cause |
|---|---|
| Whole file blank, no console error | Easing handles on the property instead of inside a keyframe (`KF011`) |
| One layer missing | Layer has no `ip`/`op`, so the playhead never matches it (`LY005`) |
| One layer missing | A shape item lacks a required property, so the player drops the layer (`SH001`) |
| Geometry present, nothing visible | No fill or stroke on the group (`LY015`), or opacity 0 throughout (`LY016`) |
| Visible jump each cycle | First and last keyframe values differ (`KF010`) |
| Motion feels mechanical | No easing handles; everything interpolates linearly (`KF007`) |

Required properties by shape type: fill `c,o` · stroke `c,o,w` · gradient fill
`s,e,g,t,o` · polystar `p,r,pt,or,os` plus `ir,is` when `sy` is 1 · ellipse `p,s` ·
rect `p,s,r` · trim `s,e,o` · transform `a,p,s,r,o`.

## Finishing

Before saying it is done:

- `lottie_lint.py` reports no errors (use `--strict` to fail on warnings too).
- `render.mjs` shows the intended motion at the start, middle, and end.
- For a loop, the first and last frames match — check the filmstrip, not the numbers.
- Nothing is clipped or off canvas unless that was the intent.

Report what you verified and what you did not. If you could not render it, say that
plainly instead of implying the motion was checked.
