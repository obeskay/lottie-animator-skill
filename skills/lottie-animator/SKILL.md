---
name: lottie-animator
description: >-
  Create, inspect, recolor, and repair Lottie animations, including converting SVG art
  into animated Lottie JSON. Use when asked to animate a logo, icon, or SVG; build motion
  graphics, micro-interactions, loaders, spinners, success/error states, toggles, or
  entrance animations; produce or edit a .json/.lottie animation file; re-skin one in a
  brand palette or dark mode; add wiggle, bounce, pulse, fade, scale, rotate, morph, or
  trim-path draw-on effects; build walk cycles or character rigs; or debug a Lottie that
  renders blank, jumps at the loop, or looks wrong in a player.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Lottie Animator

Lottie is JSON, which makes it easy to write and easy to write wrongly. The failure
mode is specific and nasty: **a broken Lottie still parses.** A missing `os` on a
polystar, an easing handle one level too high, a layer without `ip`/`op` — the file
loads, the player reports no error, and the canvas stays empty. And a correct file can
still be ugly: linear, bouncy, crowded, purple.

So do not judge an animation by whether the JSON is valid. Judge it by looking at it.

Paths below are relative to this skill's directory; from another project, call them by
absolute path. The renderer needs `npm install` once, in the repository that holds
`package.json`.

## Fast path: start from a recipe

`examples/` holds twenty-two generators, each a short Python file that writes one
finished, linted, rendered animation. Starting from the nearest one beats a blank page:
the timing, the easing and the structure are already right, and only the geometry and
the beats need to change.

| Asked for | Start from | What it teaches |
|---|---|---|
| Success, done, saved | `success-check` | trim draw-on over a settling disc, one quiet ripple |
| Error, invalid, denied | `error-shake` | a decaying shake as the hero |
| Like, favourite, react | `heart-like` | press → pop → burst; the playful register, labelled |
| Notification, alert | `notification-bell` | swing about a top pivot, clapper follow-through |
| Toggle, switch, setting | `toggle-switch` | travel plus a colour track, on a dark ground |
| Lock, privacy, access | `lock-unlock` | a shackle opening about its leg, state colour |
| Play, pause, icon to icon | `play-pause`, `shape-morph` | path morphs with matched vertex counts |
| Loading, waiting | `spinner-arc`, `typing-dots`, `panda-loader` | trim chase; a staggered wave; a character loop |
| Progress, download, charging | `download-progress`, `battery-charge` | phases that overlap; stepped fill |
| Audio, live, recording | `equalizer` | phase-offset bars anchored at the base |
| Location, presence | `location-ping` | staggered rings in perspective |
| Weather, ambient | `weather-sun` | repeater rays turning by exactly one spacing |
| Send, share, travel | `paper-plane` | spatial tangents: motion on an arc, banking |
| Celebration, reward | `confetti-burst` | ballistic arcs, three colours at most |
| Cards, onboarding, lists | `card-stack` | glide cascade; the hero lands last |
| Logo reveal | `logo-draw-on`, `rocket-launch` | SVG → Lottie, strokes drawn in reading order |
| Bounce, physics | `bouncing-ball` | squash and stretch with volume kept |

```bash
cp examples/spinner-arc.py build/loader.py
# edit build/loader.py: point its sys.path line at this skill's scripts/ directory,
# then change the geometry and beats to the brief — keep the tokens
python3 build/loader.py --palette night -o build/loader.json
```

Each generator's docstring states its brief — feeling, register, hero property. Read it
before editing so the change keeps the idea that made it work. The same file renders in
any palette, so "make it match dark mode" is `--palette night`, not a rewrite.

## The loop

```
build  →  lint  →  render  →  LOOK  →  revise
```

Never skip the render. "The JSON is valid" is not a claim about what the user sees.

```bash
python3 scripts/lottie_lint.py build/loader.json --strict
node scripts/render.mjs build/loader.json
# Read the filmstrip PNG it prints and actually look at it
node scripts/render.mjs build/loader.json --onion
# the taste pass: Read onion.png and judge the motion, not just the pixels
```

`render.mjs` writes `filmstrip.png`: labelled frames across the timeline, each with a
shape count and canvas coverage, on the ground the file was designed for (`meta.tc`;
`--bg` overrides it). It reports `EMPTY FRAME` when nothing paints (a layer faded to 0
counts as nothing), `off canvas` when the art has left the frame, and `clipped` when it
runs past an edge. That proves the animation is not broken. Whether it is good is a
second look: `--onion` writes `onion.png`, sampled frames stacked oldest-faintest, where
the spacing between ghosts is the easing and their path is the arc. Judge it against the
taste pass in [references/motion-taste.md](references/motion-taste.md).

If the tools are unavailable (another repository, no Node), say so and fall back to
`python3 -c "import json; json.load(open('a.json'))"` — but tell the user the result
is unverified rather than implying it was checked.

