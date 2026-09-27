# Changelog

## Unreleased

### Fixed

- **The linter never looked inside a precomp.** Only the root composition's layers were
  checked, so a keyframe without handles in a precomp, the `KF012` freeze, passed
  `--strict` while the file rendered blank; and a file whose only motion lived in
  precomps, as exported files often do, failed as a static image (`MQ001`). Layers in
  `assets[].layers` now get the same checks, except the composition range, which a
  precomp takes from the layers that use it. The suite is at 133 stdlib-only unit tests.
- **`render.mjs` sampled a file whose `ip` is not 0 that many frames late.** lottie-web's
  `goToAndStop` counts from the first frame and the renderer passed frames on the
  composition's clock, so the samples past the end came out as `EMPTY FRAME`: a valid
  file starting at frame 60 was reported empty on three of five frames. It now renders
  frame for frame like the same animation starting at 0.
- **The landing page loaded nothing where `docs/` was the site root on any host but
  `github.io`**, such as a server started inside `docs/`. It picked the examples' source
  by host name and asked for `../examples/`: 22 404s and an empty grid. It now reads the
  files beside it only when it is served from the repository, at `/docs/`.
- **A palette switch on the landing page could restart a one-shot mid-play.** The replay
  timer of the animation it replaced still fired, 1.4 s after that one had finished, and
  sent the new one back to frame 0. A timer now restarts only its own animation.

## 2.1.0 — 2026-09-26

### Recipes and palettes

The skill knew how to verify an animation and what good motion looks like, but every
request still started from a blank page and ended in one warm palette. Four examples
could not show the range, and one of them duplicated another.

- **Twenty-two examples, each a generator.** `examples/<name>.py` writes
  `examples/<name>.json`: success, error, like, notification, toggle, lock, play/pause,
  morph, spinner, typing, character loader, download, battery, equalizer, location,
  weather, paper plane, confetti, card stack, logo draw-on, rocket, bouncing ball. Each
  docstring states its brief (feeling, register, hero property), and each was rendered,
  read as a filmstrip and an onion skin, and revised before it shipped. The four
  originals are ported: the rocket now demonstrates `svg2lottie.convert()` from Python,
  the logo draw-on is a real logo reveal instead of a second check mark, and the panda's
  ring no longer overlaps its ears.
- **Nine palettes by role.** `motion.PALETTES`: `paper`, `night`, `dusk`, `harbor`,
  `citrus`, `berry`, `forest`, `mono`, `sky`, each with the same seven roles (ground,
  surface, ink, muted, accent, on-accent, support). Every generator takes
  `--palette NAME`, and the tests hold each palette to its contrast ratios.
- **Builders in `motion.py`.** `comp`, `layer` (parents by name, mattes), `null`,
  `group`, `ellipse`, `rect`, `star`, `path`, `svg`/`bezier` (SVG path data, centred on
  its own pivot), `fill`, `stroke` (dashes), `trim`, `repeater`, `round_corners`,
  `delay`, spatial tangents in `track`, and `main()` for the shared command line. Each
  emits the properties whose absence drops a layer, so generated files cannot hit
  `SH001`. The ground is stored as `meta.tc`.
- **Taste notes in the linter.** `KF013` when a scale starts near zero (the thing grows
  from a point) and `KF014` when easing handles overshoot: the two commonest tells of
  generated motion, reported once per file as notes, never as failures.
- **`scripts/recolor.py`.** Lists every colour in any Lottie with its uses and layers,
  and maps them — static and animated paint, gradient stops, text and solid layers.
- **SKILL.md starts from a recipe.** A table from request to the nearest example, the
  generator API, palettes, and recolouring; `skills/lottie-animator/examples` links the
  examples in beside `scripts`.
- **GIFs rebuilt in one browser.** `make-gifs.mjs` discovers every example, renders it
  on its own ground, starts entrances on their first painted frame and holds their
  final pose, and builds `hero.gif` (eight examples, eight grounds), `palettes.gif` (one
  example in all nine palettes) and the social card. The violet banner and the second
  preview page are gone; the landing page plays every example live and re-skins them.

### Fixed

- The suite was at 132 tests.
- **`render.mjs` called a spinning ring clipped.** `getBoundingClientRect()` boxes an
  element's local bounds after transforming them, so a circle at 45° measured 1.41
  times its width; the shipped panda was flagged on seven of twelve frames. The box is
  now measured along the drawn outline through the screen matrix.
- **`render.mjs` called a faded-out layer painted, and a straight line empty.** Layer
  and group opacity live on ancestors, which were ignored; and a horizontal stroke has a
  zero-height geometry box, which was skipped. Both now count as they look.
- **`render.mjs` never ran through the skill's symlink.** Made importable for
  `make-gifs.mjs`, it compares real paths before running `main()`.
