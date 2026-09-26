# Contributing to Lottie Animator

First off, thank you for considering contributing to Lottie Animator! It's people like you that make this tool great for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (SVGs, expected output, actual output)
- **Include the Lottie JSON output** if relevant

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **Include examples** of how it would work

### Pull Requests

1. Fork the repo and create your branch from `main`
2. Make your changes
3. Run the checks below and make sure they pass
4. Submit a pull request

Every change must satisfy three gates, in this order:

```bash
python3 -m unittest discover -s tests   # unit tests
python3 scripts/lottie_lint.py examples/ --strict
npm install && node scripts/render.mjs examples/<your-file>.json --onion
```

The third one is not optional and not automatable away: **open the filmstrip and look
at it.** A Lottie can lint clean and still paint nothing. If you are adding a lint
rule, add a test that fails without it.

## Project Structure

```
lottie-animator-skill/
├── .claude-plugin/       # Plugin configuration
├── .github/workflows/    # CI: tests, lint, and a real render
├── assets/               # README GIFs, the palette board, the social card
├── docs/                 # Landing page with the live gallery (GitHub Pages)
├── examples/             # <name>.py generators, the <name>.json they write, SVG sources
├── scripts/
│   ├── motion.py         # Easing tokens, palettes, shape builders
│   ├── svg2lottie.py     # SVG -> Lottie shape layers
│   ├── svgpath.py        # Path grammar -> cubic beziers
│   ├── lottie_lint.py    # Structural and motion linting
│   ├── render.mjs        # Headless render, filmstrip, onion skin
│   ├── recolor.py        # List and map the colours of any Lottie
│   └── make-gifs.mjs     # README GIFs and boards, in the same player
├── skills/
│   └── lottie-animator/
│       ├── SKILL.md      # Main skill definition
│       ├── examples/     # -> ../../examples
│       ├── scripts/      # -> ../../scripts
│       └── references/   # Technical documentation
└── tests/                # Unit tests (stdlib only)
```

## Adding New Features

### New Animation Techniques

1. Document the technique in `references/professional-techniques.md`
2. Add an example to `examples/`
3. Update `SKILL.md` with usage instructions
4. Add to the examples reference

### New Easing Presets

1. Add to `references/motion-taste.md`
2. Include visual representation
3. Document use cases

### New Examples

An example is a generator, `examples/<name>.py`, plus the JSON it writes. The test
suite rebuilds every generator and fails if the committed JSON differs, lints it in
every palette, and refuses hex literals in the source, so an example cannot drift or
work in only one palette.

1. Start from the closest existing generator and keep its shape: a docstring whose
   first line is the caption and whose "Brief:" names the feeling, the register and
   the hero property; `build(c)` using palette roles; `main(build, __file__,
   palette=...)` at the end. Geometry comes from `svg()`/`bezier()` or `svg2lottie`,
   never hand-typed vertices.
2. `python3 examples/<name>.py`, then lint `--strict`, render, and look at the
   filmstrip and the onion skin on your palette and on `night`.
3. `node scripts/make-gifs.mjs <name>` and add it to the README gallery and to
   `references/examples.md`.

## Style Guidelines

### Lottie JSON

- Write it with `scripts/motion.py`; hand-edit only to repair a file from elsewhere
- Include meaningful `nm` (name) properties on layers and shape groups
- Easing handles belong inside a keyframe, never on the property holding it
- Give every layer explicit `ip` and `op`
- Include every required property for a shape type; a missing one drops the layer

### Documentation

- Use clear, concise language
- Include code examples
- Add visual representations where helpful
- Keep tables formatted consistently

## Testing

The Python tools have no dependencies; rendering needs Node and a local Chrome
(`npm install`, then set `CHROME_PATH` if it is not in a standard location).

```bash
python3 -m unittest discover -s tests -v
python3 scripts/lottie_lint.py examples/ --strict
node scripts/render.mjs examples/panda-loader.json
```

For a browser preview, serve the repository over HTTP — `file://` cannot fetch the
JSON:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/docs/`, the landing page, which plays every example
live and re-skins them in any palette. Or drop a file on
[LottieFiles Preview](https://lottiefiles.com/preview).

## Questions?

Feel free to open an issue for any questions about contributing!

---

Thank you for helping make Lottie Animator better!