## Writing a generator

`scripts/motion.py` turns the house style into code, so a generator never types a
handle, a hex value, or a required property:

```python
import sys; sys.path.insert(0, "<skill>/scripts")
from motion import *

def build(c):                                   # c is a palette, by role
    disc = layer("Disc", group("Disc", ellipse(128), fill(c["accent"])),
                 p=(120, 120),
                 s=track((0, [92, 92], "out"), (22, [100, 100])),
                 o=track((0, 0, "out"), (10, 100)))
    return comp("Disc", 240, 240, [disc], op=90, bg=c["bg"])

if __name__ == "__main__":
    main(build, __file__, palette="paper")      # --palette NAME, -o PATH
```

- `track((t, value, ease), ...)` puts handles on every keyframe but the last, so the
  frozen-canvas defect cannot happen; `delay(track, n)` offsets it for a cascade; a 4th
  element (`{"to": ..., "ti": ...}`) makes position travel on an arc.
- Shapes: `ellipse`, `rect`, `star`, `path(squircle(w, h, r))`, and `svg(d, scale,
  center)` for any SVG path data — draw on a convenient grid and let `center` move the
  pivot to the shape's middle. Paint: `fill`, `stroke(dash=...)`. Modifiers: `trim`,
  `repeater`, `round_corners`. Structure: `group` (geometry, paint, then its transform),
  `layer` (`parent="Name"`, `td`/`tt` for mattes), `null`, `comp`.
- In a `shapes` list, and in the layer list, **the first item paints on top.**

## Palettes

Nine palettes share seven roles — `bg` (the ground, stored as `meta.tc`), `surface`,
`ink`, `muted`, `accent`, `on_accent`, `support` — and tests hold each to its contrast
ratios: `paper`, `night`, `dusk`, `harbor`, `citrus`, `berry`, `forest`, `mono`, `sky`.
Write against roles and every palette works; one accent per composition; `support` is
for masses, never a thin line on the ground.

- **A brand:** add a dict with the same seven roles to `PALETTES` and check the ratios.
- **An existing file** (from LottieFiles, a designer, anywhere):
  `python3 scripts/recolor.py in.json --list` prints every colour with its uses and
  layers; then `--map "#FF5A5F=#C8522B" -o out.json` for each role. It covers static and
  animated paint, gradient stops, and solid layers.
- **Dark mode:** render on every ground the host uses. Ink drawn on a ground of the
  same value is not low contrast, it is invisible, and only the render shows it.

## Start from real geometry

Do not hand-write bezier vertices. `svg2lottie.py` converts SVG paths, rects,
circles, ellipses, lines, polygons, polylines, groups, transforms, strokes, and
linear/radial gradients into Lottie shape layers. Each element becomes its own named
layer anchored at its own centre, so scale and rotation pivot correctly.

```bash
python3 scripts/svg2lottie.py icon.svg -o icon.json --size 512 --current-color "#1E1B18"
```

Icon sets paint with `currentColor`; pass `--current-color` or the art comes out
black. `<text>`, `<use>`, `clipPath`, and `mask` are reported as warnings — flatten
them in the source SVG first. The output is deliberately static; you add the motion,
from Python with `convert()` (see `examples/rocket-launch.py`) or by hand.

## Before keyframing, decide the motion

Answer these before touching a keyframe. It takes thirty seconds and prevents most
revision cycles:

1. **Feeling** — what should the viewer feel? (trust, delight, urgency, calm)
2. **Register** — quiet and precise unless the brief says otherwise: zero overshoot,
   nothing grows from a point. Playful, with bounce, only when asked.
3. **Hero property** — one of position, scale, rotation, opacity, shape. One. The rest
   support it at under a third of the amplitude.
4. **Timing** — feedback 6–10 frames at 60 fps, entrances 18–30, stagger 3, and a hold
   of at least 12 before a loop repeats.
5. **Easing** — `out` for arrivals, `in-out` for travel and loops, `in` only for exits.
6. **Palette** — by role, one accent. No purple gradients, no neon on black.

Motion that competes with the subject is noise. Cut it. The full doctrine, the tokens
and the taste pass are in [references/motion-taste.md](references/motion-taste.md).

More technique, by topic:
[shape-modifiers.md](references/shape-modifiers.md) (trim, repeater, offset, merge) ·
[professional-techniques.md](references/professional-techniques.md) (parenting, rigs,
walk cycles, precomps) ·
[disney-principles.md](references/disney-principles.md) ·
[lottie-gsap-integration.md](references/lottie-gsap-integration.md) (scroll scrubbing) ·
[lottie-structure.md](references/lottie-structure.md) ·
[svg-to-lottie.md](references/svg-to-lottie.md) ·
[examples.md](references/examples.md) ·
[lottie-tools-ecosystem.md](references/lottie-tools-ecosystem.md) (dotLottie, players)