- **The linter called constant motion mechanical.** A spinner turning whole
  revolutions, a trim or repeater offset and a marching dash are meant to be linear;
  `KF007` no longer counts them. Round Corners (`rd`) is a known modifier, not `SH002`.
- **`shape-modifiers.md` said a trim after the stroke does nothing.** Both orders render
  identically in lottie-web, and After Effects exports put it after the stroke; what
  fails is a modifier listed before its path. `lottie-structure.md` no longer teaches an
  overshoot preset that contradicts the house tokens, and `svg-to-lottie.md` points to
  the real converters instead of a stub.
- `.claude-plugin` metadata names the public handle, like the licence and the site.

### Taste

The tools proved an animation was not broken; nothing helped make it good, and the
shipped examples were the purple gradients and bouncy scale-from-zero entrances that
read as generated.

- **`references/motion-taste.md`**: the house style. Zero overshoot, nothing grows from
  a point, one hero property, rests as part of the motion; easing tokens, timing in
  frames, choreography, art direction, and an eight-question taste pass. Aligned with
  the Emil Kowalski / smooth-as-butter doctrine. Replaces `motion-personality.md` and
  `bezier-easing.md`, whose defaults (overshoot on everything, entrances from `[0, 0]`)
  contradicted it; bounce survives as an opt-in `playful` register.
- **`scripts/motion.py`**: those defaults as code — `track()` (handles on every
  keyframe but the last, so `KF012` cannot happen), six easing tokens, a warm palette,
  `rgba()`, and `squircle()`, a continuous-curvature corner Lottie has no primitive for.
- **`render.mjs --onion`**: sampled frames stacked oldest-faintest into `onion.png`.
  The spacing between ghosts is the easing and their path is the arc, which a filmstrip
  cannot show. The contact sheet chrome is neutral instead of violet.
- **Examples re-authored** with the tokens: warm palette on paper, cascade entrances,
  a squircle ↔ circle morph with holds, a draw-on that no longer shows a dot before the
  stroke starts. `references/examples.md` is regenerated the same way, each composition
  read as an onion skin first. GIFs rebuilt on paper.
- `disney-principles.md` marks squash, anticipation and exaggeration as playful-register
  tools; SKILL.md's easing table is the token table.
- Three tests pin `motion.py`; the suite was at 112 tests then.

### Fixed

- **A keyframe without easing handles froze the render, and the linter called it
  "linear".** lottie-web reads `o`/`i` unconditionally while interpolating; a keyframe
  without them throws inside the render pass, the pass aborts, and the canvas keeps the
  previous frame. No console error, no missing layer. Measured on lottie-web 5.12.2:
  position and rotation keyframes without handles rendered byte-identical frames at 0%,
  50% and 100%. It is now `KF012`, an error. `KF007` is kept for handles that are
  explicitly linear, which is a taste note.
- **`examples/panda-loader.json` shipped that defect** on the ring's trim path at frame 0.
  Handles added; the ring now eases both halves of the cycle, and the GIF is rebuilt.
- **Nine snippets in the references carried bare keyframes** — the spinner, the heart,
  the arm wave, the walk-cycle shadow, the loader ring, the offset path, the squash, the
  anticipation and the playful settle. A reader copying any of them would have produced
  a frozen canvas. `references/examples.md` is regenerated from eight compositions the
  suite lints, each rendered before being written down (the heart is real geometry from
  `svg2lottie.py`, the arm and the stagger are complete rather than `[...]`). The other
  fragments carry handles now, and `tests/test_docs.py` refuses a bare keyframe in any
  snippet, brace-wrapped fragments included.
- Easing curves that disagreed between references (Playful, Energetic) now match the
  table in SKILL.md.
- `lottie-gsap-integration.md` no longer recommends a `lazy` option lottie-web does not
  have, nor reaching into `renderer.elements[n].finalTransform`, which is private and
  breaks between minor versions. The parallax example drives the container instead.

### Added

- Five linter tests pinning `KF012`; the suite was at 109.
- SKILL.md: render once per background when the host has a dark mode. Art in the ink
  colour disappears on a background of the same value, and only a render shows it.

#### Earlier in this release

- **`examples/panda-loader.json` painted its own face and then covered it.** The head
  and body groups were authored back-to-front — `Face Base` sat above the pupils,
  eyebrows, blush, nose and mouth, and `Chest & Arms` sat above `White Belly`. Lottie
  paints the first item in a `shapes` array on top, so every feature rendered and was
  then hidden under an opaque ellipse. The file linted clean the whole time, and the
  defect had propagated into `assets/examples.png`. Shape order reversed in both
  groups; the panda now has the face it always contained.

### Added

- **`SH004`, an occlusion check in `lottie_lint.py`.** Reports a shape group that an
  opaque sibling painted above it covers completely — the defect below, which every
  structural check passed. Deliberately conservative: the coverer must be opaque,
  static and unrotated, and the covered geometry must fall inside the *inscribed*
  box of the covering shape rather than its bounding box, since an ellipse leaves
  its corners visible. Paths, repeaters, nested groups and anything animated are
  left alone. Brought the suite to 112 tests at the time.
