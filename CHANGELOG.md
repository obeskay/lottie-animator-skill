# Changelog

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
- **`tests/`** — 72 stdlib-only unit tests. Path arithmetic is pinned against
  hand-computed coordinates; every lint rule is pinned by a test.
- **CI** — tests and lint on Python 3.8 and 3.12, plus a job that renders every example
  in a real player and uploads the filmstrips.
- `references/shape-modifiers.md`, which the skill linked in three places but never had.

### Fixed

- **`rocket-animated.json` rendered a blank canvas.** Easing handles sat on the
  position property instead of inside a keyframe, which aborts the whole render pass —
  not just that layer. Its polystars were also missing `os`, and its strokes and
  gradient fill were missing `o`.
- **`chimp-walk-pro.json` rendered a blank canvas.** All 32 strokes were missing `o`.
- **`morphing-star.json` crashed the player.** The hero layer had no `shapes` and no
  `ip`/`op`.
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