## Easing

Handles belong **inside a keyframe**, never on the property that holds them. `x` must
stay within 0–1; `y` may exceed it, which is how overshoot is made — and why the house
default keeps `y` within 0–1.
Handles on keyframe *n* shape the segment from *n* to *n+1* — putting them on the
wrong keyframe eases the wrong half of the move.

Every keyframe except the last carries both handles, even when the motion is
linear. A keyframe without them is not "linear" in lottie-web: the player throws
while interpolating, the render pass aborts, and the canvas freezes on the previous
frame with nothing in the console. Hold keyframes (`h: 1`) are the one exception.

| Token (`motion.py`) | Use | cubic-bezier |
|---|---|---|
| `out` | arrivals, feedback | `0.23, 1, 0.32, 1` |
| `in-out` | travel and morphs, rest to rest | `0.77, 0, 0.175, 1` |
| `glide` | large surfaces | `0.32, 0.72, 0, 1` |
| `in` | exits only | `0.55, 0, 1, 0.45` |
| `linear` | constant rotation, marching offsets | `0.333, 0.333, 0.667, 0.667` |
| `swing` | pendulums, oscillation, breathing | `0.37, 0, 0.63, 1` |
| `standard` | a spinner's chase, a level meter | `0.4, 0, 0.2, 1` |
| `strike` | the first swing after a blow | `0.61, 1, 0.88, 1` |
| `fall` / `rise` | gravity, exactly t², and its mirror | `0.333, 0, 0.667, 0.333` / `0.333, 0.667, 0.667, 1` |
| `playful` | overshoot, on request only | `0.34, 1.56, 0.64, 1` |

As handles, `cubic-bezier(x1, y1, x2, y2)` is `"o": {"x": [x1], "y": [y1]}` and
`"i": {"x": [x2], "y": [y2]}` on the keyframe the move leaves. Motion that never rests
wants `linear`, `swing` or `standard`: `in-out` on an oscillation holds at every turn and
lurches between.

## The defects that render blank

Every one of these shipped in this repository at some point and passed a JSON-parse
check. The linter now catches all of them; the tests pin them.

| Symptom | Cause |
|---|---|
| Whole file blank, no console error | Easing handles on the property instead of inside a keyframe (`KF011`) |
| One layer missing | Layer has no `ip`, `op`, or `st`, so the playhead never matches it (`LY005`) |
| One layer missing | A shape item lacks a required property, so the player drops the layer (`SH001`) |
| Geometry present, nothing visible | No fill or stroke on the group (`LY015`), or opacity 0 throughout (`LY016`) |
| Part of the art never shows | A group painted under an opaque sibling listed above it (`SH004`) |
| Shape draws at zero size | Geometry left loose in `shapes` instead of inside a `gr` group |
| Art lands in the wrong place | The same offset applied on both the layer transform and the group transform |
| Visible jump each cycle | First and last keyframe values differ (`KF010`) |
| Canvas frozen on one frame, no error | A keyframe other than the last has no `o`/`i` handles; lottie-web throws mid-render and the pass aborts (`KF012`) |
| Motion feels mechanical | Linear handles on motion that starts and stops (`KF007`, a note; constant spins and marching offsets are exempt) |

Every layer needs `ip`, `op`, and `st`. Miss any one and the layer is hidden at
every frame.

Properties whose absence makes a player drop the layer — each verified by removing
it from a working file and rendering the result:

fill `c,o` · stroke `c,o,w` · gradient fill `s,e,g,o` · polystar `p,r,pt,or,os`
plus `ir,is` when `sy` is 1 · ellipse `p,s` · rect `p,s,r` · trim `s,e,o` ·
transform `o`, plus `sa` whenever `sk` is present.

The spec also lists `a,p,s,r` on a transform and `t` on a gradient. lottie-web
supplies defaults for those, so the linter reports them as warnings (`SH003`)
rather than errors — but other players are not guaranteed to be as forgiving.

## Finishing

Before saying it is done:

- `lottie_lint.py` reports no errors (use `--strict` to fail on warnings too). Its two
  taste notes — `KF013` something grows from a point, `KF014` easing overshoots — are
  the commonest tells of generated motion; fix them unless the brief asked for playful.
- `render.mjs` shows the intended motion at the start, middle, and end.
- For a loop, the first and last frames match — check the filmstrip, not the numbers.
- The taste pass in [motion-taste.md](references/motion-taste.md) was run on
  `onion.png`: spacing eases, long travel arcs, nothing grows from a point, one hero,
  a readable hold, one accent colour.
- Nothing is clipped or off canvas unless that was the intent.
- If the host has a dark mode, render once per ground (`--palette` for a generator,
  `--bg` for a finished file).

Report what you verified and what you did not. If you could not render it, say that
plainly instead of implying the motion was checked.