- **`scripts/make-gifs.mjs`** — builds the README's animated GIFs from the examples
  using `render.mjs`, so the documentation shows motion rather than stills. Drops the
  leading empty frame an entrance starts on (a flash on every loop) and appends a hold
  so the settled state is legible before repeating. `npm run gifs`.

### Changed

- The Examples section now shows the four animations running, not a static contact
  sheet. `assets/examples.png` is gone — it was a still of a motion library, and its
  panda was the broken render.
- `panda-loader.gif` is rendered on a light card: the panda is a black-and-white
  character and its chest and ears vanish against the dark background the other three
  examples use.

## 2.0.0

The skill can now verify its own output instead of assuming it.

### Added

- **`scripts/svg2lottie.py`** — deterministic SVG to Lottie conversion. Full path
  grammar (`M L H V C S Q T A Z`, absolute and relative), plus rect, circle, ellipse,
  line, polygon, polyline, groups, nested transforms, strokes, and linear/radial
  gradients. Each element becomes its own layer anchored at its own centre.
- **`scripts/lottie_lint.py`** — replaces the 37-line smoke test. Adds per-shape
  required-property checks, misplaced easing handles, layers outside the composition
  range, permanently transparent layers, unpainted geometry, parent cycles, dead
  keyframes, loop closure, and asset reference resolution. Supports `--json`,
  `--strict`, `--loop/--no-loop`, and `--allow-static`.
- **`scripts/render.mjs`** — headless render via `lottie-web` and a local Chrome.
  Writes PNG frames and a labelled contact sheet, and reports empty frames, content off
  canvas, and content clipped by the edge.
- **`tests/`** — a stdlib-only unit suite, 93 tests at this release. Path arithmetic
  is pinned against hand-computed coordinates; every lint rule is pinned by a test.
- **CI** — tests and lint on Python 3.8 and 3.12, plus a job that renders every example
  in a real player and uploads the filmstrips.
- `references/shape-modifiers.md`, which the skill linked in three places but never had.
- `tests/test_docs.py`, which lints every complete composition embedded in the
  documentation so the prose cannot drift from the tooling, and enforces the
  test count stated in the README rather than leaving it to be maintained.
- `tests/test_cli.py`, pinning the exit-code contract the CI depends on: 0 for
  success, 1 for bad content, 2 for a bad invocation. A tool that prints an
  error and still exits 0 makes a green build meaningless.

### Fixed

- **`rocket-animated.json` rendered a blank canvas.** Easing handles sat on the
  position property instead of inside a keyframe, which aborts the whole render pass —
  not just that layer. Its polystars were also missing `os`, and its strokes and
  gradient fill were missing `o`.
- **`chimp-walk-pro.json` rendered a blank canvas.** All 32 strokes were missing `o`.
- **`morphing-star.json` crashed the player.** The hero layer had no `shapes` and no
  `ip`/`op`.
- **Five of the six complete examples in `references/examples.md` were broken.**
  Layers with no `ip`/`op`/`st`, a matte circle rendering at zero size because its
  geometry sat loose in `shapes` instead of inside a `gr` group, and a transform
  offset applied twice. A reader copying them got an empty canvas. All five now
  lint clean and render.
- Linter severity recalibrated against real playback. `tr` missing `a`/`p`/`s`/`r`
  and `gf` missing `t` were being reported as errors, but lottie-web supplies
  defaults and the files render; they are now warnings (`SH003`). Conversely a
  layer missing `st`, and a `tr` carrying `sk` without `sa`, do blank the layer
  and are now errors. Each entry in the error tier was verified by removing the
  property from a working animation and rendering the result.
- Broken links to `references/shape-modifiers.md`.
- `references/examples.md` was orphaned; it is now linked from the skill.
- The preview page fetched JSON over `file://`, which browsers block, so it could never
  load an animation. It now documents serving over HTTP and pins the player version
  instead of tracking `@latest`.
- `examples/lottie.min.js` was excluded by the `*.min.js` gitignore rule, so it was
  never actually in the repository.

### Changed

- Examples rebuilt and verified: `rocket-launch.json`, `logo-draw-on.json`,
  `shape-morph.json`, and the existing `panda-loader.json`. Each one is linted and
  rendered before it ships.
- `SKILL.md` restructured around the convert → lint → render → look → revise loop, with
  a trigger-rich description and a table mapping symptoms to their causes.
- The two duplicate preview pages are now one, `assets/preview.html`.
- `assets/readme-hero.png` regenerated from the real examples: 1.3 MB down to 105 KB.

### Removed

- `scripts/validate_lottie.py`, superseded by `lottie_lint.py`. It reported `OK` for
  every file listed above.

## 1.0.0

Initial release.
